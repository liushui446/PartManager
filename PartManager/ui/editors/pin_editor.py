"""PIN 引脚检测算法编辑器 — 参考原PIN参数结构"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QSpinBox, QComboBox, QFrame,
)
from PySide6.QtCore import Qt

from ui.range_slider import RangeSlider


def _make_range_row(label: str, lo: int, hi: int, color_key: str,
                    low_val: int, high_val: int) -> dict:
    """创建一行: [标签] [低值SpinBox] [彩色RangeSlider] [高值SpinBox]"""
    from PySide6.QtGui import QColor

    color_map = {
        "R": QColor(200, 60, 60), "G": QColor(60, 180, 60),
        "B": QColor(60, 100, 220), "Gray": QColor(140, 140, 140),
        "Judge": QColor(100, 100, 180),
    }
    track_color = color_map.get(color_key, QColor(100, 100, 100))

    spin_style = ("QSpinBox{background:#0d1117;color:#e6edf3;"
                  "border:1px solid #30363d;border-radius:3px;"
                  "padding:1px 2px 1px 4px;font-size:11px;}"
                  "QSpinBox::up-button{width:14px;background:#21262d;"
                  "border-left:1px solid #30363d;}"
                  "QSpinBox::down-button{width:14px;background:#21262d;"
                  "border-left:1px solid #30363d;}")

    w = QWidget()
    row = QHBoxLayout(w)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(4)

    lbl = QLabel(label)
    lbl.setFixedWidth(72)
    lbl.setStyleSheet("color:#c9d1d9; font-size:11px; font-weight:bold;")
    row.addWidget(lbl)

    low = QSpinBox()
    low.setRange(lo, hi)
    low.setValue(low_val)
    low.setFixedWidth(52)
    low.setFixedHeight(28)
    low.setStyleSheet(spin_style)

    rs = RangeSlider()
    rs.setMinimum(lo)
    rs.setMaximum(hi)
    rs.setLowerValue(low_val)
    rs.setUpperValue(high_val)
    rs.SetColor(track_color)
    row.addWidget(rs, 1)

    high = QSpinBox()
    high.setRange(lo, hi)
    high.setValue(high_val)
    high.setFixedWidth(52)
    high.setFixedHeight(28)
    high.setStyleSheet(spin_style)
    row.addWidget(high)

    # 双向绑定: RangeSlider ↔ SpinBoxes
    rs.lowerValueChanged.connect(lambda v, s=low: (s.blockSignals(True), s.setValue(v), s.blockSignals(False)))
    rs.upperValueChanged.connect(lambda v, s=high: (s.blockSignals(True), s.setValue(v), s.blockSignals(False)))
    low.valueChanged.connect(lambda v, r=rs: r.setLowerValue(v))
    high.valueChanged.connect(lambda v, r=rs: r.setUpperValue(v))

    return {"widget": w, "low": low, "high": high, "slider": rs}


class PinEditor(QWidget):
    """PIN 引脚检测 — 少锡 + 空焊 + 检测矩形"""

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # ═══ 少锡检测 ═══
        lt_group = QGroupBox("少锡检测 — 通道范围")
        lt_layout = QVBoxLayout(lt_group)
        lt_layout.setSpacing(4)

        self._rows_lt = {}
        for key, label, color in [
            ("Less_Tin_Red", "少锡红", "R"),
            ("Less_Tin_Green", "少锡绿", "G"),
            ("Less_Tin_Blue", "少锡蓝", "B"),
            ("Less_Tin_Gray", "少锡灰", "Gray"),
        ]:
            r = _make_range_row(label, 0, 255, color, 0, 255)
            lt_layout.addWidget(r["widget"])
            self._rows_lt[key] = r

        # 少锡判定
        jr = _make_range_row("少锡判定", 0, 255, "Judge", 0, 100)
        lt_layout.addWidget(jr["widget"])
        self._rows_lt["Less_Tin_Judge"] = jr

        layout.addWidget(lt_group)

        # ═══ 空焊检测 ═══
        ew_group = QGroupBox("空焊检测 — 通道范围")
        ew_layout = QVBoxLayout(ew_group)
        ew_layout.setSpacing(4)

        self._rows_ew = {}
        for key, label, color in [
            ("Empty_Welding_Red", "空焊红", "R"),
            ("Empty_Welding_Green", "空焊绿", "G"),
            ("Empty_Welding_Blue", "空焊蓝", "B"),
            ("Empty_Welding_Gray", "空焊灰", "Gray"),
        ]:
            r = _make_range_row(label, 0, 255, color, 0, 255)
            ew_layout.addWidget(r["widget"])
            self._rows_ew[key] = r

        jr2 = _make_range_row("空焊判定", 0, 255, "Judge", 0, 100)
        ew_layout.addWidget(jr2["widget"])
        self._rows_ew["Empty_Welding_Judge"] = jr2

        layout.addWidget(ew_group)

        # ═══ 检测矩形 ═══
        rect_group = QGroupBox("检测矩形区域")
        rg = QGridLayout(rect_group)
        rg.setSpacing(4)
        self._rect_spins = {}
        rect_fields = [
            ("Detected_Rect_Left_Top_X", "检测 左上X"),
            ("Detected_Rect_Left_Top_Y", "检测 左上Y"),
            ("Detected_Rect_Right_Down_X", "检测 右下X"),
            ("Detected_Rect_Right_Down_Y", "检测 右下Y"),
            ("Position_Rect_Left_Top_X", "定位 左上X"),
            ("Position_Rect_Left_Top_Y", "定位 左上Y"),
            ("Position_Rect_Right_Down_X", "定位 右下X"),
            ("Position_Rect_Right_Down_Y", "定位 右下Y"),
        ]
        for r, (key, label) in enumerate(rect_fields):
            rr = r // 2; cc = (r % 2) * 2
            rg.addWidget(QLabel(label), rr, cc)
            sp = QSpinBox(); sp.setRange(0, 99999); sp.setValue(0)
            rg.addWidget(sp, rr, cc + 1)
            self._rect_spins[key] = sp
        layout.addWidget(rect_group)
        layout.addStretch()

    def load_params(self, params: dict):
        """加载参数"""
        try:
            for key, row_data in self._rows_lt.items():
                lo = int(params.get(f"{key}_Low", 0) or 0)
                hi = int(params.get(f"{key}_High", 255) or 255)
                row_data["low"].setValue(lo)
                row_data["high"].setValue(hi)

            for key, row_data in self._rows_ew.items():
                lo = int(params.get(f"{key}_Low", 0) or 0)
                hi = int(params.get(f"{key}_High", 255) or 255)
                row_data["low"].setValue(lo)
                row_data["high"].setValue(hi)

            for key in self._rect_spins:
                self._rect_spins[key].setValue(int(params.get(key, 0) or 0))
        except Exception:
            pass

    def collect_values(self) -> dict:
        """收集所有参数"""
        result = {}
        for key, row_data in self._rows_lt.items():
            result[f"{key}_Low"] = row_data["low"].value()
            result[f"{key}_High"] = row_data["high"].value()
        for key, row_data in self._rows_ew.items():
            result[f"{key}_Low"] = row_data["low"].value()
            result[f"{key}_High"] = row_data["high"].value()
        for key, sp in self._rect_spins.items():
            result[key] = sp.value()
        return result
