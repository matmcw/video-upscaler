# Video Upscaler

AI-powered video upscaling application using Real-ESRGAN for Windows.

## Overview

Video Upscaler is a desktop GUI application that uses Real-ESRGAN artificial intelligence to enhance and upscale video resolution. It extracts frames from a video, upscales each frame using AI, then reassembles them with the original audio.

**Features:**
- 2x, 3x, and 4x upscaling options
- GPU-accelerated processing via Vulkan
- Preserves original audio track
- Progress tracking with ETA
- Dark themed modern interface

## Requirements

- Windows 10/11 (64-bit)
- Python 3.10+
- GPU with Vulkan support (NVIDIA GTX 1060 or better recommended)
- 8GB RAM minimum

## Project Structure

```
VideoUpscaler/
├── src/
│   ├── main.py                 # Entry point
│   ├── gui/
│   │   ├── main_window.py      # Main application window
│   │   ├── widgets.py          # Custom widgets
│   │   └── styles.py           # PyQt6 stylesheet
│   └── core/
│       ├── video_processor.py  # Processing pipeline
│       ├── frame_extractor.py  # FFmpeg frame extraction
│       ├── upscaler.py         # Real-ESRGAN wrapper
│       ├── video_assembler.py  # FFmpeg video assembly
│       └── utils.py            # Utilities and validation
├── models/                     # AI model files (not included)
├── build.spec                  # PyInstaller configuration
├── build_release.bat           # Build and package script
└── requirements.txt
```

## Development Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Download external binaries (place in project root):
   - [FFmpeg](https://www.gyan.dev/ffmpeg/builds/) - ffmpeg.exe and ffprobe.exe
   - [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN/releases/tag/v0.2.5.0) - realesrgan-ncnn-vulkan.exe

5. Download model files (place in `models/` folder):
   - realesr-animevideov3-x2.bin and .param
   - realesr-animevideov3-x3.bin and .param
   - realesr-animevideov3-x4.bin and .param

6. Run the application:
   ```bash
   python src/main.py
   ```

## Building for Distribution

Run the build script to create a distributable package:

```bash
build_release.bat
```

This creates:
- `dist/VideoUpscaler/` - Ready-to-run application folder
- `dist/VideoUpscaler-v1.0.zip` - Distributable ZIP archive

## Architecture

The application uses a multi-threaded architecture:
- **Main Thread**: PyQt6 GUI event loop
- **Worker Thread**: Video processing pipeline (QThread)

Processing pipeline:
1. **Validation** - Check dependencies and input file
2. **Frame Extraction** - FFmpeg extracts frames as PNG
3. **AI Upscaling** - Real-ESRGAN processes each frame
4. **Video Assembly** - FFmpeg combines frames with original audio
5. **Cleanup** - Remove temporary files

## Technologies

- **PyQt6** - GUI framework
- **Real-ESRGAN-ncnn-vulkan** - AI upscaling engine
- **FFmpeg** - Video processing
- **PyInstaller** - Executable packaging

## License

This application is provided as-is for personal use.
- Real-ESRGAN: BSD 3-Clause License
- FFmpeg: LGPL/GPL License

## Credits

- [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) by Xintao Wang et al.
- [FFmpeg](https://ffmpeg.org) by the FFmpeg team
