"""Other 其他缺陷检测 — 参考 other_faulty.ui"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QSlider, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QFrame)
from PySide6.QtCore import Qt

class OtherEditor(QWidget):
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
        # Enhance + model type
        hr=QHBoxLayout(); hr.addWidget(QLabel("增强:"))
        self._enh=QSpinBox(); self._enh.setRange(0,10); self._enh.setValue(1); hr.addWidget(self._enh)
        hr.addStretch(); hr.addWidget(QLabel("图像类型:"))
        self._model=QComboBox(); self._model.addItems(["HSV","GRAY","H","S","V"]); hr.addWidget(self._model)
        l.addLayout(hr)
        # Brightness + Contrast sliders
        g=QGridLayout(); g.setSpacing(4)
        sliders=[("亮度","h_light",-128,128,0),("对比度","h_ctrs",2,1100,100)]
        self._sliders={}
        for r,(lb,key,lo,hi,dv) in enumerate(sliders):
            g.addWidget(QLabel(lb),r,0)
            s=QSlider(Qt.Horizontal); s.setRange(lo,hi); s.setValue(dv); s.setPageStep(10); g.addWidget(s,r,1)
            sp=QSpinBox(); sp.setRange(lo,hi); sp.setValue(dv); g.addWidget(sp,r,2)
            s.valueChanged.connect(lambda v,sb=sp:(sb.blockSignals(True),sb.setValue(v),sb.blockSignals(False)))
            sp.valueChanged.connect(lambda v,sl=s:(sl.blockSignals(True),sl.setValue(v),sl.blockSignals(False)))
            self._sliders[key]=sp
        l.addLayout(g)
        # Detection params
        g2=QGridLayout(); g2.setSpacing(4)
        params=[("检测长度","len",0,100,50),("最小错误面积","area",0,9999,25),
                ("错误像素%","err",0,100,20),("差异阈值%","diff",0,100,50),
                ("方差比例%","var",0,100,25)]
        self._params={}
        for r,(lb,key,lo,hi,dv) in enumerate(params):
            g2.addWidget(QLabel(lb),r//3*2,r%3*2)
            sp=QSpinBox(); sp.setRange(lo,hi); sp.setValue(dv); g2.addWidget(sp,r//3*2,r%3*2+1)
            self._params[key]=sp
        l.addLayout(g2)
        self._cb_auto=QCheckBox("允许自动学习"); self._cb_auto.setChecked(True); l.addWidget(self._cb_auto)
        l.addStretch()

    def load_params(self, p: dict):
        try:
            self._sliders["h_light"].setValue(int(p.get("Brightness",0)))
            self._sliders["h_ctrs"].setValue(int(p.get("Contrast",100)))
            self._enh.setValue(int(p.get("Enhance",1)))
            self._params["len"].setValue(int(p.get("Det_Length",50)))
            self._params["area"].setValue(int(p.get("M_Least_Error_Area",25)))
            self._params["err"].setValue(int(p.get("M_Errorpixelnum_Factor",20)))
            self._params["diff"].setValue(int(p.get("Diff_Thre",50)))
            self._params["var"].setValue(int(p.get("M_Init_Var_Ratio",25)))
        except: pass

    def collect_values(self) -> dict:
        return {
            "Brightness": self._sliders["h_light"].value(),
            "Contrast": self._sliders["h_ctrs"].value(),
            "Enhance": self._enh.value(),
            "Det_Length": self._params["len"].value(),
            "M_Least_Error_Area": self._params["area"].value(),
            "M_Errorpixelnum_Factor": self._params["err"].value(),
            "Diff_Thre": self._params["diff"].value(),
            "M_Init_Var_Ratio": self._params["var"].value(),
        }
