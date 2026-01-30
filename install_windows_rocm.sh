@echo off

REM Install PyTorch with ROCm 7.2 on Windows

echo.
echo ========================================
echo AI Music Video Generator - ROCm 7.2 Setup
echo ========================================
echo.
echo Download and install ROCm 7.2 for Windows from:
echo https://repo.radeon.com/rocm/windows/rocm-rel-7.2/
echo.
echo Prerequisites:
echo 1. ROCm 7.2 for Windows
echo 2. Visual Studio 2022 (C++ workload)
echo 3. Python 3.13
echo.
echo Then run the following to install PyTorch with ROCm 7.2:
echo.
echo pip install torch torchaudio --pre --index-url https://rocm.nightlies.amd.com/v2/gfx120X-all/torch
echo.
echo Or use CPU-only version:
echo pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
echo.
pause
