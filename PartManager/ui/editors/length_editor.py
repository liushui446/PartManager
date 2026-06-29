from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QSlider, QSpinBox, QCheckBox, QComboBox, QRadioButton,
    QPushButton, QButtonGroup, QFrame
)
from PySide6.QtCore import Qt


class LengthEditor(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # ═══ 1. 测距方式 ═══
        mode_layout = QHBoxLayout()
        self._bg_mode = QButtonGroup(self)
        self._rb_inner = QRadioButton("内距")
        self._rb_inner.setChecked(True)
        self._rb_outer = QRadioButton("外距")
        self._bg_mode.addButton(self._rb_inner, 0)
        self._bg_mode.addButton(self._rb_outer, 1)

        mode_layout.addWidget(QLabel("测距方式"))
        mode_layout.addWidget(self._rb_inner)
        mode_layout.addWidget(self._rb_outer)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # ═══ 2. 颜色通道行 ═══
        color_layout = QHBoxLayout()
        self._cb_r = QCheckBox("红")
        self._cb_r.setChecked(True)
        self._cb_g = QCheckBox("绿")
        self._cb_g.setChecked(True)
        self._cb_b = QCheckBox("蓝")
        self._cb_b.setChecked(False)  # 截图中蓝色未勾选

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFrameShadow(QFrame.Sunken)

        self._cmb_mode = QComboBox()
        self._cmb_mode.addItems(["平均", "最大", "最小"])

        color_layout.addWidget(self._cb_r)
        color_layout.addWidget(self._cb_g)
        color_layout.addWidget(self._cb_b)
        color_layout.addWidget(sep)
        color_layout.addWidget(self._cmb_mode)
        color_layout.addStretch()
        layout.addLayout(color_layout)

        # ═══ 3. 亮度与对比度 ═══
        adjust_layout = QGridLayout()
        adjust_layout.setSpacing(8)

        # 亮度
        adjust_layout.addWidget(QLabel("亮度"), 0, 0)
        self._sl_bright = QSlider(Qt.Horizontal)
        self._sl_bright.setRange(0, 255)
        self._sl_bright.setValue(0)
        adjust_layout.addWidget(self._sl_bright, 0, 1)
        self._sb_bright = QSpinBox()
        self._sb_bright.setRange(0, 255)
        self._sb_bright.setValue(0)
        adjust_layout.addWidget(self._sb_bright, 0, 2)
        # 绑定亮度滑块与微调框
        self._sl_bright.valueChanged.connect(lambda v, sb=self._sb_bright: (sb.blockSignals(True), sb.setValue(v), sb.blockSignals(False)))
        self._sb_bright.valueChanged.connect(lambda v, sl=self._sl_bright: (sl.blockSignals(True), sl.setValue(v), sl.blockSignals(False)))

        # 对比度
        adjust_layout.addWidget(QLabel("对比度"), 1, 0)
        self._sl_contrast = QSlider(Qt.Horizontal)
        self._sl_contrast.setRange(0, 100)
        self._sl_contrast.setValue(2)
        adjust_layout.addWidget(self._sl_contrast, 1, 1)
        self._sb_contrast = QSpinBox()
        self._sb_contrast.setRange(0, 100)
        self._sb_contrast.setValue(2)
        self._sb_contrast.setSuffix(" %")
        adjust_layout.addWidget(self._sb_contrast, 1, 2)
        # 绑定对比度滑块与微调框
        self._sl_contrast.valueChanged.connect(lambda v, sb=self._sb_contrast: (sb.blockSignals(True), sb.setValue(v), sb.blockSignals(False)))
        self._sb_contrast.valueChanged.connect(lambda v, sl=self._sl_contrast: (sl.blockSignals(True), sl.setValue(v), sl.blockSignals(False)))

        layout.addLayout(adjust_layout)

        # ═══ 4. 亮度阈值与投影阈值 ═══
        thresh_layout = QGridLayout()
        thresh_layout.setSpacing(12)
        
        thresh_layout.addWidget(QLabel("亮度阈值"), 0, 0)
        self._sb_bright_thresh = QSpinBox()
        self._sb_bright_thresh.setRange(0, 255)
        self._sb_bright_thresh.setValue(0)
        thresh_layout.addWidget(self._sb_bright_thresh, 0, 1)

        thresh_layout.addWidget(QLabel("投影阈值"), 0, 2)
        self._sb_proj_thresh = QSpinBox()
        self._sb_proj_thresh.setRange(0, 255)
        self._sb_proj_thresh.setValue(0)
        thresh_layout.addWidget(self._sb_proj_thresh, 0, 3)
        
        thresh_layout.setColumnStretch(1, 1)
        thresh_layout.setColumnStretch(3, 1)
        layout.addLayout(thresh_layout)

        # ═══ 5. 标准长度与获取按钮 ═══
        std_layout = QHBoxLayout()
        std_layout.addWidget(QLabel("标准长度"))
        self._sb_std_len = QSpinBox()
        self._sb_std_len.setRange(0, 99999)
        self._sb_std_len.setValue(0)
        std_layout.addWidget(self._sb_std_len)
        std_layout.addSpacing(10)
        
        self._btn_acquire = QPushButton("获取")
        std_layout.addWidget(self._btn_acquire)
        std_layout.addStretch()
        layout.addLayout(std_layout)
        layout.addStretch()

    # ==========================================
    # 数据加载与收集
    # ==========================================
    def load_params(self, p: dict):
        try:
            # 测距方式
            mode = int(p.get("Measure_Mode", 0))
            if mode == 0: self._rb_inner.setChecked(True)
            else: self._rb_outer.setChecked(True)

            # 通道
            self._cb_r.setChecked(bool(p.get("Check_R", 1)))
            self._cb_g.setChecked(bool(p.get("Check_G", 1)))
            self._cb_b.setChecked(bool(p.get("Check_B", 0)))

            # 色彩模式
            self._cmb_mode.setCurrentText(p.get("Color_Mode", "平均"))

            # 亮度 / 对比度
            self._sb_bright.setValue(int(p.get("Brightness", 0)))
            self._sb_contrast.setValue(int(p.get("Contrast", 2)))

            # 阈值
            self._sb_bright_thresh.setValue(int(p.get("Bright_Threshold", 0)))
            self._sb_proj_thresh.setValue(int(p.get("Project_Threshold", 0)))

            # 标准长度
            self._sb_std_len.setValue(int(p.get("Standard_Length", 0)))
        except Exception:
            pass

    def collect_values(self) -> dict:
        return {
            "Measure_Mode": self._bg_mode.checkedId(),
            "Check_R": 1 if self._cb_r.isChecked() else 0,
            "Check_G": 1 if self._cb_g.isChecked() else 0,
            "Check_B": 1 if self._cb_b.isChecked() else 0,
            "Color_Mode": self._cmb_mode.currentText(),
            "Brightness": self._sb_bright.value(),
            "Contrast": self._sb_contrast.value(),
            "Bright_Threshold": self._sb_bright_thresh.value(),
            "Project_Threshold": self._sb_proj_thresh.value(),
            "Standard_Length": self._sb_std_len.value(),
        }