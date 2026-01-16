@echo off
REM Video Upscaler Build Script
REM This script builds the Windows executable using PyInstaller

echo ==========================================
echo Video Upscaler Build Script
echo ==========================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found.
    echo Please create it first: python -m venv venv
    pause
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
venv\Scripts\pip.exe install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Building executable...
echo.

REM Run PyInstaller with the spec file
venv\Scripts\pyinstaller.exe --clean build.spec
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
echo Or run build_release.bat to do this automatically.
echo.
pause
