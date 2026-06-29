from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QSlider, QSpinBox, QCheckBox, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt


class CrestEditor(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # ═══ 1. 顶部区域（焊盘极性 + 分析区域 + 焊盘形状）═══
        top_layout = QHBoxLayout()
        top_layout.setSpacing(20)

        # 1.1 焊盘极性
        gb_polar = QGroupBox("焊盘极性")
        v_polar = QVBoxLayout(gb_polar)
        self._bg_polar = QButtonGroup(self)
        self._rb_non_polar = QRadioButton("非极性")
        self._rb_polar = QRadioButton("极性")
        self._rb_undirected = QRadioButton("不定向")
        self._rb_non_polar.setChecked(True)
        self._bg_polar.addButton(self._rb_non_polar, 0)
        self._bg_polar.addButton(self._rb_polar, 1)
        self._bg_polar.addButton(self._rb_undirected, 2)
        v_polar.addWidget(self._rb_non_polar)
        v_polar.addWidget(self._rb_polar)
        v_polar.addWidget(self._rb_undirected)
        top_layout.addWidget(gb_polar)

        # 1.2 极性引脚分析区域
        gb_analysis = QGroupBox("极性引脚分析区域")
        v_analysis = QVBoxLayout(gb_analysis)
        self._cb_inner = QCheckBox("内部分析")
        self._cb_outer = QCheckBox("外部分析")
        v_analysis.addWidget(self._cb_inner)
        v_analysis.addWidget(self._cb_outer)
        top_layout.addWidget(gb_analysis)

        # 1.3 焊盘形状
        gb_shape = QGroupBox("焊盘形状")
        h_shape = QHBoxLayout(gb_shape)
        self._bg_shape = QButtonGroup(self)
        self._rb_oval = QRadioButton("椭圆")
        self._rb_rect = QRadioButton("矩形")
        self._rb_oval.setChecked(True)
        self._bg_shape.addButton(self._rb_oval, 0)
        self._bg_shape.addButton(self._rb_rect, 1)
        h_shape.addWidget(self._rb_oval)
        h_shape.addWidget(self._rb_rect)
        top_layout.addWidget(gb_shape)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        # ═══ 2. 中间区域（焊盘/引脚有效区域百分比）═══
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(15)
        
        self._sb_pad_valid = QSpinBox()
        self._sb_pad_valid.setRange(0, 100)
        self._sb_pad_valid.setValue(100)
        self._sb_pad_valid.setSuffix(" %")
        mid_layout.addWidget(QLabel("焊盘有效区域"))
        mid_layout.addWidget(self._sb_pad_valid)
        
        mid_layout.addStretch()
        
        self._sb_pin_valid = QSpinBox()
        self._sb_pin_valid.setRange(0, 100)
        self._sb_pin_valid.setValue(75)
        self._sb_pin_valid.setSuffix(" %")
        mid_layout.addWidget(QLabel("引脚有效区域"))
        mid_layout.addWidget(self._sb_pin_valid)
        
        mid_layout.addStretch()
        layout.addLayout(mid_layout)

        # ═══ 3. 定位参数（四行颜色滑块+微调框）═══
        gb_param = QGroupBox("定位参数")
        grid = QGridLayout(gb_param)
        grid.setSpacing(6)

        # (标签名, key值, 默认值, 最小值, 最大值, 滑块样式颜色)
        param_configs = [
            ("蓝色下限", "blue", 60, 0, 255, "#4AA3DF"),
            ("绿色下限", "green", 220, 0, 255, "#6ECC56"),
            ("红色下限", "red", 230, 0, 255, "#E34141"),
            ("亮度上限", "bright", 255, 0, 255, "#9E9E9E"),
        ]
        self._params = {}

        for r, (label, key, val, lo, hi, color) in enumerate(param_configs):
            grid.addWidget(QLabel(label), r, 0)
            
            sl = QSlider(Qt.Horizontal)
            sl.setRange(lo, hi)
            sl.setValue(val)
            # 给滑块槽设置背景色，复刻截图效果
            sl.setStyleSheet(f"""
                QSlider::groove:horizontal {{
                    background: {color};
                    height: 8px;
                    border-radius: 4px;
                }}
            """)
            grid.addWidget(sl, r, 1)

            sp = QSpinBox()
            sp.setRange(lo, hi)
            sp.setValue(val)
            grid.addWidget(sp, r, 2)

            # 双向绑定（避免死循环）
            sl.valueChanged.connect(lambda v, sb=sp: (sb.blockSignals(True), sb.setValue(v), sb.blockSignals(False)))
            sp.valueChanged.connect(lambda v, sl_obj=sl: (sl_obj.blockSignals(True), sl_obj.setValue(v), sl_obj.blockSignals(False)))
            self._params[key] = sp

        layout.addWidget(gb_param)
        layout.addStretch()

    # ==========================================
    # 数据加载与收集
    # ==========================================
    def load_params(self, p: dict):
        try:
            # 焊盘极性
            polarity = int(p.get("Polarity", 0))
            if polarity == 0: self._rb_non_polar.setChecked(True)
            elif polarity == 1: self._rb_polar.setChecked(True)
            else: self._rb_undirected.setChecked(True)

            # 极性引脚分析区域
            self._cb_inner.setChecked(bool(p.get("Inner_Analysis", 0)))
            self._cb_outer.setChecked(bool(p.get("Outer_Analysis", 0)))

            # 焊盘形状
            shape = int(p.get("Pad_Shape", 0))
            if shape == 0: self._rb_oval.setChecked(True)
            else: self._rb_rect.setChecked(True)

            # 有效区域
            self._sb_pad_valid.setValue(int(p.get("Pad_Valid_Area", 100)))
            self._sb_pin_valid.setValue(int(p.get("Pin_Valid_Area", 75)))

            # 定位参数
            self._params["blue"].setValue(int(p.get("Blue_Lower", 60)))
            self._params["green"].setValue(int(p.get("Green_Lower", 220)))
            self._params["red"].setValue(int(p.get("Red_Lower", 230)))
            self._params["bright"].setValue(int(p.get("Bright_Upper", 255)))
        except Exception:
            pass

    def collect_values(self) -> dict:
        polarity_id = self._bg_polar.checkedId()
        shape_id = self._bg_shape.checkedId()
        return {
            "Polarity": polarity_id if polarity_id != -1 else 0,
            "Inner_Analysis": 1 if self._cb_inner.isChecked() else 0,
            "Outer_Analysis": 1 if self._cb_outer.isChecked() else 0,
            "Pad_Shape": shape_id if shape_id != -1 else 0,
            "Pad_Valid_Area": self._sb_pad_valid.value(),
            "Pin_Valid_Area": self._sb_pin_valid.value(),
            "Blue_Lower": self._params["blue"].value(),
            "Green_Lower": self._params["green"].value(),
            "Red_Lower": self._params["red"].value(),
            "Bright_Upper": self._params["bright"].value(),
        }