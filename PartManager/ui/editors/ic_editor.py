"""IC 算法参数编辑器 — 参考 IC 界面截图"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QSlider, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox
)
from PySide6.QtCore import Qt


class IcEditor(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # ═══ 1. 基本参数 ═══
        basic_group = QGroupBox("基本参数")
        basic_grid = QGridLayout(basic_group)
        basic_grid.setSpacing(6)

        # 引脚方位 & 角度
        basic_grid.addWidget(QLabel("引脚方位"), 0, 0)
        self.cb_pin_dir = QComboBox()
        self.cb_pin_dir.addItems(["上", "下", "左", "右"])
        basic_grid.addWidget(self.cb_pin_dir, 0, 1)

        basic_grid.addWidget(QLabel("角度"), 0, 2)
        self.sb_angle = QSpinBox()
        self.sb_angle.setRange(0, 360)
        basic_grid.addWidget(self.sb_angle, 0, 3)

        # 板子颜色 & 脚长比例
        basic_grid.addWidget(QLabel("板子颜色"), 1, 0)
        self.cb_board_color = QComboBox()
        self.cb_board_color.addItems(["绿板", "红板", "蓝板"])
        basic_grid.addWidget(self.cb_board_color, 1, 1)

        basic_grid.addWidget(QLabel("脚长比例"), 1, 2)
        ratio_layout = QHBoxLayout()
        ratio_layout.setContentsMargins(0, 0, 0, 0)
        self.sb_leg_ratio = QSpinBox()
        self.sb_leg_ratio.setRange(0, 100)
        ratio_layout.addWidget(self.sb_leg_ratio)
        ratio_layout.addWidget(QLabel("%"))
        basic_grid.addLayout(ratio_layout, 1, 3)

        layout.addWidget(basic_group)

        # ═══ 2. 定位框参数 ═══
        loc_group = QGroupBox("定位框参数")
        loc_grid = QGridLayout(loc_group)
        loc_grid.setSpacing(6)

        loc_grid.addWidget(QLabel("引脚数"), 0, 0)
        self.sb_pin_num = QSpinBox()
        self.sb_pin_num.setRange(0, 999)
        loc_grid.addWidget(self.sb_pin_num, 0, 1)

        loc_grid.addWidget(QLabel("脚长"), 0, 2)
        self.sb_leg_len = QDoubleSpinBox()
        self.sb_leg_len.setRange(0.0, 999.0)
        self.sb_leg_len.setDecimals(2)
        loc_grid.addWidget(self.sb_leg_len, 0, 3)

        loc_grid.addWidget(QLabel("脚间距"), 1, 0)
        self.sb_leg_pitch = QDoubleSpinBox()
        self.sb_leg_pitch.setRange(0.0, 999.0)
        self.sb_leg_pitch.setDecimals(2)
        loc_grid.addWidget(self.sb_leg_pitch, 1, 1)

        loc_grid.addWidget(QLabel("脚宽"), 1, 2)
        self.sb_leg_width = QDoubleSpinBox()
        self.sb_leg_width.setRange(0.0, 999.0)
        self.sb_leg_width.setDecimals(2)
        loc_grid.addWidget(self.sb_leg_width, 1, 3)

        layout.addWidget(loc_group)

        # ═══ 3. ROI 区域 ═══
        roi_group = QGroupBox("ROI区域")
        roi_grid = QGridLayout(roi_group)
        roi_grid.setSpacing(6)

        # 上边界
        roi_grid.addWidget(QLabel("上边界"), 0, 0)
        self.sb_upper = QDoubleSpinBox()
        self.sb_upper.setRange(0.0, 999.0)
        self.sb_upper.setValue(33.00)
        self.sb_upper.setDecimals(2)
        roi_grid.addWidget(self.sb_upper, 0, 1)
        self.sl_upper = QSlider(Qt.Horizontal)
        self.sl_upper.setRange(0, 99900)  # 配合两位小数
        self.sl_upper.setValue(3300)
        roi_grid.addWidget(self.sl_upper, 0, 2)

        # 下边界
        roi_grid.addWidget(QLabel("下边界"), 1, 0)
        self.sb_lower = QDoubleSpinBox()
        self.sb_lower.setRange(0.0, 999.0)
        self.sb_lower.setValue(139.00)
        self.sb_lower.setDecimals(2)
        roi_grid.addWidget(self.sb_lower, 1, 1)
        self.sl_lower = QSlider(Qt.Horizontal)
        self.sl_lower.setRange(0, 99900)
        self.sl_lower.setValue(13900)
        roi_grid.addWidget(self.sl_lower, 1, 2)

        # 自动计算
        self.cb_auto_boundary = QCheckBox("自动计算")
        roi_grid.addWidget(self.cb_auto_boundary, 2, 0, 1, 1)

        layout.addWidget(roi_group)

        # ═══ 4. 阈值与高级参数 ═══
        thresh_group = QGroupBox("阈值")
        thresh_grid = QGridLayout(thresh_group)
        thresh_grid.setSpacing(6)

        # 最小宽度
        thresh_grid.addWidget(QLabel("最小宽度"), 0, 0)
        self.sl_min_width = QSlider(Qt.Horizontal)
        self.sl_min_width.setRange(1, 100)
        self.sl_min_width.setValue(1)
        thresh_grid.addWidget(self.sl_min_width, 0, 1)
        self.sb_min_width = QSpinBox()
        self.sb_min_width.setRange(1, 100)
        self.sb_min_width.setValue(1)
        thresh_grid.addWidget(self.sb_min_width, 0, 2)

        # 引脚宽度
        thresh_grid.addWidget(QLabel("引脚宽度"), 1, 0)
        self.sl_pin_width = QSlider(Qt.Horizontal)
        self.sl_pin_width.setRange(1, 100)
        self.sl_pin_width.setValue(1)
        thresh_grid.addWidget(self.sl_pin_width, 1, 1)
        self.sb_pin_width = QSpinBox()
        self.sb_pin_width.setRange(1, 100)
        self.sb_pin_width.setValue(1)
        thresh_grid.addWidget(self.sb_pin_width, 1, 2)

        # 二值阈值
        thresh_grid.addWidget(QLabel("二值阈值"), 2, 0)
        self.sl_bin_thresh = QSlider(Qt.Horizontal)
        self.sl_bin_thresh.setRange(1, 255)
        self.sl_bin_thresh.setValue(1)
        thresh_grid.addWidget(self.sl_bin_thresh, 2, 1)
        self.sb_bin_thresh = QSpinBox()
        self.sb_bin_thresh.setRange(1, 255)
        self.sb_bin_thresh.setValue(1)
        thresh_grid.addWidget(self.sb_bin_thresh, 2, 2)

        # 差异阈值
        thresh_grid.addWidget(QLabel("差异阈值"), 3, 0)
        self.sl_diff_thresh = QSlider(Qt.Horizontal)
        self.sl_diff_thresh.setRange(0, 360)
        self.sl_diff_thresh.setValue(180)
        thresh_grid.addWidget(self.sl_diff_thresh, 3, 1)
        self.sb_diff_thresh = QSpinBox()
        self.sb_diff_thresh.setRange(0, 360)
        self.sb_diff_thresh.setValue(180)
        thresh_grid.addWidget(self.sb_diff_thresh, 3, 2)

        # 自动参数计算 + 间隔数
        auto_layout = QHBoxLayout()
        self.cb_auto_param = QCheckBox("自动参数计算")
        self.cb_auto_param.setChecked(True)
        auto_layout.addWidget(self.cb_auto_param)
        auto_layout.addStretch()
        auto_layout.addWidget(QLabel("间隔数："))
        self.sb_interval = QSpinBox()
        self.sb_interval.setRange(0, 999)
        self.sb_interval.setValue(0)
        auto_layout.addWidget(self.sb_interval)
        thresh_grid.addLayout(auto_layout, 4, 0, 1, 3)

        layout.addWidget(thresh_group)
        layout.addStretch()

        # 连接滑块和输入框的双向同步
        self._connect_slider_spin(self.sl_upper, self.sb_upper, 100.0)
        self._connect_slider_spin(self.sl_lower, self.sb_lower, 100.0)
        self._connect_slider_spin(self.sl_min_width, self.sb_min_width, 1.0)
        self._connect_slider_spin(self.sl_pin_width, self.sb_pin_width, 1.0)
        self._connect_slider_spin(self.sl_bin_thresh, self.sb_bin_thresh, 1.0)
        self._connect_slider_spin(self.sl_diff_thresh, self.sb_diff_thresh, 1.0)

    def _connect_slider_spin(self, slider, spin, factor):
        """滑块与数值框双向绑定（避免死循环）"""
        def on_slider(val):
            spin.blockSignals(True)
            spin.setValue(val / factor)
            spin.blockSignals(False)

        def on_spin(val):
            slider.blockSignals(True)
            slider.setValue(int(val * factor))
            slider.blockSignals(False)

        slider.valueChanged.connect(on_slider)
        spin.valueChanged.connect(on_spin)

    def load_params(self, params: dict):
        try:
            self.cb_pin_dir.setCurrentText(str(params.get("pin_direction", "下")))
            self.sb_angle.setValue(int(params.get("angle", 0)))
            self.cb_board_color.setCurrentText(str(params.get("board_color", "绿板")))
            self.sb_leg_ratio.setValue(int(params.get("leg_ratio", 1)))

            self.sb_pin_num.setValue(int(params.get("pin_num", 0)))
            self.sb_leg_len.setValue(float(params.get("leg_len", 0.0)))
            self.sb_leg_pitch.setValue(float(params.get("leg_pitch", 0.0)))
            self.sb_leg_width.setValue(float(params.get("leg_width", 0.0)))

            self.sb_upper.setValue(float(params.get("Upper_Boundary", 33.00)))
            self.sb_lower.setValue(float(params.get("Lower_Boundary", 139.00)))
            self.cb_auto_boundary.setChecked(bool(params.get("Auto_CalBoundary_Flag", 0)))

            self.sb_min_width.setValue(int(params.get("Min_Width", 1)))
            self.sb_pin_width.setValue(int(params.get("Pin_Width_Threshold", 1)))
            self.sb_bin_thresh.setValue(int(params.get("BinThreshold", 1)))
            self.sb_diff_thresh.setValue(int(params.get("Diff_Threshold", 180)))

            self.cb_auto_param.setChecked(bool(params.get("Auto_Calculate_Flag", 0)))
            self.sb_interval.setValue(int(params.get("Interval_Num", 0)))
        except Exception:
            pass

    def collect_values(self) -> dict:
        return {
            "pin_direction": self.cb_pin_dir.currentText(),
            "angle": self.sb_angle.value(),
            "board_color": self.cb_board_color.currentText(),
            "leg_ratio": self.sb_leg_ratio.value(),
            "pin_num": self.sb_pin_num.value(),
            "leg_len": self.sb_leg_len.value(),
            "leg_pitch": self.sb_leg_pitch.value(),
            "leg_width": self.sb_leg_width.value(),
            "Upper_Boundary": self.sb_upper.value(),
            "Lower_Boundary": self.sb_lower.value(),
            "Auto_CalBoundary_Flag": 1 if self.cb_auto_boundary.isChecked() else 0,
            "Min_Width": self.sb_min_width.value(),
            "Pin_Width_Threshold": self.sb_pin_width.value(),
            "BinThreshold": self.sb_bin_thresh.value(),
            "Diff_Threshold": self.sb_diff_thresh.value(),
            "Auto_Calculate_Flag": 1 if self.cb_auto_param.isChecked() else 0,
            "Interval_Num": self.sb_interval.value(),
        }