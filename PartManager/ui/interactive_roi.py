"""
交互式 ROI 视图 — 支持拖拽移动和角点缩放
"""
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsItem
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QPen, QColor, QBrush, QPainter, QPixmap, QCursor


class RoiRectItem(QGraphicsRectItem):
    """可拖拽移动 + 四角缩放的 ROI 矩形"""

    handle_size = 8

    def __init__(self, rect, parent=None):
        super().__init__(rect, parent)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self._resizing = False
        self._resize_corner = -1
        self._changed_cb = None  # 回调函数

    def set_changed_callback(self, cb):
        self._changed_cb = cb

    def set_style(self):
        self.setPen(QPen(QColor(255, 0, 0), 2))
        self.setBrush(QBrush(QColor(255, 0, 0, 30)))

    def hoverMoveEvent(self, event):
        if self._resizing:
            return
        pos = event.pos()
        corner = self._hit_corner(pos)
        if corner >= 0:
            cursors = [Qt.SizeFDiagCursor, Qt.SizeBDiagCursor,
                       Qt.SizeFDiagCursor, Qt.SizeBDiagCursor]
            self.setCursor(cursors[corner])
        else:
            self.setCursor(Qt.SizeAllCursor)
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        corner = self._hit_corner(event.pos())
        if corner >= 0:
            self._resizing = True
            self._resize_corner = corner
            self._resize_start = self.rect()
            self._press_pos = event.scenePos()
        else:
            self._resizing = False
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing:
            delta = event.scenePos() - self._press_pos
            old = self._resize_start
            c = self._resize_corner
            new_rect = QRectF(old)
            if c in (0, 3):  # left side
                new_rect.setLeft(old.left() + delta.x())
            if c in (1, 2):  # right side
                new_rect.setRight(old.right() + delta.x())
            if c in (0, 1):  # top
                new_rect.setTop(old.top() + delta.y())
            if c in (2, 3):  # bottom
                new_rect.setBottom(old.bottom() + delta.y())
            # 最小尺寸限制
            if new_rect.width() < 10: new_rect.setWidth(10)
            if new_rect.height() < 10: new_rect.setHeight(10)
            self.setRect(new_rect)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        changed = self._resizing
        if self._resizing:
            self._resizing = False
        super().mouseReleaseEvent(event)
        if changed and self._changed_cb:
            self._changed_cb()

    def _hit_corner(self, pos):
        r = self.rect()
        hs = self.handle_size
        corners = [
            QRectF(r.left() - hs, r.top() - hs, hs * 2, hs * 2),      # TL
            QRectF(r.right() - hs, r.top() - hs, hs * 2, hs * 2),     # TR
            QRectF(r.right() - hs, r.bottom() - hs, hs * 2, hs * 2),  # BR
            QRectF(r.left() - hs, r.bottom() - hs, hs * 2, hs * 2),   # BL
        ]
        for i, cr in enumerate(corners):
            if cr.contains(pos):
                return i
        return -1

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        # 画四个角点
        r = self.rect()
        hs = self.handle_size
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.setBrush(QBrush(QColor(255, 0, 0)))
        for cx, cy in [(r.left(), r.top()), (r.right(), r.top()),
                       (r.right(), r.bottom()), (r.left(), r.bottom())]:
            painter.drawRect(int(cx - hs / 2), int(cy - hs / 2), hs, hs)


class InteractiveRoiView(QGraphicsView):
    """交互式模板图像 + ROI 视图"""

    roi_changed = Signal(float, float, float, float)  # x, y, w, h (像素坐标)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        from PySide6.QtWidgets import QFrame
        self.setFrameShape(QFrame.NoFrame)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setStyleSheet("background:#0d1117; border:1px solid #30363d; border-radius:4px;")

        self._pixmap_item = None
        self._roi_item = None
        self._img_w = 0
        self._img_h = 0

    def set_image(self, pixmap: QPixmap, img_w: int, img_h: int,
                  roi_x: float = 0, roi_y: float = 0,
                  roi_w: float = 0, roi_h: float = 0):
        """设置模板图像和ROI矩形"""
        self._scene.clear()
        self._img_w = img_w
        self._img_h = img_h

        self._pixmap_item = self._scene.addPixmap(pixmap)
        self._pixmap_item.setPos(0, 0)

        self.setSceneRect(QRectF(0, 0, pixmap.width(), pixmap.height()))
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

        if roi_w > 0 and roi_h > 0:
            rect = QRectF(roi_x, roi_y, roi_w, roi_h)
            self._roi_item = RoiRectItem(rect, self._pixmap_item)
            self._roi_item.set_style()
            self._roi_item.set_changed_callback(self._emit_roi_changed)

    def update_roi(self, roi_x: float, roi_y: float, roi_w: float, roi_h: float):
        """更新ROI位置"""
        if self._roi_item:
            self._roi_item.setRect(QRectF(roi_x, roi_y, roi_w, roi_h))

    def _emit_roi_changed(self):
        if self._roi_item:
            r = self._roi_item.rect()
            self._scene.update()
            self.roi_changed.emit(r.x(), r.y(), r.width(), r.height())
        """获取当前ROI矩形 (x, y, w, h) 像素坐标"""
        if self._roi_item:
            r = self._roi_item.rect()
            return r.x(), r.y(), r.width(), r.height()
        return 0, 0, 0, 0

    def wheelEvent(self, event):
        """滚轮缩放"""
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)
