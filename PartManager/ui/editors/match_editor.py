"""Match 模板匹配 — 参考 matchAlgorithmDialog.ui"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QSlider, QSpinBox, QDoubleSpinBox, QCheckBox,
    QComboBox, QRadioButton, QFrame, QLineEdit)
from PySide6.QtCore import Qt

class MatchEditor(QWidget):
    def __init__(self): super().__init__(); self._init_ui()
    def _init_ui(self):
        l = QVBoxLayout(self); l.setSpacing(6)
        # RGB row
        f=QFrame(); f.setStyleSheet("background:#1c2128; border-radius:4px;")
        rl=QHBoxLayout(f); rl.setContentsMargins(6,4,6,4)
        self._cb_r=QCheckBox("R红"); self._cb_r.setChecked(True); rl.addWidget(self._cb_r)
        self._cb_g=QCheckBox("G绿"); self._cb_g.setChecked(True); rl.addWidget(self._cb_g)
        self._cb_b=QCheckBox("B蓝"); self._cb_b.setChecked(True); rl.addWidget(self._cb_b)
        sep=QFrame(); sep.setFrameShape(QFrame.VLine); sep.setStyleSheet("color:#30363d;"); rl.addWidget(sep)
        self._cmb=QComboBox(); self._cmb.addItems(["彩色","平均","最大"]); rl.addWidget(self._cmb)
        l.addWidget(f)
        # Offset
        orw=QHBoxLayout(); orw.addWidget(QLabel("允许偏移X:"))
        self._offx=QLineEdit("0.5"); orw.addWidget(self._offx); orw.addWidget(QLabel("Y:"))
        self._offy=QLineEdit("0.5"); orw.addWidget(self._offy); orw.addWidget(QLabel("角度:"))
        self._offa=QLineEdit("6"); orw.addWidget(self._offa); l.addLayout(orw)
        # Enhance + Gray
        hr=QHBoxLayout(); hr.addWidget(QLabel("增强:"))
        self._enh=QSpinBox(); self._enh.setRange(0,10); self._enh.setValue(1); hr.addWidget(self._enh)
        hr.addStretch(); hr.addWidget(QLabel("灰度:"))
        self._gray=QSpinBox(); self._gray.setRange(0,1000); self._gray.setValue(297); hr.addWidget(self._gray)
        l.addLayout(hr)
        # Sliders
        g=QGridLayout(); g.setSpacing(4)
        sliders=[("亮度","h_light",-128,128,0),("对比度","h_ctrs",2,200,100),("相似度","h_sim",0,100,40)]
        self._sliders={}
        for r,(lb,key,lo,hi,dv) in enumerate(sliders):
            g.addWidget(QLabel(lb),r,0)
            s=QSlider(Qt.Horizontal); s.setRange(lo,hi); s.setValue(dv); s.setPageStep(10); g.addWidget(s,r,1)
            sp=QSpinBox(); sp.setRange(lo,hi); sp.setValue(dv); g.addWidget(sp,r,2)
            s.valueChanged.connect(lambda v,sb=sp:(sb.blockSignals(True),sb.setValue(v),sb.blockSignals(False)))
            sp.valueChanged.connect(lambda v,sl=s:(sl.blockSignals(True),sl.setValue(v),sl.blockSignals(False)))
            self._sliders[key]=sp
        l.addLayout(g)
        # Correction mode
        cg=QGroupBox("校正方式"); cl=QHBoxLayout(cg)
        self._rb_img=QRadioButton("图像"); self._rb_img.setChecked(True); cl.addWidget(self._rb_img)
        self._rb_grav=QRadioButton("重心"); cl.addWidget(self._rb_grav)
        self._rb_ellip=QRadioButton("椭圆"); cl.addWidget(self._rb_ellip)
        self._rb_rect=QRadioButton("矩形"); cl.addWidget(self._rb_rect); l.addWidget(cg)
        # Bottom
        br=QHBoxLayout()
        self._cb_polar=QCheckBox("极性"); br.addWidget(self._cb_polar)
        self._cb_shield=QCheckBox("屏蔽框"); br.addWidget(self._cb_shield); br.addStretch(); l.addLayout(br)
        l.addStretch()

    def load_params(self, p: dict):
        try:
            self._sliders["h_light"].setValue(int(p.get("Brightness",0)))
            self._sliders["h_ctrs"].setValue(int(p.get("Contrast",100)))
            self._enh.setValue(int(p.get("Enhance",1)))
            self._gray.setValue(int(p.get("Gray",297)))
            self._offx.setText(str(p.get("Search_Scope_X","0.5")))
            self._offy.setText(str(p.get("Search_Scope_Y","0.5")))
            self._offa.setText(str(p.get("Search_Scope_Angle","6")))
        except: pass

    def collect_values(self) -> dict:
        return {
            "Brightness": self._sliders["h_light"].value(),
            "Contrast": self._sliders["h_ctrs"].value(),
            "Enhance": self._enh.value(), "Gray": self._gray.value(),
            "Search_Scope_X": float(self._offx.text() or 0.5),
            "Search_Scope_Y": float(self._offy.text() or 0.5),
            "Search_Scope_Angle": float(self._offa.text() or 6),
        }
