"""Short 短路检测 — 参考 short.ui"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QSlider, QSpinBox, QCheckBox, QComboBox, QPushButton, QRadioButton,
    QStackedWidget, QFrame, QGroupBox, QButtonGroup)
from PySide6.QtCore import Qt

class ShortEditor(QWidget):
    def __init__(self): super().__init__(); self._init_ui()
    def _init_ui(self):
        l = QVBoxLayout(self); l.setSpacing(6)
        # Mode radio
        hr = QHBoxLayout()
        self._rb_proj = QRadioButton("投影"); self._rb_proj.setChecked(True)
        self._rb_color = QRadioButton("抽色"); self._rb_color.setEnabled(False)
        self._cb_watch = QCheckBox("观察"); self._cb_watch.setChecked(True)
        hr.addWidget(self._rb_proj); hr.addWidget(self._rb_color); hr.addWidget(self._cb_watch); hr.addStretch()
        l.addLayout(hr)
        # RGB row
        self._rgb_frame = self._make_rgb_row(); l.addWidget(self._rgb_frame)
        # Sliders
        g = QGridLayout(); g.setSpacing(4)
        sliders = [
            ("最小宽度", "h_minw", 2, 100, 40),
            ("引脚宽度", "h_pinw", 0, 100, 0),
            ("投影阈值", "h_proj", 0, 255, 120),
            ("差值阈值", "h_diff", 0, 255, 180),
        ]
        self._sliders = {}
        for r,(lb,key,lo,hi,dv) in enumerate(sliders):
            g.addWidget(QLabel(lb), r, 0)
            s = QSlider(Qt.Horizontal); s.setRange(lo, hi); s.setValue(dv); s.setPageStep(10)
            g.addWidget(s, r, 1)
            sp = QSpinBox(); sp.setRange(lo, hi); sp.setValue(dv)
            g.addWidget(sp, r, 2)
            s.valueChanged.connect(lambda v, sb=sp: (sb.blockSignals(True), sb.setValue(v), sb.blockSignals(False)))
            sp.valueChanged.connect(lambda v, sl=s: (sl.blockSignals(True), sl.setValue(v), sl.blockSignals(False)))
            self._sliders[key] = sp
        l.addLayout(g)
        # Range sliders R/G/B/Light
        rg = QGroupBox("RGB 范围")
        rg_grid = QGridLayout(rg); rg_grid.setSpacing(4)
        for r,(lb,lo,hi) in enumerate([("R",0,180),("G",0,180),("B",0,180),("Light",0,255)]):
            rg_grid.addWidget(QLabel(lb),r,0)
            slo=QSpinBox(); slo.setRange(lo,hi); slo.setValue(lo); rg_grid.addWidget(slo,r,1)
            shi=QSpinBox(); shi.setRange(lo,hi); shi.setValue(hi); rg_grid.addWidget(shi,r,2)
        l.addWidget(rg)
        # Bottom
        br = QHBoxLayout()
        self._cb_auto = QCheckBox("允许自动计算"); self._cb_auto.setChecked(True); br.addWidget(self._cb_auto)
        self._board_cb = QComboBox(); self._board_cb.addItems(["黑/绿板","白板"]); br.addWidget(self._board_cb)
        br.addStretch(); l.addLayout(br)

    def _make_rgb_row(self):
        f=QFrame(); f.setStyleSheet("background:#1c2128; border-radius:4px;")
        rl=QHBoxLayout(f); rl.setContentsMargins(6,4,6,4)
        self._cb_r=QCheckBox("R红"); self._cb_r.setChecked(True); rl.addWidget(self._cb_r)
        self._cb_g=QCheckBox("G绿"); self._cb_g.setChecked(True); rl.addWidget(self._cb_g)
        self._cb_b=QCheckBox("B蓝"); self._cb_b.setChecked(True); rl.addWidget(self._cb_b)
        sep=QFrame(); sep.setFrameShape(QFrame.VLine); sep.setStyleSheet("color:#30363d;"); rl.addWidget(sep)
        self._cmb_mode=QComboBox(); self._cmb_mode.addItems(["彩色","平均","最大"]); rl.addWidget(self._cmb_mode)
        return f

    def load_params(self, p: dict):
        try:
            self._sliders["h_minw"].setValue(int(p.get("Mini_Width",40)))
            self._sliders["h_pinw"].setValue(int(p.get("Pin_Width",0)))
            self._sliders["h_proj"].setValue(int(p.get("Project_Threshold",120)))
            self._sliders["h_diff"].setValue(int(p.get("Diff_Threshold",180)))
            self._cb_auto.setChecked(p.get("Allow_Auto_Calculate",1))
            self._board_cb.setCurrentIndex(p.get("Board_Color",0))
        except: pass

    def collect_values(self) -> dict:
        return {
            "Mini_Width": self._sliders["h_minw"].value(),
            "Pin_Width": self._sliders["h_pinw"].value(),
            "Project_Threshold": self._sliders["h_proj"].value(),
            "Diff_Threshold": self._sliders["h_diff"].value(),
            "Allow_Auto_Calculate": 1 if self._cb_auto.isChecked() else 0,
            "Board_Color": self._board_cb.currentIndex(),
        }
