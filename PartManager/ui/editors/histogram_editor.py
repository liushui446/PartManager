from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QSpinBox, QComboBox, QCheckBox, QRadioButton, QButtonGroup,
    QFrame
)
from PySide6.QtCore import Qt


class HistogramEditor(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # ═══ 1. 顶部行：颜色通道与统计模式 ═══
        top_layout = QHBoxLayout()
        self._cb_r = QCheckBox("红")
        self._cb_r.setChecked(True)
        self._cb_g = QCheckBox("绿")
        self._cb_g.setChecked(True)
        self._cb_b = QCheckBox("蓝")
        self._cb_b.setChecked(True)

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFrameShadow(QFrame.Sunken)

        self._cmb_hist_mode = QComboBox()
        self._cmb_hist_mode.addItems(["平均", "最大", "最小"])

        top_layout.addWidget(self._cb_r)
        top_layout.addWidget(self._cb_g)
        top_layout.addWidget(self._cb_b)
        top_layout.addWidget(sep)
        top_layout.addWidget(self._cmb_hist_mode)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        # ═══ 2. 中间行：检测模式 ═══
        gb_detect = QGroupBox("检测模式")
        h_detect = QHBoxLayout(gb_detect)
        
        self._bg_detect = QButtonGroup(self)
        self._rb_min = QRadioButton("Min")
        self._rb_max = QRadioButton("Max")
        self._rb_range = QRadioButton("Range")
        self._rb_min.setChecked(True)
        
        self._bg_detect.addButton(self._rb_min, 0)
        self._bg_detect.addButton(self._rb_max, 1)
        self._bg_detect.addButton(self._rb_range, 2)
        
        h_detect.addWidget(self._rb_min)
        h_detect.addWidget(self._rb_max)
        h_detect.addWidget(self._rb_range)
        h_detect.addStretch()
        layout.addWidget(gb_detect)

        # ═══ 3. 底部行：三个微调参数（垂直分布，靠左对齐） ═══
        self._sb_enhance = QSpinBox()
        self._sb_enhance.setRange(0, 999)
        self._sb_enhance.setValue(1)

        self._sb_filter = QSpinBox()
        self._sb_filter.setRange(0, 100)
        self._sb_filter.setValue(1)

        self._sb_ratio = QSpinBox()
        self._sb_ratio.setRange(0, 1000)
        self._sb_ratio.setValue(100)
        self._sb_ratio.setSuffix(" %")

        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(8)

        # 增强
        h_enhance = QHBoxLayout()
        h_enhance.addWidget(QLabel("增强"))
        h_enhance.addWidget(self._sb_enhance)
        h_enhance.addStretch()
        bottom_layout.addLayout(h_enhance)

        # 滤波
        h_filter = QHBoxLayout()
        h_filter.addWidget(QLabel("滤波"))
        h_filter.addWidget(self._sb_filter)
        h_filter.addStretch()
        bottom_layout.addLayout(h_filter)

        # 比率
        h_ratio = QHBoxLayout()
        h_ratio.addWidget(QLabel("比率"))
        h_ratio.addWidget(self._sb_ratio)
        h_ratio.addStretch()
        bottom_layout.addLayout(h_ratio)

        bottom_layout.addStretch()
        layout.addLayout(bottom_layout)
        layout.addStretch()

    # ==========================================
    # 数据加载与收集
    # ==========================================
    def load_params(self, p: dict):
        try:
            self._cb_r.setChecked(bool(p.get("Check_R", 1)))
            self._cb_g.setChecked(bool(p.get("Check_G", 1)))
            self._cb_b.setChecked(bool(p.get("Check_B", 1)))
            self._cmb_hist_mode.setCurrentText(p.get("Hist_Mode", "平均"))

            mode = int(p.get("Detect_Mode", 0))
            if mode == 0: self._rb_min.setChecked(True)
            elif mode == 1: self._rb_max.setChecked(True)
            else: self._rb_range.setChecked(True)

            self._sb_enhance.setValue(int(p.get("Enhance", 1)))
            self._sb_filter.setValue(int(p.get("Filter", 1)))
            self._sb_ratio.setValue(int(p.get("Ratio", 100)))
        except Exception:
            pass

    def collect_values(self) -> dict:
        return {
            "Check_R": 1 if self._cb_r.isChecked() else 0,
            "Check_G": 1 if self._cb_g.isChecked() else 0,
            "Check_B": 1 if self._cb_b.isChecked() else 0,
            "Hist_Mode": self._cmb_hist_mode.currentText(),
            "Detect_Mode": self._bg_detect.checkedId(),
            "Enhance": self._sb_enhance.value(),
            "Filter": self._sb_filter.value(),
            "Ratio": self._sb_ratio.value(),
        }