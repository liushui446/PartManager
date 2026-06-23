"""OCR 错件检测 — 参考 ocr_wrong.ui"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QSlider, QSpinBox, QCheckBox, QComboBox, QRadioButton, QFrame)
from PySide6.QtCore import Qt

class OcrEditor(QWidget):
    def __init__(self): super().__init__(); self._init_ui()
    def _init_ui(self):
        l = QVBoxLayout(self); l.setSpacing(6)
        # Top: char type + RGB + color
        tr = QHBoxLayout()
        cg = QGroupBox("字符类别"); cl = QHBoxLayout(cg)
        self._rb_ind = QRadioButton("独立字符"); self._rb_ind.setChecked(True); cl.addWidget(self._rb_ind)
        self._rb_conn = QRadioButton("连体字符"); cl.addWidget(self._rb_conn); tr.addWidget(cg)
        rgb = QFrame(); rgb.setStyleSheet("background:#1c2128; border-radius:4px;")
        rl = QHBoxLayout(rgb); rl.setContentsMargins(6,4,6,4)
        self._cb_r = QCheckBox("R红"); rl.addWidget(self._cb_r)
        self._cb_g = QCheckBox("G绿"); self._cb_g.setChecked(True); rl.addWidget(self._cb_g)
        self._cb_b = QCheckBox("B蓝"); self._cb_b.setChecked(True); rl.addWidget(self._cb_b)
        sep = QFrame(); sep.setFrameShape(QFrame.VLine); sep.setStyleSheet("color:#30363d;"); rl.addWidget(sep)
        self._cmb = QComboBox(); self._cmb.addItems(["最大","平均","彩色"]); rl.addWidget(self._cmb)
        tr.addWidget(rgb)
        bw = QGroupBox("字符黑白"); bl = QHBoxLayout(bw)
        self._rb_white = QRadioButton("白色字符"); self._rb_white.setChecked(True); bl.addWidget(self._rb_white)
        self._rb_black = QRadioButton("黑色字符"); bl.addWidget(self._rb_black); tr.addWidget(bw)
        l.addLayout(tr)
        # Sliders
        g = QGridLayout(); g.setSpacing(4)
        sliders = [("字符宽度","h_w",0,100,37),("大小下限","h_sz",0,350,150)]
        self._sliders = {}
        for r,(lb,key,lo,hi,dv) in enumerate(sliders):
            g.addWidget(QLabel(lb),r,0)
            s = QSlider(Qt.Horizontal); s.setRange(lo,hi); s.setValue(dv); s.setPageStep(10); g.addWidget(s,r,1)
            sp = QSpinBox(); sp.setRange(lo,hi); sp.setValue(dv); g.addWidget(sp,r,2)
            s.valueChanged.connect(lambda v,sb=sp:(sb.blockSignals(True),sb.setValue(v),sb.blockSignals(False)))
            sp.valueChanged.connect(lambda v,sl=s:(sl.blockSignals(True),sl.setValue(v),sl.blockSignals(False)))
            self._sliders[key] = sp
        l.addLayout(g); l.addStretch()

    def load_params(self, p: dict):
        try:
            self._sliders["h_w"].setValue(int(p.get("Binary_Threshold",37)))
            self._sliders["h_sz"].setValue(int(p.get("Contour_NumThre",150)))
        except: pass

    def collect_values(self) -> dict:
        return {
            "Binary_Threshold": self._sliders["h_w"].value(),
            "Contour_NumThre": self._sliders["h_sz"].value(),
        }
