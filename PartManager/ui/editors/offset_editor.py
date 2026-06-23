"""Offset 偏移检测 — 参考 offset.ui"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QSpinBox, QCheckBox, QComboBox, QPushButton)
from PySide6.QtCore import Qt

class OffsetEditor(QWidget):
    def __init__(self): super().__init__(); self._init_ui()
    def _init_ui(self):
        l = QVBoxLayout(self); l.setSpacing(6)
        # RGB checkboxes + color mode
        rgb = QFrame(); rgb.setStyleSheet("background:#1c2128; border-radius:4px;")
        rl = QHBoxLayout(rgb); rl.setContentsMargins(6,4,6,4)
        self._cb_r = QCheckBox("R红"); self._cb_r.setChecked(True); rl.addWidget(self._cb_r)
        self._cb_g = QCheckBox("G绿"); self._cb_g.setChecked(True); rl.addWidget(self._cb_g)
        self._cb_b = QCheckBox("B蓝"); self._cb_b.setChecked(True); rl.addWidget(self._cb_b)
        sep = QFrame(); sep.setFrameShape(QFrame.VLine); sep.setStyleSheet("color:#30363d;"); rl.addWidget(sep)
        self._color_mode = QComboBox(); self._color_mode.addItems(["彩色","平均","最大"]); rl.addWidget(self._color_mode)
        l.addWidget(rgb)
        # Brightness
        h = QHBoxLayout(); h.addWidget(QLabel("亮度阈值:")); self._bright = QSpinBox(); self._bright.setRange(0,255); self._bright.setValue(100); h.addWidget(self._bright); l.addLayout(h)
        # Body edge
        h2 = QHBoxLayout(); h2.addWidget(QLabel("本体边缘位置:")); self._body = QSpinBox(); self._body.setRange(0,1000); self._body.setValue(104); h2.addWidget(self._body); l.addLayout(h2)
        l.addStretch()

    def load_params(self, p: dict):
        try:
            self._cb_r.setChecked(p.get("Color_Channel",7)&1)
            self._cb_g.setChecked(p.get("Color_Channel",7)&2)
            self._cb_b.setChecked(p.get("Color_Channel",7)&4)
            self._color_mode.setCurrentIndex(max(0,p.get("Color_Method",1)-1))
            self._bright.setValue(int(p.get("Color_Gray_Low",100)))
            self._body.setValue(int(p.get("Search_Scope_X",104)))
        except: pass
    def collect_values(self) -> dict:
        ch = (1 if self._cb_r.isChecked() else 0)|(2 if self._cb_g.isChecked() else 0)|(4 if self._cb_b.isChecked() else 0)
        return {"Color_Channel":ch,"Color_Method":self._color_mode.currentIndex()+1,
                "Color_Gray_Low":self._bright.value(),"Search_Scope_X":self._body.value()}
