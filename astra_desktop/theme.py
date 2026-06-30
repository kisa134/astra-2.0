"""ASTRA Desktop — Fluent Design Theme System v4.0"""
from PySide6.QtGui import QFont, QPalette, QColor

# ═══════════════════════════════════════════════════════════
# FLUENT DESIGN TOKENS — Windows 11 / Apple Inspired
# ═══════════════════════════════════════════════════════════
class Colors:
    # Base (Slate scale — deep blue-gray, not pure black)
    BG_DEEP      = "#0f172a"   # Slate 900 — main background
    BG_PANEL     = "#1e293b"   # Slate 800 — cards/panels
    BG_CARD      = "#162032"   # Slightly darker card
    BG_HOVER     = "#334155"   # Slate 700 — hover state
    BG_ELEVATED  = "#27354f"   # Elevated surface
    
    # Accents (soft, not neon-aggressive)
    PRIMARY      = "#8b5cf6"   # Violet 500
    PRIMARY_L    = "#a78bfa"   # Violet 400 — lighter
    PRIMARY_D    = "#7c3aed"   # Violet 600 — darker
    SECONDARY    = "#14b8a6"   # Teal 500
    SECONDARY_L  = "#2dd4bf"   # Teal 400
    
    # Semantic (muted modern)
    SUCCESS      = "#10b981"   # Emerald 500
    WARNING      = "#f59e0b"   # Amber 500
    ERROR        = "#f43f5e"   # Rose 500
    INFO         = "#3b82f6"   # Blue 500
    
    # Text (warm, not harsh)
    TXT_PRIMARY  = "#f1f5f9"   # Slate 100
    TXT_SECONDARY= "#94a3b8"   # Slate 400
    TXT_DIM      = "#64748b"   # Slate 500
    TXT_MUTED    = "#475569"   # Slate 600
    
    # Glassmorphism (for panels)
    GLASS_BG     = "rgba(30, 41, 59, 0.75)"
    GLASS_BORDER = "rgba(148, 163, 184, 0.15)"
    
    # Gradient strings for QSS (subtle, not neon)
    GRADIENT_ACCENT = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8b5cf6, stop:1 #14b8a6)"


class Fonts:
    @staticmethod
    def get(size=12, weight=QFont.Weight.Normal, italic=False):
        f = QFont("Segoe UI", size)
        f.setWeight(weight)
        f.setItalic(italic)
        return f
    
    H1   = lambda: Fonts.get(28, QFont.Weight.DemiBold)
    H2   = lambda: Fonts.get(20, QFont.Weight.DemiBold)
    H3   = lambda: Fonts.get(14, QFont.Weight.Medium)
    BODY = lambda: Fonts.get(12, QFont.Weight.Normal)
    MONO = lambda: Fonts.get(11, QFont.Weight.Normal)
    SMALL= lambda: Fonts.get(10, QFont.Weight.Normal)
    TINY = lambda: Fonts.get(9, QFont.Weight.Light)
    BIG  = lambda: Fonts.get(42, QFont.Weight.DemiBold)


class Spacing:
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    XXL = 32
    SIDEBAR = 220
    HEADER  = 52


# ═══════════════════════════════════════════════════════════
# GLOBAL FLUENT STYLESHEET
# ═══════════════════════════════════════════════════════════
ASTRA_STYLESHEET = f"""
/* === ROOT === */
QMainWindow, QDialog, QWidget {{
    background-color: {Colors.BG_DEEP};
    color: {Colors.TXT_PRIMARY};
    font-family: 'Segoe UI', 'Inter', sans-serif;
    border: none;
}}

/* === SCROLLBARS (thin, modern) === */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    border-radius: 3px;
    margin: 4px 2px 4px 2px;
}}
QScrollBar::handle:vertical {{
    background: {Colors.BG_HOVER};
    border-radius: 3px;
    min-height: 40px;
}}
QScrollBar::handle:vertical:hover {{
    background: {Colors.PRIMARY};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
    border-radius: 3px;
    margin: 2px 4px 2px 4px;
}}
QScrollBar::handle:horizontal {{
    background: {Colors.BG_HOVER};
    border-radius: 3px;
    min-width: 40px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {Colors.PRIMARY};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* === BUTTONS (pill shape, soft) === */
QPushButton {{
    background-color: {Colors.BG_PANEL};
    color: {Colors.TXT_PRIMARY};
    border: 1px solid {Colors.BG_HOVER};
    border-radius: 10px;
    padding: 8px 18px;
    font-size: 12px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {Colors.BG_HOVER};
    border: 1px solid {Colors.PRIMARY_L};
}}
QPushButton:pressed {{
    background-color: {Colors.PRIMARY};
    color: #ffffff;
}}
QPushButton:disabled {{
    background-color: {Colors.BG_CARD};
    color: {Colors.TXT_MUTED};
    border: 1px solid {Colors.BG_CARD};
}}
QPushButton#accent {{
    background-color: {Colors.PRIMARY};
    color: #ffffff;
    border: none;
    font-weight: 600;
    padding: 10px 24px;
}}
QPushButton#accent:hover {{
    background-color: {Colors.PRIMARY_L};
}}
QPushButton#accent:pressed {{
    background-color: {Colors.PRIMARY_D};
}}
QPushButton#sidebar {{
    background-color: transparent;
    border: none;
    border-radius: 10px;
    padding: 10px 14px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
    color: {Colors.TXT_SECONDARY};
}}
QPushButton#sidebar:hover {{
    background-color: {Colors.BG_ELEVATED};
    color: {Colors.TXT_PRIMARY};
}}
QPushButton#sidebar:checked {{
    background-color: {Colors.BG_ELEVATED};
    color: {Colors.PRIMARY_L};
    border-left: 3px solid {Colors.PRIMARY};
}}

/* === INPUTS === */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {Colors.BG_CARD};
    color: {Colors.TXT_PRIMARY};
    border: 1px solid {Colors.BG_HOVER};
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13px;
    selection-background-color: {Colors.PRIMARY};
    selection-color: #ffffff;
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {Colors.PRIMARY};
}}
QLineEdit::placeholder, QTextEdit::placeholder {{
    color: {Colors.TXT_MUTED};
}}

/* === COMBO BOX === */
QComboBox {{
    background-color: {Colors.BG_CARD};
    color: {Colors.TXT_PRIMARY};
    border: 1px solid {Colors.BG_HOVER};
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 12px;
    min-width: 100px;
}}
QComboBox:hover {{
    border: 1px solid {Colors.PRIMARY};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background-color: {Colors.BG_PANEL};
    color: {Colors.TXT_PRIMARY};
    border: 1px solid {Colors.PRIMARY};
    border-radius: 8px;
    selection-background-color: {Colors.PRIMARY};
    selection-color: #ffffff;
    padding: 4px;
}}

/* === TOOLTIP === */
QToolTip {{
    background-color: {Colors.BG_PANEL};
    color: {Colors.TXT_PRIMARY};
    border: 1px solid {Colors.BG_HOVER};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 11px;
}}

/* === PROGRESS BAR === */
QProgressBar {{
    background-color: {Colors.BG_CARD};
    border: none;
    border-radius: 6px;
    height: 6px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    background-color: {Colors.PRIMARY};
    border-radius: 6px;
}}
QProgressBar#growth::chunk {{
    background-color: {Colors.SECONDARY};
}}
QProgressBar#health::chunk {{
    background-color: {Colors.SUCCESS};
}}

/* === MENU BAR === */
QMenuBar {{
    background-color: {Colors.BG_DEEP};
    color: {Colors.TXT_PRIMARY};
    border-bottom: 1px solid {Colors.BG_PANEL};
    padding: 4px;
}}
QMenuBar::item {{
    background-color: transparent;
    padding: 6px 14px;
    border-radius: 6px;
}}
QMenuBar::item:selected {{
    background-color: {Colors.BG_PANEL};
    color: {Colors.PRIMARY_L};
}}
QMenu {{
    background-color: {Colors.BG_PANEL};
    color: {Colors.TXT_PRIMARY};
    border: 1px solid {Colors.BG_HOVER};
    border-radius: 10px;
    padding: 6px;
}}
QMenu::item {{
    padding: 8px 20px;
    border-radius: 6px;
}}
QMenu::item:selected {{
    background-color: {Colors.BG_HOVER};
    color: {Colors.PRIMARY_L};
}}
QMenu::separator {{
    height: 1px;
    background-color: {Colors.BG_HOVER};
    margin: 6px 10px;
}}

/* === GROUP BOX === */
QGroupBox {{
    background-color: {Colors.BG_PANEL};
    border: 1px solid {Colors.BG_HOVER};
    border-radius: 12px;
    margin-top: 14px;
    padding-top: 12px;
    padding: 12px;
    font-size: 12px;
    font-weight: 600;
    color: {Colors.PRIMARY_L};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    top: -2px;
    padding: 0 8px;
    color: {Colors.PRIMARY_L};
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/* === LIST WIDGET === */
QListWidget {{
    background-color: transparent;
    border: none;
    outline: none;
    padding: 4px;
}}
QListWidget::item {{
    background-color: transparent;
    color: {Colors.TXT_SECONDARY};
    border-radius: 8px;
    padding: 10px 12px;
    margin: 2px 4px;
}}
QListWidget::item:hover {{
    background-color: {Colors.BG_ELEVATED};
    color: {Colors.TXT_PRIMARY};
}}
QListWidget::item:selected {{
    background-color: {Colors.BG_PANEL};
    color: {Colors.PRIMARY_L};
    border-left: 3px solid {Colors.PRIMARY};
}}

/* === TAB BAR === */
QTabBar::tab {{
    background-color: transparent;
    color: {Colors.TXT_SECONDARY};
    border: none;
    padding: 10px 24px;
    font-size: 12px;
    font-weight: 500;
    border-radius: 8px 8px 0 0;
}}
QTabBar::tab:hover {{
    color: {Colors.TXT_PRIMARY};
    background-color: {Colors.BG_ELEVATED};
}}
QTabBar::tab:selected {{
    color: {Colors.PRIMARY_L};
    background-color: {Colors.BG_PANEL};
}}
QTabWidget::pane {{
    border: none;
    background-color: {Colors.BG_DEEP};
}}
"""
