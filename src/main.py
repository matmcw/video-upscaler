"""
Video Upscaler - Main Entry Point

AI-powered video upscaling application using Real-ESRGAN.
Supports 2x, 3x, and 4x upscaling for photorealistic video content.

Usage:
    python main.py              # Launch GUI application
    python main.py --help       # Show help

When packaged as an executable:
    VideoUpscaler.exe           # Launch GUI application
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path for imports when running as script
if not getattr(sys, 'frozen', False):
    src_dir = Path(__file__).parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))


def main():
    """Main entry point for the Video Upscaler application."""
    # Import PyQt6 here to allow the path setup above to complete first
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon

    from gui.main_window import MainWindow

    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Video Upscaler")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("VideoUpscaler")

    # Set application icon if available
    icon_path = Path(__file__).parent.parent / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
