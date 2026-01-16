@echo off
REM ============================================================================
REM Video Upscaler - Build Release Script
REM Creates a distributable ZIP file with all dependencies
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo  Video Upscaler - Build Release
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "build.spec" (
    echo ERROR: build.spec not found. Run this script from the project root.
    pause
    exit /b 1
)

REM Check for required files
echo Checking required files...

set MISSING=0

if not exist "ffmpeg.exe" (
    echo   [MISSING] ffmpeg.exe
    set MISSING=1
)
if not exist "ffprobe.exe" (
    echo   [MISSING] ffprobe.exe
    set MISSING=1
)
if not exist "realesrgan-ncnn-vulkan.exe" (
    echo   [MISSING] realesrgan-ncnn-vulkan.exe
    set MISSING=1
)
if not exist "models\realesr-animevideov3-x2.bin" (
    echo   [MISSING] models\realesr-animevideov3-x2.bin
    set MISSING=1
)
if not exist "models\realesr-animevideov3-x2.param" (
    echo   [MISSING] models\realesr-animevideov3-x2.param
    set MISSING=1
)
if not exist "models\realesr-animevideov3-x3.bin" (
    echo   [MISSING] models\realesr-animevideov3-x3.bin
    set MISSING=1
)
if not exist "models\realesr-animevideov3-x3.param" (
    echo   [MISSING] models\realesr-animevideov3-x3.param
    set MISSING=1
)
if not exist "models\realesr-animevideov3-x4.bin" (
    echo   [MISSING] models\realesr-animevideov3-x4.bin
    set MISSING=1
)
if not exist "models\realesr-animevideov3-x4.param" (
    echo   [MISSING] models\realesr-animevideov3-x4.param
    set MISSING=1
)

if !MISSING!==1 (
    echo.
    echo ERROR: Required files are missing. See README.md for download instructions.
    pause
    exit /b 1
)

echo   All required files found.
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
echo   Done.
echo.

REM Activate venv and run PyInstaller
echo Building executable with PyInstaller...
echo   This may take a minute...
call venv\Scripts\activate.bat
venv\Scripts\pyinstaller.exe build.spec
if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed.
    pause
    exit /b 1
)
echo   Build complete.
echo.

REM Copy external files
echo Copying external dependencies...
copy /y "ffmpeg.exe" "dist\VideoUpscaler\" >nul
copy /y "ffprobe.exe" "dist\VideoUpscaler\" >nul
copy /y "realesrgan-ncnn-vulkan.exe" "dist\VideoUpscaler\" >nul
copy /y "RELEASE_README.txt" "dist\VideoUpscaler\README.txt" >nul
echo   Binaries copied.

REM Create models folder and copy models
mkdir "dist\VideoUpscaler\models" 2>nul
copy /y "models\*.bin" "dist\VideoUpscaler\models\" >nul
copy /y "models\*.param" "dist\VideoUpscaler\models\" >nul
echo   Models copied.
echo.

REM Wait for file handles to be released
echo Waiting for file handles to release...
timeout /t 3 /nobreak >nul

REM Create ZIP file
echo Creating ZIP archive...
set ZIPNAME=VideoUpscaler-v1.0.zip
if exist "dist\%ZIPNAME%" del "dist\%ZIPNAME%"
powershell -Command "Compress-Archive -Path 'dist\VideoUpscaler' -DestinationPath 'dist\%ZIPNAME%' -Force"
if errorlevel 1 (
    echo   First attempt failed, retrying in 5 seconds...
    timeout /t 5 /nobreak >nul
    powershell -Command "Compress-Archive -Path 'dist\VideoUpscaler' -DestinationPath 'dist\%ZIPNAME%' -Force"
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to create ZIP archive. Try closing other applications.
        echo You can manually ZIP the dist\VideoUpscaler folder.
        pause
        exit /b 1
    )
)
echo   Created: dist\%ZIPNAME%
echo.

REM Show results
echo ========================================
echo  Build Complete!
echo ========================================
echo.
echo Output files:
echo   dist\VideoUpscaler\     - Unzipped distribution folder
echo   dist\%ZIPNAME%  - Ready to distribute
echo.

REM Show ZIP size
for %%A in ("dist\%ZIPNAME%") do echo ZIP size: %%~zA bytes (~%%~zA bytes)
echo.

pause
