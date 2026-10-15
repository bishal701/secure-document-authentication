"""
Leakage-Safe AI Classifier Training Script (Gap 10).
Trains PyTorch QRArtifactCNN, BaselineRFClassifier, and MajorityClassBaseline on the synthetic QR dataset.
Splits are strictly grouped by unique payload ID to prevent data leakage.
Applies balanced class weighting to handle the 9:1 imbalance between genuine and manipulated samples.
Saves model weights, configuration, training history, per-sample predictions, and confusion matrices.
"""

import os
import sys
import json
import time
import cv2
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.ml_classifier.model import QRArtifactCNN, HandcraftedFeatureExtractor, BaselineRFClassifier
from backend.qr_watermark.benchmark_evaluator import BenchmarkEvaluator

MODELS_DIR = BASE_DIR / "models"
RESULTS_GAP10_DIR = BASE_DIR / "results" / "gap10"
MANIFEST_PATH = BASE_DIR / "data" / "synthetic" / "manifest.csv"

class QRDataset(Dataset):
    """PyTorch Dataset loading images dynamically from manifest records."""
    def __init__(self, df: pd.DataFrame, base_dir: Path, target_size: Tuple[int, int] = (128, 128)):
        self.df = df.reset_index(drop=True)
        self.base_dir = base_dir
        self.target_size = target_size

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_rel = row["image_path"]
        img_path = self.base_dir / img_rel
        img_bgr = cv2.imread(str(img_path))
        if img_bgr is None:
            raise FileNotFoundError(f"Image not found: {img_path}")
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, self.target_size)
        # Normalize to [0, 1]
        tensor = torch.tensor(gray, dtype=torch.float32).unsqueeze(0) / 255.0
        label = torch.tensor(int(row["ground_truth_label"]), dtype=torch.long)
        return tensor, label, row["sample_id"]

def train_and_evaluate_classifiers(force_retrain: bool = True):
    print("=" * 60)
    print("AI CLASSIFIER TRAINING AND EVALUATION (GAP 10)")
    print("=" * 60)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_GAP10_DIR.mkdir(parents=True, exist_ok=True)

    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Manifest not found: {MANIFEST_PATH}. Run scripts/generate_synthetic_benchmark_dataset.py first.")

    df = pd.read_csv(MANIFEST_PATH)
    print(f"Total Manifest Samples: {len(df)}")

    # 1. Leakage-Safe Splitting by Unique Payload ID
    df_train = df[df["split"] == "train"].copy()
    df_val = df[df["split"] == "val"].copy()
    df_test = df[df["split"] == "test"].copy()

    # Leakage check: Verify zero intersection of payload_id between splits
    train_pids = set(df_train["payload_id"].unique())
    val_pids = set(df_val["payload_id"].unique())
    test_pids = set(df_test["payload_id"].unique())

    assert len(train_pids.intersection(test_pids)) == 0, "DATA LEAKAGE DETECTED: Overlap between Train and Test!"
    assert len(train_pids.intersection(val_pids)) == 0, "DATA LEAKAGE DETECTED: Overlap between Train and Val!"
    assert len(val_pids.intersection(test_pids)) == 0, "DATA LEAKAGE DETECTED: Overlap between Val and Test!"

    print(f"Leakage Check PASSED! Zero overlap across splits.")
    print(f"Train: {len(df_train)} samples ({len(train_pids)} payloads)")
    print(f"Val:   {len(df_val)} samples ({len(val_pids)} payloads)")
    print(f"Test:  {len(df_test)} samples ({len(test_pids)} payloads)")

    # 2. PyTorch DataLoaders
    train_dataset = QRDataset(df_train, BASE_DIR)
    val_dataset = QRDataset(df_val, BASE_DIR)
    test_dataset = QRDataset(df_test, BASE_DIR)

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

    # 3. Train QRArtifactCNN with Balanced Class Weights
    device = torch.device("cpu")
    model = QRArtifactCNN(in_channels=1, num_classes=2).to(device)

    # Compute balanced class weights on training split (Class 0: Genuine, Class 1: Manipulated)
    n_train_total = len(df_train)
    n_train_gen = int(np.sum(df_train["ground_truth_label"] == 0))
    n_train_man = int(np.sum(df_train["ground_truth_label"] == 1))
    weight_gen = float(n_train_total / (2.0 * max(1, n_train_gen)))
    weight_man = float(n_train_total / (2.0 * max(1, n_train_man)))
    class_weights = torch.tensor([weight_gen, weight_man], dtype=torch.float32).to(device)
    print(f"Training Class Distribution -> Genuine (0): {n_train_gen}, Manipulated (1): {n_train_man}")
    print(f"Applied Loss Weights: w(0)={weight_gen:.3f}, w(1)={weight_man:.3f}")

    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)

    best_val_loss = float("inf")
    best_weights_path = MODELS_DIR / "qr_cnn_best.pth"
    history = []

    epochs = 12
    if best_weights_path.exists() and not force_retrain:
        print(f"Found trained weights at {best_weights_path}. Loading existing model...")
        model.load_state_dict(torch.load(best_weights_path, map_location=device))
    else:
        print(f"\n--- Training CNN with Balanced Loss for {epochs} epochs on CPU ---")
        t0_train = time.time()
        for epoch in range(1, epochs + 1):
            model.train()
            train_loss, train_correct, train_total = 0.0, 0, 0
            for x, y, _ in train_loader:
                x, y = x.to(device), y.to(device)
                optimizer.zero_grad()
                out = model(x)
                loss = criterion(out, y)
                loss.backward()
                optimizer.step()

                train_loss += loss.item() * x.size(0)
                preds = torch.argmax(out, dim=1)
                train_correct += (preds == y).sum().item()
                train_total += x.size(0)

            model.eval()
            val_loss, val_correct, val_total = 0.0, 0, 0
            val_preds_list, val_targets_list = [], []
            with torch.no_grad():
                for x, y, _ in val_loader:
                    x, y = x.to(device), y.to(device)
                    out = model(x)
                    loss = criterion(out, y)
                    val_loss += loss.item() * x.size(0)
                    preds = torch.argmax(out, dim=1)
                    val_correct += (preds == y).sum().item()
                    val_total += x.size(0)
                    val_preds_list.extend(preds.cpu().numpy().tolist())
                    val_targets_list.extend(y.cpu().numpy().tolist())

            epoch_train_loss = train_loss / train_total
            epoch_train_acc = train_correct / train_total
            epoch_val_loss = val_loss / val_total
            epoch_val_acc = val_correct / val_total

            # Compute balanced accuracy on validation set
            val_metrics = BenchmarkEvaluator.calculate_classification_metrics(np.array(val_targets_list), np.array(val_preds_list))
            epoch_val_bal_acc = val_metrics["balanced_accuracy"]

            history.append({
                "epoch": epoch,
                "train_loss": round(epoch_train_loss, 4),
                "train_acc": round(epoch_train_acc, 4),
                "val_loss": round(epoch_val_loss, 4),
                "val_acc": round(epoch_val_acc, 4),
                "val_balanced_acc": round(epoch_val_bal_acc, 4)
            })

            if epoch_val_loss < best_val_loss:
                best_val_loss = epoch_val_loss
                torch.save(model.state_dict(), best_weights_path)

            print(f"Epoch {epoch:02d}/{epochs:02d} | Train Loss: {epoch_train_loss:.4f} Acc: {epoch_train_acc:.4f} | Val Loss: {epoch_val_loss:.4f} Acc: {epoch_val_acc:.4f} BalAcc: {epoch_val_bal_acc:.4f}")

        train_duration = time.time() - t0_train
        print(f"CNN Training completed in {train_duration:.2f}s. Best weights saved to: {best_weights_path}")
        pd.DataFrame(history).to_csv(RESULTS_GAP10_DIR / "cnn_training_history.csv", index=False)

    # 4. Evaluate CNN on Held-Out Test Set
    model.load_state_dict(torch.load(best_weights_path, map_location=device))
    model.eval()

    all_preds_cnn = []
    all_probs_cnn = []
    all_targets = []
    all_sids = []

    t0_infer = time.perf_counter()
    with torch.no_grad():
        for x, y, sids in test_loader:
            x = x.to(device)
            out = model(x)
            probs = F.softmax(out, dim=1)[:, 1].numpy()
            preds = torch.argmax(out, dim=1).numpy()
            all_preds_cnn.extend(preds.tolist())
            all_probs_cnn.extend(probs.tolist())
            all_targets.extend(y.numpy().tolist())
            all_sids.extend(sids)
    test_infer_time_ms = ((time.perf_counter() - t0_infer) / len(all_targets)) * 1000.0

    cnn_metrics = BenchmarkEvaluator.calculate_classification_metrics(np.array(all_targets), np.array(all_preds_cnn))
    cnn_metrics["inference_latency_ms"] = round(test_infer_time_ms, 2)
    cnn_metrics["model"] = "QRArtifactCNN"

    # 5. Non-Neural Random Forest Baseline (Trained with class_weight='balanced')
    print("\n--- Training Handcrafted Feature Non-Neural Baseline (Random Forest) ---")
    def get_features_for_df(subset_df: pd.DataFrame):
        X_feats, y_labels = [], []
        for _, r in subset_df.iterrows():
            img = cv2.imread(str(BASE_DIR / r["image_path"]))
            feat = HandcraftedFeatureExtractor.extract_features(img)
            X_feats.append(feat)
            y_labels.append(int(r["ground_truth_label"]))
        return np.array(X_feats), np.array(y_labels)

    X_train_rf, y_train_rf = get_features_for_df(df_train)
    X_test_rf, y_test_rf = get_features_for_df(df_test)

    rf_model = BaselineRFClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    t0_rf_train = time.time()
    rf_model.fit(X_train_rf, y_train_rf)
    rf_train_time = time.time() - t0_rf_train

    t0_rf_inf = time.perf_counter()
    y_pred_rf = rf_model.predict(X_test_rf)
    y_prob_rf = rf_model.predict_proba(X_test_rf)[:, 1]
    rf_infer_time_ms = ((time.perf_counter() - t0_rf_inf) / len(y_test_rf)) * 1000.0

    rf_metrics = BenchmarkEvaluator.calculate_classification_metrics(y_test_rf, y_pred_rf)
    rf_metrics["inference_latency_ms"] = round(rf_infer_time_ms, 2)
    rf_metrics["model"] = "BaselineRandomForest"

    joblib.dump(rf_model, MODELS_DIR / "rf_baseline.joblib")

    # 6. Transparent Majority-Class Baseline (Always predicts majority class: 1 = Manipulated)
    majority_class = int(df_train["ground_truth_label"].mode()[0])
    y_pred_majority = np.full_like(all_targets, majority_class)
    maj_metrics = BenchmarkEvaluator.calculate_classification_metrics(np.array(all_targets), y_pred_majority)
    maj_metrics["inference_latency_ms"] = 0.00
    maj_metrics["model"] = "MajorityClassBaseline"
    maj_metrics["majority_class"] = majority_class

    # 7. Save Predictions & Summary
    df_test_preds = df_test.copy().reset_index(drop=True)
    df_test_preds["cnn_prediction"] = all_preds_cnn
    df_test_preds["cnn_prob_manipulated"] = all_probs_cnn
    df_test_preds["rf_prediction"] = y_pred_rf
    df_test_preds["rf_prob_manipulated"] = y_prob_rf
    df_test_preds["majority_prediction"] = y_pred_majority
    df_test_preds.to_csv(RESULTS_GAP10_DIR / "held_out_test_predictions.csv", index=False)

    summary = {
        "dataset_split": {
            "train_samples": len(df_train),
            "val_samples": len(df_val),
            "test_samples": len(df_test),
            "train_payloads": len(train_pids),
            "test_payloads": len(test_pids),
            "leakage_detected": False
        },
        "cnn_metrics": cnn_metrics,
        "rf_baseline_metrics": rf_metrics,
        "majority_baseline_metrics": maj_metrics
    }
    with open(RESULTS_GAP10_DIR / "classifier_benchmark_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 60)
    print("HELD-OUT TEST EVALUATION COMPARISON (ALL EVALUATED ON SAME TEST IDENTITIES):")
    print(f"Majority Baseline -> Precision: {maj_metrics['precision']:.4f}, Recall/ADR: {maj_metrics['recall']:.4f}, F1: {maj_metrics['f1_score']:.4f}, BalAcc: {maj_metrics['balanced_accuracy']:.4f}, FAR: {maj_metrics['far_percent']:.1f}%, FRR: {maj_metrics['frr_percent']:.1f}%")
    print(f"RF Baseline       -> Precision: {rf_metrics['precision']:.4f}, Recall/ADR: {rf_metrics['recall']:.4f}, F1: {rf_metrics['f1_score']:.4f}, BalAcc: {rf_metrics['balanced_accuracy']:.4f}, FAR: {rf_metrics['far_percent']:.1f}%, FRR: {rf_metrics['frr_percent']:.1f}%, Latency: {rf_metrics['inference_latency_ms']:.2f}ms")
    print(f"CNN Model         -> Precision: {cnn_metrics['precision']:.4f}, Recall/ADR: {cnn_metrics['recall']:.4f}, F1: {cnn_metrics['f1_score']:.4f}, BalAcc: {cnn_metrics['balanced_accuracy']:.4f}, FAR: {cnn_metrics['far_percent']:.1f}%, FRR: {cnn_metrics['frr_percent']:.1f}%, Latency: {cnn_metrics['inference_latency_ms']:.2f}ms")
    print("=" * 60)
    return summary

if __name__ == "__main__":
    train_and_evaluate_classifiers(force_retrain=True)
