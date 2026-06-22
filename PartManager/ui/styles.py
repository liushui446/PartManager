"""
元器件模板库管理系统 - 深色主题样式表 v2
"""

GLOBAL_STYLE = """
/* === 全局 === */
QMainWindow { background-color: #0d1117; }
QDialog { background-color: #161b22; color: #c9d1d9; font-family: "Microsoft YaHei", "Segoe UI", sans-serif; }

/* === 菜单栏 === */
QMenuBar { background-color: #161b22; color: #c9d1d9; border-bottom: 1px solid #30363d; padding: 2px; }
QMenuBar::item { padding: 6px 12px; border-radius: 4px; }
QMenuBar::item:selected { background-color: #1f6feb; color: #fff; }
QMenu { background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 4px; }
QMenu::item { padding: 6px 28px; border-radius: 4px; }
QMenu::item:selected { background-color: #1f6feb; }

/* === QTreeWidget === */
QTreeWidget { background-color: #0d1117; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; padding: 4px; outline: none; font-size: 13px; }
QTreeWidget::item { height: 28px; padding: 3px 8px; border-radius: 4px; }
QTreeWidget::item:selected { background-color: #1f6feb; color: #fff; }
QTreeWidget::item:hover:!selected { background-color: #21262d; }

/* === QTableWidget === */
QTableWidget { background-color: #0d1117; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; gridline-color: #21262d; font-size: 12px; selection-background-color: #1f6feb; selection-color: #fff; }
QTableWidget::item { padding: 4px 8px; }
QHeaderView::section { background-color: #21262d; color: #8b949e; font-weight: bold; padding: 5px 8px; border: none; border-right: 1px solid #30363d; border-bottom: 1px solid #30363d; font-size: 12px; }

/* === QTabWidget === */
QTabWidget::pane { background-color: #0d1117; border: 1px solid #30363d; border-radius: 6px; top: -1px; }
QTabBar::tab { background-color: #21262d; color: #8b949e; padding: 6px 16px; border: 1px solid #30363d; border-bottom: none; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; font-size: 12px; }
QTabBar::tab:selected { background-color: #0d1117; color: #58a6ff; border-bottom: 2px solid #1f6feb; }
QTabBar::tab:hover:!selected { background-color: #30363d; color: #c9d1d9; }

/* === QPushButton === */
QPushButton { background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; padding: 7px 14px; font-size: 12px; font-weight: bold; }
QPushButton:hover { background-color: #30363d; border-color: #8b949e; }
QPushButton:pressed { background-color: #0d419d; }

QPushButton#btnPrimary { background-color: #238636; border-color: #2ea043; color: #fff; }
QPushButton#btnPrimary:hover { background-color: #2ea043; }

/* === QComboBox === */
QComboBox { background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; padding: 5px 10px; font-size: 13px; min-height: 20px; }
QComboBox:hover { border-color: #58a6ff; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView { background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; selection-background-color: #1f6feb; }

/* === QLineEdit === */
QLineEdit { background-color: #0d1117; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; padding: 5px 10px; font-size: 13px; }
QLineEdit:focus { border-color: #58a6ff; }

/* === QSpinBox / QDoubleSpinBox === */
QSpinBox, QDoubleSpinBox { background-color: #0d1117; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; padding: 5px 8px; font-size: 13px; }
QSpinBox:focus, QDoubleSpinBox:focus { border-color: #58a6ff; }

/* === QSlider === */
QSlider::groove:horizontal { background: #30363d; height: 5px; border-radius: 3px; }
QSlider::handle:horizontal { background: #58a6ff; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px; }
QSlider::handle:horizontal:hover { background: #79c0ff; }
QSlider::sub-page:horizontal { background: #1f6feb; border-radius: 3px; }

/* === QGroupBox === */
QGroupBox { color: #c9d1d9; border: 1px solid #30363d; border-radius: 8px; margin-top: 12px; padding: 14px 10px 10px 10px; font-size: 12px; font-weight: bold; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 6px; color: #58a6ff; }

/* === QLabel === */
QLabel { color: #c9d1d9; font-size: 13px; }

/* === QSplitter === */
QSplitter::handle { background-color: #30363d; width: 2px; }

/* === QScrollBar === */
QScrollBar:vertical { background-color: #0d1117; width: 8px; border-radius: 4px; }
QScrollBar::handle:vertical { background-color: #30363d; border-radius: 4px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background-color: #484f58; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background-color: #0d1117; height: 8px; border-radius: 4px; }
QScrollBar::handle:horizontal { background-color: #30363d; border-radius: 4px; min-width: 30px; }
QScrollBar::handle:horizontal:hover { background-color: #484f58; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* === QStatusBar === */
QStatusBar { background-color: #161b22; color: #8b949e; border-top: 1px solid #30363d; font-size: 12px; }

/* === QCheckBox === */
QCheckBox { color: #c9d1d9; font-size: 13px; }
QCheckBox::indicator { width: 16px; height: 16px; border: 1px solid #30363d; border-radius: 3px; background-color: #0d1117; }
QCheckBox::indicator:checked { background-color: #1f6feb; border-color: #58a6ff; }

/* === QRadioButton === */
QRadioButton { color: #c9d1d9; font-size: 13px; }

/* === QListWidget === */
QListWidget { background-color: #0d1117; color: #c9d1d9; border: 1px solid #30363d; border-radius: 4px; font-size: 12px; outline: none; }
QListWidget::item { padding: 5px 8px; border-radius: 3px; }
QListWidget::item:selected { background-color: #1f6feb; color: #fff; }
QListWidget::item:hover:!selected { background-color: #21262d; }
"""

# ─── 紧凑标题栏 ───
TITLE_STYLE = """
QLabel#titleLabel {
    font-size: 18px; font-weight: bold; color: #58a6ff; padding: 2px 8px;
    border-bottom: 2px solid #1f6feb;
}
"""

# ─── 紧凑摘要栏（单行横向） ───
SUMMARY_STYLE = """
QLabel#summaryValue {
    font-size: 15px; font-weight: bold; color: #58a6ff;
}
QLabel#summaryLabel {
    font-size: 10px; color: #8b949e;
}
"""

# ─── 参数编辑器字体（白色） ───
PARAM_PANEL_STYLE = """
QScrollArea#paramScroll { background-color: transparent; border: none; }
QWidget#paramContainer { background-color: #0d1117; }
QLabel#paramTitle {
    font-size: 14px; font-weight: bold; color: #58a6ff; padding: 4px 0;
    border-bottom: 1px solid #30363d;
}
QLabel#paramLabel {
    font-size: 12px; color: #e6edf3;
    min-width: 110px;
}
QLabel#paramValue {
    font-size: 12px; color: #c9d1d9;
}
QLabel#sectionTitle {
    font-size: 13px; font-weight: bold; color: #79c0ff;
    padding: 4px 0;
}
"""

# ─── 状态栏 ───
STATUS_STYLE = """
QLabel#statusLabel { color: #8b949e; font-size: 11px; }
"""

# ─── 卡片框架 ───
CARD_STYLE = """
QFrame#cardFrame {
    background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 4px;
}
"""
