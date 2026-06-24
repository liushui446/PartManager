"""新建元件对话框"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QComboBox, QLineEdit, QPushButton, QFileDialog, QDialogButtonBox,
    QGroupBox, QMessageBox,
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt


PACKAGE_TYPES = [
    "CHIP_R", "CHIP_C", "DIODE", "TR", "MELF", "SOP", "QFP",
    "BGA", "LED", "PLUGINUNIT", "SINGLERECT", "SOLDERJOINT", "OTHER",
]
PACKAGE_CN = {
    "CHIP_R": "电阻", "CHIP_C": "电容", "DIODE": "二极管",
    "TR": "三极管", "MELF": "色环电阻", "SOP": "SOP", "QFP": "QFP",
    "BGA": "BGA", "LED": "LED", "PLUGINUNIT": "插件",
    "SINGLERECT": "单框", "SOLDERJOINT": "焊点", "OTHER": "其它",
}


class NewComponentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新建元器件")
        self.setMinimumWidth(420)
        self._image_path = ""
        self._image_data = b""
        self._image_w = 0
        self._image_h = 0
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 封装类型
        form = QFormLayout()
        self._pkg_combo = QComboBox()
        for pt in PACKAGE_TYPES:
            self._pkg_combo.addItem(f"{PACKAGE_CN.get(pt, pt)} ({pt})", pt)
        form.addRow("封装类型:", self._pkg_combo)

        # 元件名称
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("输入元件名称...")
        form.addRow("元件名称:", self._name_edit)
        layout.addLayout(form)

        # 模板图像
        img_group = QGroupBox("模板图像")
        img_layout = QVBoxLayout(img_group)

        btn_row = QHBoxLayout()
        self._img_btn = QPushButton("📁 选择图片")
        self._img_btn.clicked.connect(self._select_image)
        btn_row.addWidget(self._img_btn)
        btn_row.addStretch()
        img_layout.addLayout(btn_row)

        self._img_label = QLabel("未选择图片")
        self._img_label.setAlignment(Qt.AlignCenter)
        self._img_label.setMinimumHeight(120)
        self._img_label.setStyleSheet(
            "QLabel { background:#0d1117; border:1px solid #30363d; border-radius:4px; color:#484f58; }")
        img_layout.addWidget(self._img_label)

        self._img_info = QLabel("")
        self._img_info.setStyleSheet("color:#8b949e; font-size:11px;")
        img_layout.addWidget(self._img_info)
        layout.addWidget(img_group)

        # 按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _select_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择模板图像", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.tif)")
        if not path:
            return
        self._image_path = path
        try:
            with open(path, "rb") as f:
                data = f.read()
            # 解析图像尺寸
            img = QImage.fromData(data)
            if img.isNull():
                QMessageBox.warning(self, "错误", "无法解析该图像文件")
                return
            self._image_w = img.width()
            self._image_h = img.height()
            # 转换为 RGB888 原始像素（去除行对齐填充）
            if img.format() != QImage.Format_RGB888:
                img = img.convertToFormat(QImage.Format_RGB888)
            w, h = img.width(), img.height()
            raw = bytearray(w * h * 3)
            for y in range(h):
                src = img.constScanLine(y)
                offset = y * w * 3
                raw[offset:offset + w * 3] = bytes(src[:w * 3])
            self._image_data = bytes(raw)
            # 预览
            pixmap = QPixmap.fromImage(img)
            mw = self._img_label.width() - 16
            mh = self._img_label.height() - 16
            if mw < 100: mw = 280
            if mh < 100: mh = 180
            scaled = pixmap.scaled(mw, mh, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self._img_label.setPixmap(scaled)
            self._img_info.setText(f"{self._image_w}×{self._image_h} px | {len(self._image_data)} bytes")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载图片失败: {e}")

    def _on_accept(self):
        name = self._name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请输入元件名称")
            return
        if not self._image_data:
            QMessageBox.warning(self, "提示", "请选择模板图像")
            return
        self.accept()

    def get_package_type(self) -> str:
        return self._pkg_combo.currentData()

    def get_component_name(self) -> str:
        return self._name_edit.text().strip()

    def get_image_data(self) -> tuple:
        return self._image_data, self._image_w, self._image_h
