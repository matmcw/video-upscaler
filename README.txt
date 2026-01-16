================================================================================
                           VIDEO UPSCALER v1.0
                    AI-Powered Video Upscaling Tool
================================================================================

Video Upscaler uses Real-ESRGAN artificial intelligence to enhance and upscale
video resolution. Perfect for upscaling 1080p footage to 4K quality.


SYSTEM REQUIREMENTS
-------------------
- Windows 10/11 (64-bit)
- GPU with Vulkan support (NVIDIA GTX 1060 or better recommended)
- 8GB RAM minimum (16GB recommended)
- Sufficient disk space for temporary frame storage


FOLDER STRUCTURE
----------------
After setup, your folder should look like this:

    VideoUpscaler/
    ├── VideoUpscaler.exe              <- Main application
    ├── ffmpeg.exe                     <- Video processing (download required)
    ├── ffprobe.exe                    <- Video analysis (download required)
    ├── realesrgan-ncnn-vulkan.exe     <- AI upscaler (download required)
    ├── models/                        <- Model files folder
    │   ├── realesr-animevideov3-x2.bin    <- 2x model (download required)
    │   ├── realesr-animevideov3-x2.param
    │   ├── realesr-animevideov3-x3.bin    <- 3x model (download required)
    │   ├── realesr-animevideov3-x3.param
    │   ├── realesr-animevideov3-x4.bin    <- 4x model (download required)
    │   └── realesr-animevideov3-x4.param
    ├── temp/                          <- Created automatically during processing
    └── README.txt                     <- This file


SETUP INSTRUCTIONS
------------------

1. DOWNLOAD FFMPEG
   - Go to: https://www.gyan.dev/ffmpeg/builds/
   - Download "ffmpeg-release-essentials.zip"
   - Extract and copy ffmpeg.exe and ffprobe.exe to this folder

2. DOWNLOAD REAL-ESRGAN (includes models)
   - Go to: https://github.com/xinntao/Real-ESRGAN/releases/tag/v0.2.5.0
   - Download "realesrgan-ncnn-vulkan-20220424-windows.zip"
   - Extract and copy:
     * realesrgan-ncnn-vulkan.exe to this folder
     * All files from the "models" subfolder to the models/ folder here

   Required model files (for 2x, 3x, 4x upscaling):
     - realesr-animevideov3-x2.bin and .param
     - realesr-animevideov3-x3.bin and .param
     - realesr-animevideov3-x4.bin and .param


USAGE
-----

1. Double-click VideoUpscaler.exe to launch the application

2. Click "Browse..." next to "Input Video" to select your video file
   - Supported formats: MP4, MKV, AVI, MOV, WMV, FLV, WEBM

3. The output path is auto-generated, but you can change it if needed

4. Select your desired scale factor:
   - 2x: Double the resolution (e.g., 1080p -> 2160p)
   - 3x: Triple the resolution
   - 4x: Quadruple the resolution (e.g., 1080p -> 4320p/8K)

5. Click "Start Upscaling" and wait for processing to complete
   - Progress is shown with frame count and estimated time remaining
   - Processing time depends on video length and resolution

6. The upscaled video will be saved to the output location


TIPS FOR BEST RESULTS
---------------------

- Use high-quality source videos for best results
- 2x upscaling is fastest and often sufficient
- 4x upscaling takes significantly longer but provides maximum detail
- Close other GPU-intensive applications during processing
- Ensure you have enough disk space (temp files can be large)


TROUBLESHOOTING
---------------

"FFmpeg not found"
  -> Download FFmpeg and place ffmpeg.exe in the application folder

"Real-ESRGAN not found"
  -> Download Real-ESRGAN and place the exe in the application folder

"Model files not found"
  -> Create a 'models' folder and add the realesr-animevideov3 model files
  -> You need the -x2, -x3, and -x4 versions (.bin and .param for each)

"Vulkan GPU initialization failed"
  -> Update your graphics card drivers
  -> Ensure your GPU supports Vulkan (most modern GPUs do)

"GPU ran out of memory"
  -> Try processing a lower resolution video
  -> Close other applications using the GPU
  -> Use a smaller scale factor (2x instead of 4x)

"Processing appears stuck"
  -> Check GPU utilization in Task Manager
  -> Some frames take longer to process than others
  -> For very long videos, processing can take hours


KEYBOARD SHORTCUTS
------------------
Ctrl+O    Open video file
Ctrl+S    Save output as (change output path)
Ctrl+Q    Quit application


CREDITS
-------
- Real-ESRGAN by Xintao Wang et al.
  https://github.com/xinntao/Real-ESRGAN

- FFmpeg by the FFmpeg team
  https://ffmpeg.org

- Built with PyQt6


LICENSE
-------
This application is provided as-is for personal use.
Real-ESRGAN and FFmpeg are subject to their respective licenses.


SUPPORT
-------
For issues and feature requests, please contact the developer.


================================================================================
                         Thank you for using Video Upscaler!
================================================================================
