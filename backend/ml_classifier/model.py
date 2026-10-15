"""
Deep-Learning AI Classifier and Machine-Learning Baseline for QR Artefact Authentication (Gap 10).
Distinguishes Genuine Authenticated QR Artefacts from Unauthorized Reproductions and Digital Manipulations.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import cv2
from typing import Dict, Any, List, Tuple
from skimage.feature import graycomatrix, graycoprops
from sklearn.ensemble import RandomForestClassifier

class QRArtifactCNN(nn.Module):
    """
    Lightweight, leakage-resilient Convolutional Neural Network
    designed for edge deployment and fast CPU inference (<15 ms).
    """

    def __init__(self, in_channels: int = 1, num_classes: int = 2):
        super(QRArtifactCNN, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, 16, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(16)
        self.pool1 = nn.MaxPool2d(2, 2) # 128 -> 64

        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(32)
        self.pool2 = nn.MaxPool2d(2, 2) # 64 -> 32

        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(64)
        self.pool3 = nn.MaxPool2d(2, 2) # 32 -> 16

        self.adaptive_pool = nn.AdaptiveAvgPool2d((4, 4))
        self.fc1 = nn.Linear(64 * 4 * 4, 64)
        self.dropout = nn.Dropout(0.3)
        self.fc2 = nn.Linear(64, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.pool1(F.relu(self.bn1(self.conv1(x))))
        x = self.pool2(F.relu(self.bn2(self.conv2(x))))
        x = self.pool3(F.relu(self.bn3(self.conv3(x))))
        x = self.adaptive_pool(x)
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

class HandcraftedFeatureExtractor:
    """
    Extracts statistical microtexture, DCT spectral, and gradient features
    for the non-neural Random Forest baseline.
    """

    @staticmethod
    def extract_features(image_rgb: np.ndarray) -> np.ndarray:
        """
        Extracts an 8-dimensional feature vector:
        [GLCM_contrast, GLCM_dissimilarity, GLCM_homogeneity, GLCM_energy,
         DCT_high_freq_ratio, Sobel_grad_mean, Sobel_grad_std, Lapl_var]
        """
        if len(image_rgb.shape) == 3:
            gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_rgb.copy()

        # Resize for fixed-scale analysis
        gray = cv2.resize(gray, (128, 128))

        # 1. GLCM Features
        glcm = graycomatrix(gray, distances=[1, 2], angles=[0, np.pi/4], levels=256, symmetric=True, normed=True)
        contrast = float(np.mean(graycoprops(glcm, "contrast")))
        dissimilarity = float(np.mean(graycoprops(glcm, "dissimilarity")))
        homogeneity = float(np.mean(graycoprops(glcm, "homogeneity")))
        energy = float(np.mean(graycoprops(glcm, "energy")))

        # 2. 2D DCT High-Frequency Energy Ratio
        dct = cv2.dct(gray.astype(np.float32))
        total_energy = float(np.sum(dct ** 2)) + 1e-8
        # High frequency: outer diagonal
        mask_lf = np.zeros_like(dct)
        mask_lf[:32, :32] = 1.0
        hf_energy = float(np.sum((dct * (1.0 - mask_lf)) ** 2))
        r_hf = hf_energy / total_energy

        # 3. Spatial Gradient Features
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        grad_mag = np.sqrt(sobelx**2 + sobely**2)
        grad_mean = float(np.mean(grad_mag))
        grad_std = float(np.std(grad_mag))

        # 4. Laplacian sharpness variance
        lapl_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        return np.array([
            contrast, dissimilarity, homogeneity, energy,
            r_hf, grad_mean, grad_std, lapl_var
        ], dtype=np.float32)

class BaselineRFClassifier:
    """Random Forest non-neural baseline classifier."""

    def __init__(self, n_estimators: int = 100, random_state: int = 42, class_weight: Any = "balanced"):
        self.rf = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state, class_weight=class_weight)
        self.is_trained = False

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.rf.fit(X, y)
        self.is_trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.rf.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.rf.predict_proba(X)
