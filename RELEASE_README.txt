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


QUICK START
-----------
1. Double-click VideoUpscaler.exe
2. Click "Browse..." to select your video
3. Choose scale factor (2x, 3x, or 4x)
4. Click "Start Upscaling"
5. Wait for processing to complete


USAGE
-----

1. Launch the application by double-clicking VideoUpscaler.exe

2. Select your input video:
   - Click "Browse..." or drag and drop a video file
   - Supported formats: MP4, MKV, AVI, MOV, WMV, FLV, WEBM

3. The output path is auto-generated but can be changed

4. Select your desired scale factor:
   - 2x: Double the resolution (e.g., 1080p -> 4K) - Fastest
   - 3x: Triple the resolution
   - 4x: Quadruple the resolution (e.g., 1080p -> 8K) - Slowest

5. Click "Start Upscaling" to begin processing
   - Progress shows frame count and estimated time remaining
   - Click "Cancel" to stop processing at any time

6. When complete, find your upscaled video at the output location


TIPS FOR BEST RESULTS
---------------------
- Use high-quality source videos for best results
- 2x upscaling is fastest and often sufficient for most uses
- 4x upscaling takes significantly longer but provides maximum detail
- Close other GPU-intensive applications during processing
- Ensure you have enough disk space (temp files can be several GB)


TROUBLESHOOTING
---------------

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

Application won't start
  -> Make sure all files are in the same folder
  -> Try running as administrator
  -> Check that your antivirus isn't blocking the application


CREDITS
-------
- Real-ESRGAN by Xintao Wang et al.
  https://github.com/xinntao/Real-ESRGAN

- FFmpeg by the FFmpeg team
  https://ffmpeg.org


LICENSE
-------
This application is provided as-is for personal use.
Real-ESRGAN and FFmpeg are subject to their respective licenses.


================================================================================
                        Thank you for using Video Upscaler!
================================================================================
