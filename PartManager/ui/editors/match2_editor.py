"""Match2 二次匹配 — 参考 Match2AlgorithmDialog.ui"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QLineEdit, QCheckBox, QComboBox, QFrame)
from PySide6.QtCore import Qt

class Match2Editor(QWidget):
    def __init__(self): super().__init__(); self._init_ui()
    def _init_ui(self):
        l = QVBoxLayout(self); l.setSpacing(6)
        # Body positioning group
        bg = QGroupBox("本体定位")
        bl = QVBoxLayout(bg); bl.setSpacing(4)
        f=QFrame(); f.setStyleSheet("background:#1c2128; border-radius:4px;")
        rl=QHBoxLayout(f); rl.setContentsMargins(6,4,6,4)
        self._cb_rb=QCheckBox("R红"); self._cb_rb.setChecked(True); rl.addWidget(self._cb_rb)
        self._cb_gb=QCheckBox("G绿"); self._cb_gb.setChecked(True); rl.addWidget(self._cb_gb)
        self._cb_bb=QCheckBox("B蓝"); self._cb_bb.setChecked(True); rl.addWidget(self._cb_bb)
        sep=QFrame(); sep.setFrameShape(QFrame.VLine); sep.setStyleSheet("color:#30363d;"); rl.addWidget(sep)
        self._cmb_body=QComboBox(); self._cmb_body.addItems(["平均","彩色","最大"]); rl.addWidget(self._cmb_body)
        bl.addWidget(f)
        self._cb_body_dual=QCheckBox("本体双定位"); bl.addWidget(self._cb_body_dual)
        l.addWidget(bg)
        # Base positioning group
        bsg = QGroupBox()
        bsl = QVBoxLayout(bsg); bsl.setSpacing(4)
        self._cb_base=QCheckBox("基板定位"); self._cb_base.setChecked(True); bsl.addWidget(self._cb_base)
        f2=QFrame(); f2.setStyleSheet("background:#1c2128; border-radius:4px;")
        rl2=QHBoxLayout(f2); rl2.setContentsMargins(6,4,6,4)
        self._cb_rb2=QCheckBox("R红"); self._cb_rb2.setChecked(True); rl2.addWidget(self._cb_rb2)
        self._cb_gb2=QCheckBox("G绿"); self._cb_gb2.setChecked(True); rl2.addWidget(self._cb_gb2)
        self._cb_bb2=QCheckBox("B蓝"); self._cb_bb2.setChecked(True); rl2.addWidget(self._cb_bb2)
        sep2=QFrame(); sep2.setFrameShape(QFrame.VLine); sep2.setStyleSheet("color:#30363d;"); rl2.addWidget(sep2)
        self._cmb_base=QComboBox(); self._cmb_base.addItems(["平均","彩色","最大"]); rl2.addWidget(self._cmb_base)
        bsl.addWidget(f2)
        hr=QHBoxLayout(); hr.addWidget(QLabel("Dx:"))
        self._dx=QLineEdit("0.50"); hr.addWidget(self._dx); hr.addStretch(); hr.addWidget(QLabel("Dy:"))
        self._dy=QLineEdit("0.50"); hr.addWidget(self._dy); bsl.addLayout(hr)
        hr2=QHBoxLayout()
        self._cb_show=QCheckBox("显示效果"); self._cb_show.setChecked(True); hr2.addWidget(self._cb_show)
        self._cb_shield=QCheckBox("屏蔽本体"); hr2.addWidget(self._cb_shield); hr2.addStretch()
        bsl.addLayout(hr2); l.addWidget(bsg)
        l.addStretch()

    def load_params(self, p: dict):
        try:
            self._dx.setText(str(p.get("Search_Scope_X","0.50")))
            self._dy.setText(str(p.get("Search_Scope_Y","0.50")))
        except: pass

    def collect_values(self) -> dict:
        return {
            "Search_Scope_X": float(self._dx.text() or 0.5),
            "Search_Scope_Y": float(self._dy.text() or 0.5),
        }
