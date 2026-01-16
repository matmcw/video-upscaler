"""
PyQt6 stylesheets for Video Upscaler.

Provides a modern, clean appearance with consistent styling across
all widgets. Uses a dark theme optimized for video editing workflows.
"""

# Color palette
COLORS = {
    "background": "#1a1a1a",
    "background_light": "#242424",
    "background_lighter": "#333333",
    "foreground": "#ffffff",
    "foreground_dim": "#888888",
    "accent": "#0078d4",
    "accent_hover": "#1a8cff",
    "accent_pressed": "#005a9e",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "border": "#3a3a3a",
}

STYLESHEET = f"""
/* Global styles */
QWidget {{
    background-color: {COLORS["background"]};
    color: {COLORS["foreground"]};
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 10pt;
}}

QMainWindow {{
    background-color: {COLORS["background"]};
}}

/* Section headers */
QLabel[class="section-header"] {{
    font-size: 14pt;
    font-weight: bold;
    color: {COLORS["foreground"]};
    padding: 8px 0;
}}

/* Field labels */
QLabel[class="field-label"] {{
    font-size: 10pt;
    color: {COLORS["foreground_dim"]};
}}

/* Step labels */
QLabel[class="step-label"] {{
    font-size: 9pt;
    color: {COLORS["foreground_dim"]};
}}

QLabel[class="step-label-active"] {{
    font-size: 9pt;
    color: {COLORS["accent"]};
    font-weight: bold;
}}

/* Video info */
QLabel[class="video-info"] {{
    font-size: 9pt;
    color: {COLORS["foreground_dim"]};
    padding: 4px 0;
}}

/* Line edits */
QLineEdit {{
    background-color: {COLORS["background_light"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 10px 12px;
    color: {COLORS["foreground"]};
    font-size: 10pt;
    selection-background-color: {COLORS["accent"]};
}}

QLineEdit:focus {{
    border-color: {COLORS["accent"]};
}}

QLineEdit:disabled {{
    background-color: {COLORS["background"]};
    color: {COLORS["foreground_dim"]};
}}

/* Regular buttons */
QPushButton {{
    background-color: {COLORS["background_lighter"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 8px 16px;
    color: {COLORS["foreground"]};
    font-size: 10pt;
}}

QPushButton:hover {{
    background-color: {COLORS["border"]};
}}

QPushButton:pressed {{
    background-color: {COLORS["background_light"]};
}}

QPushButton:disabled {{
    background-color: {COLORS["background"]};
    color: {COLORS["foreground_dim"]};
    border-color: {COLORS["background_light"]};
}}

/* Primary button */
QPushButton[class="primary"] {{
    background-color: {COLORS["accent"]};
    border-color: {COLORS["accent"]};
    color: white;
    font-weight: bold;
    font-size: 11pt;
    padding: 12px 24px;
}}

QPushButton[class="primary"]:hover {{
    background-color: {COLORS["accent_hover"]};
    border-color: {COLORS["accent_hover"]};
}}

QPushButton[class="primary"]:pressed {{
    background-color: {COLORS["accent_pressed"]};
}}

QPushButton[class="primary"]:disabled {{
    background-color: {COLORS["background_lighter"]};
    border-color: {COLORS["border"]};
    color: {COLORS["foreground_dim"]};
}}

/* Danger button */
QPushButton[class="danger"] {{
    background-color: {COLORS["error"]};
    border-color: {COLORS["error"]};
    color: white;
}}

QPushButton[class="danger"]:hover {{
    background-color: #dc2626;
}}

/* Scale toggle buttons */
QPushButton[class="scale-toggle"] {{
    background-color: {COLORS["background_light"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 0;
    padding: 8px 24px;
    color: {COLORS["foreground_dim"]};
    font-weight: normal;
    min-width: 60px;
}}

QPushButton[class="scale-toggle"][position="left"] {{
    border-top-left-radius: 6px;
    border-bottom-left-radius: 6px;
}}

QPushButton[class="scale-toggle"][position="right"] {{
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
}}

QPushButton[class="scale-toggle"]:checked {{
    background-color: {COLORS["accent"]};
    border-color: {COLORS["accent"]};
    color: white;
    font-weight: bold;
}}

QPushButton[class="scale-toggle"]:hover:!checked {{
    background-color: {COLORS["background_lighter"]};
}}

QPushButton[class="scale-toggle"]:disabled {{
    background-color: {COLORS["background"]};
    color: {COLORS["foreground_dim"]};
}}

/* Progress bars */
QProgressBar {{
    background-color: {COLORS["background_light"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    text-align: center;
    color: {COLORS["foreground"]};
    font-size: 9pt;
}}

QProgressBar::chunk {{
    background-color: {COLORS["accent"]};
    border-radius: 5px;
}}

QProgressBar[class="complete"]::chunk {{
    background-color: {COLORS["success"]};
}}

QProgressBar[class="error"] {{
    border-color: {COLORS["error"]};
}}

QProgressBar[class="error"]::chunk {{
    background-color: {COLORS["error"]};
}}

/* Scroll area */
QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollArea > QWidget > QWidget {{
    background-color: transparent;
}}

/* Scroll bars */
QScrollBar:vertical {{
    background-color: {COLORS["background"]};
    width: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS["background_lighter"]};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS["border"]};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
}}

/* Message boxes */
QMessageBox {{
    background-color: {COLORS["background_light"]};
}}

QMessageBox QLabel {{
    color: {COLORS["foreground"]};
}}

/* Tooltips */
QToolTip {{
    background-color: {COLORS["background_light"]};
    color: {COLORS["foreground"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 4px;
    padding: 4px 8px;
}}

/* Separator line */
QFrame[class="separator"] {{
    background-color: {COLORS["border"]};
    max-height: 1px;
}}
"""


def get_stylesheet() -> str:
    return STYLESHEET


def get_colors() -> dict:
    return COLORS.copy()
