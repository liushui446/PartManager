"""Short 短路检测 — 参考 short.ui"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QSlider, QSpinBox, QCheckBox, QComboBox, QRadioButton,
    QFrame, QButtonGroup
)
from PySide6.QtCore import Qt


class ShortEditor(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # ═══ 1. 顶部模式栏 (投影/抽色/观察) ═══
        mode_layout = QHBoxLayout()
        self._bg_mode = QButtonGroup(self)
        self._rb_proj = QRadioButton("投影")
        self._rb_proj.setChecked(True)
        self._rb_color = QRadioButton("抽色")
        self._cb_watch = QCheckBox("观察")
        self._cb_watch.setChecked(True)

        self._bg_mode.addButton(self._rb_proj)
        self._bg_mode.addButton(self._rb_color)
        mode_layout.addWidget(self._rb_proj)
        mode_layout.addWidget(self._rb_color)
        mode_layout.addWidget(self._cb_watch)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # ═══ 2. 颜色通道行 (RGB 勾选框 + 下拉菜单) ═══
        color_layout = QHBoxLayout()
        self._cb_r = QCheckBox("红")
        self._cb_r.setChecked(True)
        self._cb_g = QCheckBox("绿")
        self._cb_g.setChecked(True)
        self._cb_b = QCheckBox("蓝")
        self._cb_b.setChecked(True)

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFrameShadow(QFrame.Sunken)
        
        self._cmb_color_mode = QComboBox()
        self._cmb_color_mode.addItems(["彩色", "灰度", "二值"])

        color_layout.addWidget(self._cb_r)
        color_layout.addWidget(self._cb_g)
        color_layout.addWidget(self._cb_b)
        color_layout.addWidget(sep)
        color_layout.addWidget(self._cmb_color_mode)
        color_layout.addStretch()
        layout.addLayout(color_layout)

        # ═══ 3. 四个参数滑块 ═══
        slider_layout = QGridLayout()
        slider_layout.setSpacing(8)
        slider_params = [
            ("最小宽度", "h_minw", 1, 100, 9),
            ("引脚宽度", "h_pinw", 1, 100, 9),
            ("投影阈值", "h_proj", 0, 255, 72),
            ("差异阈值", "h_diff", 0, 255, 14),
        ]
        self._sliders = {}
        for r, (lb, key, lo, hi, dv) in enumerate(slider_params):
            slider_layout.addWidget(QLabel(lb), r, 0)
            sl = QSlider(Qt.Horizontal)
            sl.setRange(lo, hi)
            sl.setValue(dv)
            sl.setPageStep(10)
            slider_layout.addWidget(sl, r, 1)

            sp = QSpinBox()
            sp.setRange(lo, hi)
            sp.setValue(dv)
            slider_layout.addWidget(sp, r, 2)

            # 双向绑定
            sl.valueChanged.connect(lambda v, sb=sp: (sb.blockSignals(True), sb.setValue(v), sb.blockSignals(False)))
            sp.valueChanged.connect(lambda v, sl_obj=sl: (sl_obj.blockSignals(True), sl_obj.setValue(v), sl_obj.blockSignals(False)))
            self._sliders[key] = sp
        layout.addLayout(slider_layout)

        # ═══ 4. 四个范围条带 (左微调 - 滑块 - 右微调) ═══
        range_layout = QGridLayout()
        range_layout.setSpacing(4)
        # 默认左侧值：180,180,180,255 ；右侧值：0,0,0,0
        self._range_controls = []
        default_lefts = [180, 180, 180, 255]
        default_rights = [0, 0, 0, 0]
        
        for i in range(4):
            sb_l = QSpinBox()
            sb_l.setRange(0, 255)
            sb_l.setValue(default_lefts[i])
            sl = QSlider(Qt.Horizontal)
            sl.setRange(0, 255)
            sl.setValue(default_lefts[i])  # 滑块默认与左侧绑定
            sb_r = QSpinBox()
            sb_r.setRange(0, 255)
            sb_r.setValue(default_rights[i])

            range_layout.addWidget(sb_l, i, 0)
            range_layout.addWidget(sl, i, 1)
            range_layout.addWidget(sb_r, i, 2)

            # 双向绑定滑块与左侧微调框
            sl.valueChanged.connect(lambda v, sb=sb_l: (sb.blockSignals(True), sb.setValue(v), sb.blockSignals(False)))
            sb_l.valueChanged.connect(lambda v, sl_obj=sl: (sl_obj.blockSignals(True), sl_obj.setValue(v), sl_obj.blockSignals(False)))

            self._range_controls.append({"left": sb_l, "slider": sl, "right": sb_r})
        layout.addLayout(range_layout)

        # ═══ 5. 底部配置与统计信息 ═══
        bottom_layout = QVBoxLayout()
        # 第一行：允许自动计算 + 板子颜色
        config_row = QHBoxLayout()
        self._cb_auto = QCheckBox("允许自动计算")
        self._cb_auto.setChecked(True)
        self._board_cb = QComboBox()
        self._board_cb.addItems(["黑/绿板", "白板"])
        config_row.addWidget(self._cb_auto)
        config_row.addStretch()
        config_row.addWidget(self._board_cb)
        bottom_layout.addLayout(config_row)

        # 第二行：统计显示
        stats_row = QHBoxLayout()
        self._lbl_avg_bright = QLabel("平均亮度：94")
        self._lbl_pin_gap = QLabel("引脚间隔数：6")
        self._lbl_straight_lines = QLabel("直通线数：6")
        stats_row.addWidget(self._lbl_avg_bright)
        stats_row.addStretch()
        stats_row.addWidget(self._lbl_pin_gap)
        stats_row.addStretch()
        stats_row.addWidget(self._lbl_straight_lines)
        bottom_layout.addLayout(stats_row)

        layout.addLayout(bottom_layout)

    # ==========================================
    # 数据加载与收集
    # ==========================================
    def load_params(self, p: dict):
        try:
            self._sliders["h_minw"].setValue(int(p.get("Mini_Width", 9)))
            self._sliders["h_pinw"].setValue(int(p.get("Pin_Width", 9)))
            self._sliders["h_proj"].setValue(int(p.get("Project_Threshold", 72)))
            self._sliders["h_diff"].setValue(int(p.get("Diff_Threshold", 14)))
            
            # 加载范围条数据
            for i, ctrl in enumerate(self._range_controls):
                ctrl["left"].setValue(int(p.get(f"Range_L{i}", [180,180,180,255][i])))
                ctrl["right"].setValue(int(p.get(f"Range_R{i}", [0,0,0,0][i])))

            self._cb_auto.setChecked(bool(p.get("Allow_Auto_Calculate", 1)))
            self._board_cb.setCurrentIndex(int(p.get("Board_Color", 0)))

            # 加载统计信息（如果提供了则更新）
            self._lbl_avg_bright.setText(f"平均亮度：{p.get('Avg_Brightness', 94)}")
            self._lbl_pin_gap.setText(f"引脚间隔数：{p.get('Pin_Gap', 6)}")
            self._lbl_straight_lines.setText(f"直通线数：{p.get('Straight_Lines', 6)}")
        except Exception:
            pass

    def collect_values(self) -> dict:
        values = {
            "Mini_Width": self._sliders["h_minw"].value(),
            "Pin_Width": self._sliders["h_pinw"].value(),
            "Project_Threshold": self._sliders["h_proj"].value(),
            "Diff_Threshold": self._sliders["h_diff"].value(),
            "Allow_Auto_Calculate": 1 if self._cb_auto.isChecked() else 0,
            "Board_Color": self._board_cb.currentIndex(),
            "Color_Mode": self._cmb_color_mode.currentText(),
            "Check_R": 1 if self._cb_r.isChecked() else 0,
            "Check_G": 1 if self._cb_g.isChecked() else 0,
            "Check_B": 1 if self._cb_b.isChecked() else 0,
        }
        # 收集范围条数据
        for i, ctrl in enumerate(self._range_controls):
            values[f"Range_L{i}"] = ctrl["left"].value()
            values[f"Range_R{i}"] = ctrl["right"].value()
        return values

    # ==========================================
    # 辅助：更新统计信息 (供外部调用)
    # ==========================================
    def update_stats(self, avg_brightness, pin_gap, straight_lines):
        self._lbl_avg_bright.setText(f"平均亮度：{avg_brightness}")
        self._lbl_pin_gap.setText(f"引脚间隔数：{pin_gap}")
        self._lbl_straight_lines.setText(f"直通线数：{straight_lines}")