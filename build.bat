@echo off
REM Video Upscaler Build Script
REM This script builds the Windows executable using PyInstaller

echo ==========================================
echo Video Upscaler Build Script
echo ==========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Building executable...
echo.

REM Run PyInstaller with the spec file
pyinstaller --clean build.spec
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Build complete!
echo ==========================================
echo.
echo Output location: dist\VideoUpscaler\
echo.
echo Next steps:
echo 1. Copy ffmpeg.exe to dist\VideoUpscaler\
echo 2. Copy ffprobe.exe to dist\VideoUpscaler\
echo 3. Copy realesrgan-ncnn-vulkan.exe to dist\VideoUpscaler\
echo 4. Create models\ folder and add model files
echo.
echo See README.txt for download links.
echo.
pause
