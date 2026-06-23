"""OCV 字符检测 — 参考 OcvAlgorithmDialog.ui"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QSlider, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox,
    QRadioButton, QFrame, QButtonGroup)
from PySide6.QtCore import Qt

class OcvEditor(QWidget):
    def __init__(self): super().__init__(); self._init_ui()
    def _init_ui(self):
        l = QVBoxLayout(self); l.setSpacing(6)
        # RGB row
        f=QFrame(); f.setStyleSheet("background:#1c2128; border-radius:4px;")
        rl=QHBoxLayout(f); rl.setContentsMargins(6,4,6,4)
        self._cb_r=QCheckBox("R红"); self._cb_r.setChecked(True); rl.addWidget(self._cb_r)
        self._cb_g=QCheckBox("G绿"); self._cb_g.setChecked(True); rl.addWidget(self._cb_g)
        self._cb_b=QCheckBox("B蓝"); rl.addWidget(self._cb_b)
        sep=QFrame(); sep.setFrameShape(QFrame.VLine); sep.setStyleSheet("color:#30363d;"); rl.addWidget(sep)
        self._cmb_mode=QComboBox(); self._cmb_mode.addItems(["彩色","平均","最大"]); rl.addWidget(self._cmb_mode)
        l.addWidget(f)
        # Algorithm + Mode
        hr=QHBoxLayout()
        alg_g=QGroupBox("算法选择"); ag=QHBoxLayout(alg_g)
        self._rb_ocv=QRadioButton("OCV"); self._rb_ocv.setChecked(True); ag.addWidget(self._rb_ocv)
        self._rb_ocr=QRadioButton("OCR"); ag.addWidget(self._rb_ocr)
        hr.addWidget(alg_g)
        mode_g=QGroupBox("模式"); mg=QHBoxLayout(mode_g)
        self._blur_group=QButtonGroup(self)
        for i,t in enumerate(["模糊1","模糊2","模糊3","模糊4"]):
            rb=QRadioButton(t); mg.addWidget(rb); self._blur_group.addButton(rb,i)
            if i==0: rb.setChecked(True)
        hr.addWidget(mode_g)
        l.addLayout(hr)
        # Sliders
        g=QGridLayout(); g.setSpacing(4)
        sliders=[
            ("亮度","h_light",-128,128,18,0),
            ("对比度","h_ctrs",0,200,50,100),
            ("二值化阈值","h_range",0,255,20,0),
            ("字符面积阈值","h_size",0,200,10,0),
            ("字符差异阈值","h_differ",0,100,10,0),
        ]
        self._sliders={}
        for r,(lb,key,lo,hi,dv,unit) in enumerate(sliders):
            g.addWidget(QLabel(lb),r,0)
            s=QSlider(Qt.Horizontal); s.setRange(lo,hi); s.setValue(dv); s.setPageStep(10); g.addWidget(s,r,1)
            sp=QSpinBox(); sp.setRange(lo,hi); sp.setValue(dv); g.addWidget(sp,r,2)
            if unit: g.addWidget(QLabel("%" if unit==100 else ""),r,3)
            s.valueChanged.connect(lambda v,sb=sp:(sb.blockSignals(True),sb.setValue(v),sb.blockSignals(False)))
            sp.valueChanged.connect(lambda v,sl=s:(sl.blockSignals(True),sl.setValue(v),sl.blockSignals(False)))
            self._sliders[key]=sp
        l.addLayout(g)
        # Bottom options
        br=QHBoxLayout()
        self._cb_polar=QCheckBox("极性"); br.addWidget(self._cb_polar)
        self._cb_rotate=QCheckBox("图像旋转"); br.addWidget(self._cb_rotate)
        self._cb_fast=QCheckBox("快速匹配"); self._cb_fast.setChecked(True); br.addWidget(self._cb_fast)
        br.addStretch(); l.addLayout(br)
        l.addStretch()

    def load_params(self, p: dict):
        try:
            self._sliders["h_light"].setValue(int(p.get("Brightness",18)))
            self._sliders["h_ctrs"].setValue(int(p.get("Contrast",50)))
            self._sliders["h_range"].setValue(int(p.get("Binary_Threshold",20)))
            self._cb_polar.setChecked(p.get("Polarity",0))
            self._rb_ocv.setChecked(p.get("Img_Type",0)==0)
            self._rb_ocr.setChecked(p.get("Img_Type",0)!=0)
        except: pass

    def collect_values(self) -> dict:
        return {
            "Brightness": self._sliders["h_light"].value(),
            "Contrast": self._sliders["h_ctrs"].value(),
            "Binary_Threshold": self._sliders["h_range"].value(),
            "Polarity": 1 if self._cb_polar.isChecked() else 0,
            "Img_Type": 0 if self._rb_ocv.isChecked() else 1,
        }
