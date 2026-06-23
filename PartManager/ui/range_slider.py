"""
双把手范围滑块 — 参考原 C++ RangeSlider 控件
"""

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, Signal, QRect
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QPixmap, QFont


class RangeSlider(QWidget):
    """双把手范围选择滑块，支持背景 Pixmap 和彩色轨道"""

    lowerValueChanged = Signal(int)
    upperValueChanged = Signal(int)

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(parent)
        self._min = 0
        self._max = 255
        self._lower = 0
        self._upper = 255
        self._track_color = QColor(80, 80, 80)
        self._handle_color = QColor(200, 200, 200)
        self._active_color = QColor(100, 100, 100)
        self._bg_pixmap: QPixmap | None = None
        self._dragging = 0  # 0=none, 1=lower, 2=upper
        self.setFixedHeight(40)
        self.setMinimumWidth(100)
        self.setMouseTracking(True)

    def setMinimum(self, val: int): self._min = val; self.update()
    def setMaximum(self, val: int): self._max = val; self.update()
    def setLowerValue(self, val: int):
        val = max(self._min, min(val, self._upper))
        if val != self._lower:
            self._lower = val; self.update(); self.lowerValueChanged.emit(val)
    def setUpperValue(self, val: int):
        val = max(self._lower, min(val, self._max))
        if val != self._upper:
            self._upper = val; self.update(); self.upperValueChanged.emit(val)
    def lowerValue(self) -> int: return self._lower
    def upperValue(self) -> int: return self._upper

    def SetColor(self, color: QColor):
        self._track_color = color; self.update()
    def SetPixMap(self, pixmap: QPixmap):
        self._bg_pixmap = pixmap; self.update()

    def _val_to_x(self, val: int) -> int:
        rng = self._max - self._min
        if rng == 0: return 0
        return int((val - self._min) / rng * (self.width() - 2)) + 1

    def _x_to_val(self, x: int) -> int:
        rng = self._max - self._min
        if rng == 0: return self._min
        return self._min + int((x - 1) / (self.width() - 2) * rng)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # 背景
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(30, 30, 35))
        p.drawRoundedRect(0, 0, w, h, 6, 6)

        # Pixmap 背景
        if self._bg_pixmap and not self._bg_pixmap.isNull():
            pm = self._bg_pixmap.scaled(w - 2, h - 10, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            p.drawPixmap(1, 5, pm)

        # 轨道
        track_y = h // 2 - 3
        track_h = 6
        lx = self._val_to_x(self._lower)
        ux = self._val_to_x(self._upper)

        # 未选中区
        p.setBrush(QColor(60, 63, 68))
        p.drawRoundedRect(1, track_y, w - 2, track_h, 3, 3)
        # 选中区
        p.setBrush(self._track_color)
        p.drawRoundedRect(lx, track_y, ux - lx, track_h, 3, 3)

        # 把手
        handle_w = 10
        for hx, is_lower in [(lx, True), (ux, False)]:
            p.setBrush(self._handle_color if self._dragging != (1 if is_lower else 2)
                       else QColor(255, 255, 255))
            p.drawRoundedRect(hx - handle_w // 2, 5, handle_w, h - 10, 4, 4)

        p.end()

    def mousePressEvent(self, event):
        x = event.position().x()
        lx = self._val_to_x(self._lower)
        ux = self._val_to_x(self._upper)
        dist_l = abs(x - lx)
        dist_u = abs(x - ux)
        if dist_l < dist_u and dist_l < 15:
            self._dragging = 1
        elif dist_u < 15:
            self._dragging = 2
        else:
            self._dragging = 0
        self.update()

    def mouseMoveEvent(self, event):
        if self._dragging == 1:
            self.setLowerValue(self._x_to_val(int(event.position().x())))
        elif self._dragging == 2:
            self.setUpperValue(self._x_to_val(int(event.position().x())))
        self.update()

    def mouseReleaseEvent(self, event):
        self._dragging = 0
        self.update()
