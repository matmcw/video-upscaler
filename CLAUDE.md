# CLAUDE.md - Video Upscaler Project

## Project Purpose
Windows GUI application for AI-powered video upscaling of photorealistic content (baseball edits).
Uses Real-ESRGAN-ncnn-vulkan for frame enhancement with PyQt6 interface.

## Architecture Overview
- **GUI Layer**: PyQt6 main window with file pickers, settings, progress display
- **Processing Layer**: QThread worker running FFmpeg + Real-ESRGAN pipeline
- **Core Modules**: Separate files for frame extraction, upscaling, assembly

## Key Design Decisions
1. Single video processing (no batch queue)
2. Scale factor only in settings (2x, 3x, 4x)
3. Temp files stored in `temp/` next to EXE
4. Binaries bundled, models external

## Code Conventions
- Use pathlib.Path for all file operations
- Subprocess calls use subprocess.run() with capture_output=True
- GUI updates via Qt signals/slots (never directly from worker thread)
- Error messages should be user-friendly with actionable next steps

## File Naming
- Python files: snake_case.py
- Classes: PascalCase
- Functions/variables: snake_case

## Processing Pipeline
1. validate_inputs() - Check file exists, binaries present
2. get_video_info() - FFprobe for fps, frame count
3. extract_frames() - FFmpeg to temp/input/
4. upscale_frames() - Real-ESRGAN temp/input/ → temp/output/
5. assemble_video() - FFmpeg combine frames + original audio
6. cleanup() - Remove temp folders

## Threading
- MainWindow runs on main thread
- VideoProcessor runs on QThread
- Progress updates via pyqtSignal(int, int, str) → (current, total, status)

## Build Command
```
pyinstaller --onedir --windowed --name VideoUpscaler src/main.py
```

## Testing Checklist
- [ ] File picker selects video correctly
- [ ] Progress bar updates during processing
- [ ] Cancel button stops processing cleanly
- [ ] Output video has correct resolution
- [ ] Audio is preserved in output
- [ ] Error dialogs show for missing files/binaries

## File Structure
```
VideoUpscaler/
├── src/
│   ├── main.py                 # Entry point
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py      # Main application window
│   │   ├── widgets.py          # Custom widgets (progress, file picker)
│   │   └── styles.py           # PyQt6 stylesheet
│   └── core/
│       ├── __init__.py
│       ├── video_processor.py  # Main processing pipeline
│       ├── frame_extractor.py  # FFmpeg frame extraction
│       ├── upscaler.py         # Real-ESRGAN wrapper
│       ├── video_assembler.py  # FFmpeg video assembly
│       └── utils.py            # Path helpers, validation
├── models/                     # Model files (user downloads)
├── requirements.txt
├── build.spec
└── README.txt
```

## External Dependencies
- ffmpeg.exe - Video frame extraction and assembly
- ffprobe.exe - Video metadata extraction
- realesrgan-ncnn-vulkan.exe - AI upscaling engine
- Model files: realesrgan-x4plus.bin and realesrgan-x4plus.param
