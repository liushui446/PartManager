"""
TOC算法参数编辑器 — 参考 TocEmptyAlgorithmDialog 原始UI设计
"""

from typing import Dict, List, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QSlider, QSpinBox, QDoubleSpinBox,
    QPushButton, QFrame, QCheckBox, QComboBox, QStackedWidget
)
from PySide6.QtCore import Qt, Signal, QPoint, QRect
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QPolygon

from ui.range_slider import RangeSlider


# ─── 色度三角形控件 ─────────────────────────────────────────────

class TriangleWidget(QWidget):
    """HSL色度三角形可视化 — 框选范围随RGB参数变化"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(140, 120)
        self.setMaximumHeight(180)
        self._r_lo, self._r_hi = 0, 180
        self._g_lo, self._g_hi = 0, 180
        self._b_lo, self._b_hi = 0, 180

    def SetRedLowValue(self, v): self._r_lo = v; self.update()
    def SetRedHighValue(self, v): self._r_hi = v; self.update()
    def SetGreenLowValue(self, v): self._g_lo = v; self.update()
    def SetGreenHighValue(self, v): self._g_hi = v; self.update()
    def SetBlueLowValue(self, v): self._b_lo = v; self.update()
    def SetBlueHighValue(self, v): self._b_hi = v; self.update()

    def _hue_to_xy(self, h: float, w: int, hgt: int, margin: int,
                    r_pt: QPoint, g_pt: QPoint, b_pt: QPoint) -> QPoint:
        """将色相值(0-180)映射到三角形坐标"""
        # 三角形顶点: R=0/180(顶部), G=60(左下), B=120(右下)
        # 简化: 线性插值
        if h <= 60:
            t = h / 60.0
            x = r_pt.x() + (g_pt.x() - r_pt.x()) * t
            y = r_pt.y() + (g_pt.y() - r_pt.y()) * t
        elif h <= 120:
            t = (h - 60) / 60.0
            x = g_pt.x() + (b_pt.x() - g_pt.x()) * t
            y = g_pt.y() + (b_pt.y() - g_pt.y()) * t
        else:
            t = (h - 120) / 60.0
            x = b_pt.x() + (r_pt.x() - b_pt.x()) * t
            y = b_pt.y() + (r_pt.y() - b_pt.y()) * t
        return QPoint(int(x), int(y))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        margin = 10
        tw, th = w - 2 * margin, h - 2 * margin

        # 背景
        p.fillRect(self.rect(), QColor(22, 27, 34))

        # 三角形顶点 (R=红顶, G=绿左下, B=蓝右下)
        r_pt = QPoint(margin + tw // 2, margin)
        g_pt = QPoint(margin, margin + th)
        b_pt = QPoint(margin + tw, margin + th)

        # 填充三角形 — 渐变色彩
        for y in range(margin, margin + th + 1):
            t = (y - margin) / th if th > 0 else 0
            left_x = int(r_pt.x() + (g_pt.x() - r_pt.x()) * t)
            right_x = int(r_pt.x() + (b_pt.x() - r_pt.x()) * t)
            for x in range(left_x, right_x + 1):
                if left_x == right_x: continue
                u = (x - left_x) / (right_x - left_x) if right_x != left_x else 0
                # Barycentric: (1-t, t*(1-u), t*u)
                a_r = 1.0 - t
                a_g = t * (1.0 - u)
                a_b = t * u
                rr = int(255 * a_r)
                gg = int(255 * a_g)
                bb = int(255 * a_b)
                p.setPen(QColor(rr, gg, bb))
                p.drawPoint(x, y)

        # 边框
        p.setPen(QPen(QColor(80, 80, 90), 1.5))
        poly = QPolygon([r_pt, g_pt, b_pt])
        p.drawPolygon(poly)

        # 选中的颜色区间框（6个点: R低,R高,G低,G高,B低,B高）
        pts = [
            self._hue_to_xy(self._r_lo, w, h, margin, r_pt, g_pt, b_pt),
            self._hue_to_xy(self._r_hi, w, h, margin, r_pt, g_pt, b_pt),
            self._hue_to_xy(self._g_lo, w, h, margin, r_pt, g_pt, b_pt),
            self._hue_to_xy(self._g_hi, w, h, margin, r_pt, g_pt, b_pt),
            self._hue_to_xy(self._b_lo, w, h, margin, r_pt, g_pt, b_pt),
            self._hue_to_xy(self._b_hi, w, h, margin, r_pt, g_pt, b_pt),
        ]


        # 计算凸包作为选中区域
        from PySide6.QtGui import QPolygonF
        cx = sum(p.x() for p in pts) / 6
        cy = sum(p.y() for p in pts) / 6
        pts_sorted = sorted(pts, key=lambda p: __import__('math').atan2(p.y()-cy, p.x()-cx))
        poly = QPolygonF([p for p in pts_sorted])
        p.setPen(QPen(QColor(255, 255, 255), 2))
        p.setBrush(QColor(0, 0, 0, 100))
        p.drawPolygon(poly)

        # 顶点标签
        # 为每个字母绘制一个带背景的标签
        label_data = [
            ("R", r_pt + QPoint(-20, 6)),   # 在顶点正下方一点
            ("G", g_pt + QPoint(10, -20)),  # 在左下角右上方
            ("B", b_pt + QPoint(-10, -20))  # 在右下角左上方
        ]

        for label, pos in label_data:
            # 获取文字矩形（用于背景和居中）
            rect = p.fontMetrics().boundingRect(label)
            # 将矩形中心对齐到 pos
            text_rect = QRect(
                pos.x() - rect.width() // 2,
                pos.y() - rect.height() // 2,
                rect.width(),
                rect.height()
            )
            # 画半透明黑色背景，让文字在任何颜色下都清晰
            p.fillRect(text_rect, QColor(0, 0, 0, 160))
            # 画白色文字
            p.setPen(QColor(255, 255, 255))
            p.drawText(text_rect, Qt.AlignCenter, label)

        p.end()


# ─── TOC 算法参数编辑器 ──────────────────────────────────────────

class TocAlgorithmEditor(QWidget):
    """TOC 算法参数编辑器，参考 TocEmptyAlgorithmDialog"""

    param_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_params: List[Dict] = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # ═══ 顶部：四通道范围滑块 ═══
        channel_group = QGroupBox("RGB + 灰度 通道范围")
        ch_layout = QVBoxLayout(channel_group)
        ch_layout.setSpacing(6)

        # 红通道
        self._row_red = self._make_channel_row("R 红色", 0, 180, QColor(200, 60, 60))
        ch_layout.addWidget(self._row_red["layout"])
        # 绿通道
        self._row_green = self._make_channel_row("G 绿色", 0, 180, QColor(60, 180, 60))
        ch_layout.addWidget(self._row_green["layout"])
        # 蓝通道
        self._row_blue = self._make_channel_row("B 蓝色", 0, 180, QColor(60, 100, 220))
        ch_layout.addWidget(self._row_blue["layout"])
        # 灰度通道
        self._row_gray = self._make_channel_row("灰度", 0, 255, QColor(160, 160, 160))
        ch_layout.addWidget(self._row_gray["layout"])

        layout.addWidget(channel_group)

        # ═══ 中部：功能控件 ═══
        mid_row = QHBoxLayout()
        mid_row.setSpacing(10)

        self._toggle_btn = QPushButton("色度图")
        self._toggle_btn.setFixedWidth(80)
        self._toggle_btn.clicked.connect(self._toggle_view)
        mid_row.addWidget(self._toggle_btn)

        self._auto_extract_cb = QCheckBox("自动提取")
        mid_row.addWidget(self._auto_extract_cb)

        mid_row.addStretch()
        mid_row.addWidget(QLabel("灰度均值:"))
        self._gray_mean_label = QLabel("—")
        self._gray_mean_label.setStyleSheet("color:#58a6ff; font-weight:bold;")
        mid_row.addWidget(self._gray_mean_label)
        layout.addLayout(mid_row)

        # ═══ 底部：StackedWidget (色度图 / 详细参数) ═══
        self._stack = QStackedWidget()

        # 页面 0: 色度三角形
        self._triangle = TriangleWidget()
        self._stack.addWidget(self._triangle)

        # 页面 1: 详细参数
        detail_page = QWidget()
        detail_layout = QVBoxLayout(detail_page)
        detail_layout.setSpacing(6)

        self._detail_sliders = {}
        detail_params = [
            ("histoPercentile", "直方图范围百分点", 0, 100, 50),
            ("intenseResolution", "强度分辨率", 1, 100, 10),
            ("hueResolution", "色度分辨率", 1, 100, 10),
            ("intenseTolerance", "强度可容忍比例", 0, 100, 20),
            ("hueTolerance", "色调可容忍比例", 0, 100, 20),
        ]
        for key, label, lo, hi, default in detail_params:
            row = QHBoxLayout()
            lbl = QLabel(f"  {label}:")
            lbl.setFixedWidth(130)
            lbl.setStyleSheet("color:#c9d1d9; font-size:12px;")
            row.addWidget(lbl)

            slider = QSlider(Qt.Horizontal)
            slider.setRange(lo, hi)
            slider.setValue(default)
            row.addWidget(slider, 1)

            spin = QSpinBox()
            spin.setRange(lo, hi)
            spin.setValue(default)
            spin.setFixedWidth(55)
            spin.setStyleSheet("QSpinBox { font-size:11px; }")
            row.addWidget(spin)

            slider.valueChanged.connect(
                lambda v, s=spin: (s.blockSignals(True), s.setValue(v), s.blockSignals(False)))
            spin.valueChanged.connect(
                lambda v, sl=slider: (sl.blockSignals(True), sl.setValue(v), sl.blockSignals(False)))

            detail_layout.addLayout(row)
            self._detail_sliders[key] = spin

        # 参数自适应
        adapt_row = QHBoxLayout()
        adapt_row.addWidget(QLabel("  参数自适应:"))
        self._adapt_combo = QComboBox()
        self._adapt_combo.addItems(["方法1", "方法2", "方法3", "方法4"])
        self._adapt_combo.setCurrentIndex(0)
        adapt_row.addWidget(self._adapt_combo)
        adapt_row.addStretch()
        detail_layout.addLayout(adapt_row)
        detail_layout.addStretch()

        self._stack.addWidget(detail_page)
        layout.addWidget(self._stack, 1)

    def _make_channel_row(self, label: str, lo: int, hi: int, color: QColor) -> dict:
        """创建一行: [标签] [低值SpinBox] [RangeSlider] [高值SpinBox]"""
        w = QWidget()
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        lbl = QLabel(label)
        lbl.setFixedWidth(55)
        lbl.setStyleSheet("color:#c9d1d9; font-size:11px;")
        row.addWidget(lbl)

        # 低值SpinBox
        low = QSpinBox()
        low.setRange(lo, hi)
        low.setFixedWidth(58)
        low.setFixedHeight(34)
        low.setStyleSheet("""
            QSpinBox { 
                font-size:11px; 
                color:#c9d1d9;
                padding: 2px 3px;
                border: 1px solid #444a53;
                background-color:#161b22;
            }
            /* 整体按钮容器宽度加宽 */
            QSpinBox::up-button, QSpinBox::down-button {
                width: 18px;
                border: none;
            }
            /* 上箭头按钮：浅深色底 */
            QSpinBox::up-button {
                background:#363c44;
                border-top-right-radius:4px;
            }
            /* 下箭头按钮：更深底色，区分上层 */
            QSpinBox::down-button {
                background:#2a2f36;
                border-bottom-right-radius:4px;
            }
            /* 加大白色箭头，清晰可见 */
            QSpinBox::up-arrow {
                width:10px;
                height:10px;
                color:#ffffff;
            }
            QSpinBox::down-arrow {
                width:10px;
                height:10px;
                color:#ffffff;
            }
        """)
        row.addWidget(low)

        rs = RangeSlider()
        rs.setMinimum(lo)
        rs.setMaximum(hi)
        rs.SetColor(color)
        row.addWidget(rs, 1)

        # 高值SpinBox 和左侧样式完全统一
        high = QSpinBox()
        high.setRange(lo, hi)
        high.setValue(hi)
        high.setFixedWidth(58)
        high.setFixedHeight(34)
        high.setStyleSheet("""
            QSpinBox { 
                font-size:11px; 
                color:#c9d1d9;
                padding: 2px 3px;
                border: 1px solid #444a53;
                background-color:#161b22;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 18px;
                border: none;
            }
            QSpinBox::up-button {
                background:#363c44;
                border-top-right-radius:4px;
            }
            QSpinBox::down-button {
                background:#2a2f36;
                border-bottom-right-radius:4px;
            }
            QSpinBox::up-arrow {
                width:10px;
                height:10px;
                color:#000000;
            }
            QSpinBox::down-arrow {
                width:10px;
                height:10px;
                color:#000000;
            }
            QSpinBox::up-button:hover {background:#404750;}
            QSpinBox::down-button:hover {background:#31373f;}
        """)
        row.addWidget(high)

        # 双向绑定逻辑不变
        rs.lowerValueChanged.connect(
            lambda v, s=low: (s.blockSignals(True), s.setValue(v), s.blockSignals(False)))
        rs.upperValueChanged.connect(
            lambda v, s=high: (s.blockSignals(True), s.setValue(v), s.blockSignals(False)))
        low.valueChanged.connect(
            lambda v, r=rs: r.setLowerValue(v))
        high.valueChanged.connect(
            lambda v, r=rs: r.setUpperValue(v))

        return {"layout": w, "low": low, "high": high, "slider": rs}

    def _toggle_view(self):
        if self._stack.currentIndex() == 0:
            self._stack.setCurrentIndex(1)
            self._toggle_btn.setText("详细参数")
        else:
            self._stack.setCurrentIndex(0)
            self._toggle_btn.setText("色度图")

    # ═════════════════════════════════════════════════════

    def load_params(self, common_params: Dict[str, Any], toc_params: Dict[str, Any]):
        """加载 COMMON 和 TOC 参数数据"""
        self._current_params = [common_params, toc_params]

        # 四个通道从 COMMON 取
        self._row_red["low"].setValue(int(common_params.get("Color_Red_Low", 0)))
        self._row_red["high"].setValue(int(common_params.get("Color_Red_High", 180)))
        self._row_green["low"].setValue(int(common_params.get("Color_Green_Low", 0)))
        self._row_green["high"].setValue(int(common_params.get("Color_Green_High", 180)))
        self._row_blue["low"].setValue(int(common_params.get("Color_Blue_Low", 0)))
        self._row_blue["high"].setValue(int(common_params.get("Color_Blue_High", 180)))
        self._row_gray["low"].setValue(int(common_params.get("Color_Gray_Low", 0)))
        self._row_gray["high"].setValue(int(common_params.get("Color_Gray_High", 255)))

        # 绑定 RangeSlider → 色度三角形
        for color_name, row_key in [("Red", "_row_red"), ("Green", "_row_green"),
                                     ("Blue", "_row_blue")]:
            rs = getattr(self, row_key)["slider"]
            triangle = self._triangle
            # 断开旧信号（避免重复连接）
            try:
                rs.lowerValueChanged.disconnect()
                rs.upperValueChanged.disconnect()
            except Exception:
                pass
            if color_name == "Red":
                rs.lowerValueChanged.connect(triangle.SetRedLowValue)
                rs.upperValueChanged.connect(triangle.SetRedHighValue)
            elif color_name == "Green":
                rs.lowerValueChanged.connect(triangle.SetGreenLowValue)
                rs.upperValueChanged.connect(triangle.SetGreenHighValue)
            else:
                rs.lowerValueChanged.connect(triangle.SetBlueLowValue)
                rs.upperValueChanged.connect(triangle.SetBlueHighValue)

        # 初始设置三角形值
        self._triangle.SetRedLowValue(int(common_params.get("Color_Red_Low", 0)))
        self._triangle.SetRedHighValue(int(common_params.get("Color_Red_High", 180)))
        self._triangle.SetGreenLowValue(int(common_params.get("Color_Green_Low", 0)))
        self._triangle.SetGreenHighValue(int(common_params.get("Color_Green_High", 180)))
        self._triangle.SetBlueLowValue(int(common_params.get("Color_Blue_Low", 0)))
        self._triangle.SetBlueHighValue(int(common_params.get("Color_Blue_High", 180)))

        # TOC 参数
        auto = toc_params.get("Auto_Extract_Color", 0)
        self._auto_extract_cb.setChecked(bool(auto))

        gray_mean = toc_params.get("Template_Gray_Mean", 0)
        self._gray_mean_label.setText(str(gray_mean))

        self._detail_sliders["histoPercentile"].setValue(
            int(toc_params.get("Histo_Percentile_Pt", 50)))
        self._detail_sliders["intenseResolution"].setValue(
            int(toc_params.get("Intense_Resolution", 10)))
        self._detail_sliders["hueResolution"].setValue(
            int(toc_params.get("Hue_Resolution", 10)))
        self._detail_sliders["intenseTolerance"].setValue(
            int(toc_params.get("Intense_Vary_Tolerance_Factor", 20)))
        self._detail_sliders["hueTolerance"].setValue(
            int(toc_params.get("Hue_Vary_Tolerance_Factor", 20)))
        adapt = int(toc_params.get("Param_Adapt_Method", 1))
        self._adapt_combo.setCurrentIndex(max(0, adapt - 1))

        # 更新三角形
        self._triangle.SetRedLowValue(int(common_params.get("Color_Red_Low", 0)))
        self._triangle.SetRedHighValue(int(common_params.get("Color_Red_High", 180)))
        self._triangle.SetGreenLowValue(int(common_params.get("Color_Green_Low", 0)))
        self._triangle.SetGreenHighValue(int(common_params.get("Color_Green_High", 180)))
        self._triangle.SetBlueLowValue(int(common_params.get("Color_Blue_Low", 0)))
        self._triangle.SetBlueHighValue(int(common_params.get("Color_Blue_High", 180)))

    def collect_values(self) -> dict:
        return {
            "common": {
                "Color_Red_Low": self._row_red["low"].value(),
                "Color_Red_High": self._row_red["high"].value(),
                "Color_Green_Low": self._row_green["low"].value(),
                "Color_Green_High": self._row_green["high"].value(),
                "Color_Blue_Low": self._row_blue["low"].value(),
                "Color_Blue_High": self._row_blue["high"].value(),
                "Color_Gray_Low": self._row_gray["low"].value(),
                "Color_Gray_High": self._row_gray["high"].value(),
            },
            "toc": {
                "Auto_Extract_Color": 1 if self._auto_extract_cb.isChecked() else 0,
                "Template_Gray_Mean": int(self._gray_mean_label.text()),
                "Histo_Percentile_Pt": self._detail_sliders["histoPercentile"].value(),
                "Intense_Resolution": self._detail_sliders["intenseResolution"].value(),
                "Hue_Resolution": self._detail_sliders["hueResolution"].value(),
                "Intense_Vary_Tolerance_Factor": self._detail_sliders["intenseTolerance"].value(),
                "Hue_Vary_Tolerance_Factor": self._detail_sliders["hueTolerance"].value(),
                "Param_Adapt_Method": self._adapt_combo.currentIndex() + 1,
            },
        }
