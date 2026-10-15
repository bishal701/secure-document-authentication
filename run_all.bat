@echo off
setlocal enabledelayedexpansion
title Secure Document Authentication & QR Watermarking Suite

:MENU
cls
echo ===========================================================================
echo       SECURE DOCUMENT AUTHENTICATION & QR WATERMARKING SUITE
echo ===========================================================================
echo   Project: Stealth-Aware QR Watermarking (LSB vs DWT-DCT, Print-Scan, AI)
echo   Author:  Bishal Paul (23BCI0224, VIT Vellore)
echo ===========================================================================
echo.
echo   [1] Run All PyTest Test Cases (31 tests)
echo   [2] Run Comprehensive End-to-End System Audit (27 security checks)
echo   [3] Start Interactive Web Dashboard & API (http://127.0.0.1:8000)
echo   [4] Run Gap 3 Benchmark (Spatial LSB vs Transform DWT-DCT)
echo   [5] Run Gap 10 Benchmark (Watermark Strength vs AI Classification)
echo   [6] Re-Generate All 10 Publication Figures (300 DPI)
echo   [7] Recompile Research Paper (DOCX and PDF Manuscripts)
echo   [8] Validate Physical Hardware Manifest (Gap 4)
echo   [9] Run Full Automated Pipeline (Benchmarks + Figures + Paper + Tests)
echo   [0] Exit
echo.
echo ===========================================================================
set /p choice="Enter your choice [0-9]: "

if "%choice%"=="1" goto PYTEST
if "%choice%"=="2" goto AUDIT
if "%choice%"=="3" goto WEBAPP
if "%choice%"=="4" goto GAP3
if "%choice%"=="5" goto GAP10
if "%choice%"=="6" goto FIGURES
if "%choice%"=="7" goto PAPER
if "%choice%"=="8" goto MANIFEST
if "%choice%"=="9" goto RUNALL
if "%choice%"=="0" goto EXIT
echo Invalid choice, please try again.
pause
goto MENU

:PYTEST
cls
echo [Executing PyTest Suite...]
python -m pytest -v tests/
echo.
pause
goto MENU

:AUDIT
cls
echo [Executing End-to-End Cryptographic & Security Verification Audit...]
python run_complete_system_test.py
echo.
pause
goto MENU

:WEBAPP
cls
echo [Starting Web App on http://127.0.0.1:8000 - Press Ctrl+C in CMD to stop]
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
pause
goto MENU

:GAP3
cls
echo [Executing Gap 3 Benchmark: LSB vs. DWT-DCT...]
python scripts\run_gap3_benchmark.py
echo.
pause
goto MENU

:GAP10
cls
echo [Executing Gap 10 Benchmark: Stealth-Accuracy Pareto Analysis...]
python scripts\run_gap10_benchmark.py
echo.
pause
goto MENU

:FIGURES
cls
echo [Re-Generating All 10 Publication Figures (300 DPI)...]
python scripts\generate_publication_figures.py
echo.
pause
goto MENU

:PAPER
cls
echo [Recompiling Research Paper DOCX and PDF...]
python scripts\generate_research_manuscript.py
echo.
pause
goto MENU

:MANIFEST
cls
echo [Validating Physical Hardware Manifest...]
python scripts\validate_physical_manifest.py
echo.
pause
goto MENU

:RUNALL
cls
echo ===========================================================================
echo RUNNING COMPLETE RESEARCH & VERIFICATION PIPELINE
echo ===========================================================================
echo.
echo [1/6] Running PyTest suite...
python -m pytest -v tests/
echo.
echo [2/6] Running System Verification Audit...
python run_complete_system_test.py
echo.
echo [3/6] Running Gap 3 Benchmark...
python scripts\run_gap3_benchmark.py
echo.
echo [4/6] Running Gap 10 Benchmark & Pareto Analysis...
python scripts\run_gap10_benchmark.py
echo.
echo [5/6] Generating Publication Figures...
python scripts\generate_publication_figures.py
echo.
echo [6/6] Generating Research Manuscript (DOCX & PDF)...
python scripts\generate_research_manuscript.py
echo.
echo ===========================================================================
echo FULL RESEARCH PIPELINE SUCCESSFULLY COMPLETED!
echo ===========================================================================
pause
goto MENU

:EXIT
echo Exiting. Goodbye!
exit /b 0
