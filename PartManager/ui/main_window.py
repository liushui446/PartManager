"""
元器件模板库管理系统 - 主窗口 v3
"""

import sys, os
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem,
    QTabWidget, QLabel, QPushButton, QStatusBar,
    QHeaderView, QFrame, QGroupBox, QMessageBox, QCheckBox,
    QLineEdit, QAbstractItemView, QSizePolicy, QMenuBar, QMenu,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap, QImage, QAction, QPainter, QPen, QColor

from db import ComponentDatabase
from ui.styles import GLOBAL_STYLE, TITLE_STYLE, STATUS_STYLE, CARD_STYLE, SUMMARY_STYLE, PARAM_PANEL_STYLE
from ui.algorithm_editor import AlgorithmParamEditor, ALGORITHM_SHORT_NAMES
from ui.toc_editor import TocAlgorithmEditor
from ui.editors.offset_editor import OffsetEditor
from ui.editors.short_editor import ShortEditor
from ui.editors.ocv_editor import OcvEditor
from ui.editors.ocr_editor import OcrEditor
from ui.editors.other_editor import OtherEditor
from ui.editors.pin_editor import PinEditor
from ui.editors.match_editor import MatchEditor
from ui.editors.match2_editor import Match2Editor
from ui.editors.pin_editor import PinEditor


class MainWindow(QMainWindow):
    def __init__(self, db_path: str):
        super().__init__()
        self._db = ComponentDatabase(db_path)
        self._current_component: Optional[str] = None
        self._current_algo_table: Optional[str] = None

        self._init_ui()
        self._apply_styles()
        self._load_data()
        self._connect_signals()

    # ═════════════════════════════════════════════════════════════
    #  UI 构建
    # ═════════════════════════════════════════════════════════════

    def _init_ui(self):
        self.setWindowTitle("元器件模板库管理系统 v3.0")
        self.resize(1520, 920)
        self.setMinimumSize(1100, 680)

        self._create_menu_bar()

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(10, 6, 10, 6)
        root.setSpacing(4)

        # ── 标题 + 摘要（单行紧凑） ──
        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        title = QLabel("🔧 元器件模板库管理系统")
        title.setObjectName("titleLabel")
        top_row.addWidget(title)

        # 紧凑摘要 — 直接内嵌在标题行
        self._summary_widgets = {}
        for key, label in [
            ("component_count", "元器件"), ("ng_record_count", "NG"),
            ("package_type_count", "封装"), ("algorithm_table_count", "算法"),
        ]:
            hh = QHBoxLayout()
            hh.setSpacing(3)
            val = QLabel("--"); val.setObjectName("summaryValue")
            lbl = QLabel(label); lbl.setObjectName("summaryLabel")
            hh.addWidget(val); hh.addWidget(lbl)
            top_row.addLayout(hh)
            self._summary_widgets[key] = val

        top_row.addStretch()

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("搜索元器件...")
        self._search_input.setFixedWidth(220)
        self._search_input.setClearButtonEnabled(True)
        top_row.addWidget(self._search_input)
        root.addLayout(top_row)

        # ── 主三栏 ──
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(2)

        left = self._build_left_panel()
        center = self._build_center_panel()
        right = self._build_right_panel()

        splitter.addWidget(left)
        splitter.addWidget(center)
        splitter.addWidget(right)
        splitter.setSizes([260, 720, 500])
        root.addWidget(splitter)

        # ── 状态栏 ──
        self._status_bar = QStatusBar()
        self._status_label = QLabel("就绪 ✓ (数据已缓存到内存)")
        self._status_label.setObjectName("statusLabel")
        self._status_bar.addWidget(self._status_label)
        self.setStatusBar(self._status_bar)

    def _build_left_panel(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("cardFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(2, 2, 2, 2)

        lbl = QLabel("📦 元器件列表")
        lbl.setStyleSheet("font-weight:bold; font-size:13px; color:#58a6ff; padding:2px 4px;")
        layout.addWidget(lbl)

        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["名称 / 类型"])
        self._tree.setRootIsDecorated(True)
        self._tree.setAnimated(True)
        layout.addWidget(self._tree)
        return frame

    def _build_center_panel(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("cardFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)

        # ── 紧凑信息头 ──
        info_row = QHBoxLayout()
        self._info_table = QTableWidget()
        self._info_table.setColumnCount(2)
        self._info_table.setHorizontalHeaderLabels(["属性", "值"])
        self._info_table.horizontalHeader().setStretchLastSection(True)
        self._info_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._info_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._info_table.verticalHeader().setVisible(False)
        self._info_table.setMaximumHeight(180)
        self._info_table.setMaximumWidth(340)
        info_row.addWidget(self._info_table)

        self._image_label = QLabel("选择元器件后显示")
        self._image_label.setAlignment(Qt.AlignCenter)
        self._image_label.setMinimumSize(160, 120)
        self._image_label.setMaximumHeight(180)
        self._image_label.setStyleSheet(
            "QLabel { background:#0d1117; border:1px solid #30363d; border-radius:4px; color:#484f58; }"
        )
        info_row.addWidget(self._image_label)
        layout.addLayout(info_row)

        # ── 上方：检测项列表（参考 RefCompoNGTable） ──
        ng_lbl = QLabel("📋 检测项列表（点击行查看算法参数）")
        ng_lbl.setStyleSheet("font-weight:bold; font-size:12px; color:#58a6ff; padding:1px 4px;")
        layout.addWidget(ng_lbl)

        self._ng_table = QTableWidget()
        self._ng_table.setColumnCount(5)
        self._ng_table.setHorizontalHeaderLabels(
            ["检测项", "NG_ID", "类型", "应用模式", "当前使用算法"])
        self._ng_table.horizontalHeader().setStretchLastSection(True)
        self._ng_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._ng_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._ng_table.verticalHeader().setVisible(False)
        self._ng_table.setMaximumHeight(140)
        layout.addWidget(self._ng_table)

        # ── 下方：算法参数列表（参考 RefCompAlgorTable） ──
        algor_lbl = QLabel("⚙️ 算法参数列表（点击行编辑参数，勾选Use设置默认算法）")
        algor_lbl.setStyleSheet("font-weight:bold; font-size:12px; color:#58a6ff; padding:1px 4px;")
        layout.addWidget(algor_lbl)

        self._algor_table = QTableWidget()
        self._algor_table.setColumnCount(10)
        self._algor_table.setHorizontalHeaderLabels(
            ["元件名", "元件类型", "NG类型", "NG_ID", "算法", "Use", "ROI_X", "ROI_Y", "ROI_W", "ROI_H"])
        self._algor_table.horizontalHeader().setStretchLastSection(True)
        self._algor_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._algor_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._algor_table.verticalHeader().setVisible(False)
        layout.addWidget(self._algor_table)

        # 按钮
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._btn_save_db = QPushButton("💾 更新数据库")
        self._btn_save_db.setObjectName("btnPrimary")
        self._btn_export = QPushButton("📊 导出CSV")
        btn_row.addWidget(self._btn_save_db)
        btn_row.addWidget(self._btn_export)
        layout.addLayout(btn_row)

        return frame

    def _build_right_panel(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("cardFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(2, 2, 2, 2)

        # 算法类型标题行
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        icon_lbl = QLabel("🔧")
        icon_lbl.setStyleSheet("font-size:16px;")
        title_row.addWidget(icon_lbl)
        self._algo_title = QLabel("算法参数编辑")
        self._algo_title.setStyleSheet("font-weight:bold; font-size:13px; color:#58a6ff; padding:2px 0;")
        title_row.addWidget(self._algo_title)

        self._algo_type_badge = QLabel("")
        self._algo_type_badge.setStyleSheet(
            "background:#1f6feb; color:#fff; border-radius:4px; padding:2px 10px; font-size:11px;")
        title_row.addWidget(self._algo_type_badge)

        self._algo_ng_badge = QLabel("")
        self._algo_ng_badge.setStyleSheet(
            "background:#21262d; color:#8b949e; border-radius:4px; padding:2px 8px; font-size:11px;")
        title_row.addWidget(self._algo_ng_badge)
        title_row.addStretch()
        layout.addLayout(title_row)

        # 用 StackedWidget 切换各算法专用编辑器
        from PySide6.QtWidgets import QStackedWidget
        self._editor_stack = QStackedWidget()
        self._editors: dict = {}
        # 按 algo_type 索引
        editor_map = {
            "generic": AlgorithmParamEditor,
            1: TocAlgorithmEditor,     # TOC
            2: MatchEditor,            # Match
            3: AlgorithmParamEditor,   # Histogram
            4: OcvEditor,              # OCV
            5: AlgorithmParamEditor,   # Compare
            7: AlgorithmParamEditor,   # Glue
            8: AlgorithmParamEditor,   # Length
            10: PinEditor,            # PIN
            12: ShortEditor,           # Short
            13: Match2Editor,          # Match2
            14: OtherEditor,           # Other
            15: OffsetEditor,          # ALOffset
            16: AlgorithmParamEditor,  # Crest
            19: AlgorithmParamEditor,  # IC
        }
        # generic always at index 0
        generic_ed = AlgorithmParamEditor()
        self._editor_stack.addWidget(generic_ed)
        self._editors["generic"] = generic_ed
        self._editor_stack.setCurrentIndex(0)
        layout.addWidget(self._editor_stack)
        self._editor_map = editor_map  # store for dispatch
        return frame

    def _create_menu_bar(self):
        mb = self.menuBar()
        fm = mb.addMenu("文件(&F)")
        fm.addAction(QAction("刷新(&R)", self, triggered=self._load_data))
        fm.addSeparator()
        fm.addAction(QAction("退出(&X)", self, triggered=self.close))
        hm = mb.addMenu("帮助(&H)")
        hm.addAction(QAction("关于(&A)", self, triggered=self._show_about))

    def _apply_styles(self):
        self.setStyleSheet(
            GLOBAL_STYLE + TITLE_STYLE + STATUS_STYLE + CARD_STYLE +
            SUMMARY_STYLE + PARAM_PANEL_STYLE
        )

    def _connect_signals(self):
        self._tree.itemClicked.connect(self._on_tree_clicked)
        self._ng_table.cellClicked.connect(self._on_ng_clicked)
        self._algor_table.cellClicked.connect(self._on_algor_clicked)
        self._search_input.textChanged.connect(self._on_search)
        self._btn_save_db.clicked.connect(self._save_to_db)
        self._btn_export.clicked.connect(self._export_csv)

    # ═════════════════════════════════════════════════════════════
    #  数据加载
    # ═════════════════════════════════════════════════════════════

    def _load_data(self):
        try:
            s = self._db.get_statistics()
            self._summary_widgets["component_count"].setText(str(s["component_count"]))
            self._summary_widgets["ng_record_count"].setText(str(s["ng_record_count"]))
            self._summary_widgets["package_type_count"].setText(str(s["package_type_count"]))
            self._summary_widgets["algorithm_table_count"].setText(str(s["algorithm_table_count"]))
            self._load_component_tree()
        except Exception as e:
            self._status_label.setText(f"加载失败: {e}")

    def _load_component_tree(self):
        self._tree.clear()
        components = self._db.get_all_components()
        pkg_items: dict = {}
        for pkg in self._db.get_package_types():
            cn = self.PACKAGE_CN.get(pkg, pkg)
            item = QTreeWidgetItem([cn])
            item.setData(0, Qt.UserRole, pkg)  # 存原始英文名
            item.setFlags(item.flags() | Qt.ItemIsEnabled)
            f = QFont(); f.setBold(True); item.setFont(0, f)
            self._tree.addTopLevelItem(item)
            pkg_items[pkg] = item
        for c in components:
            pkg = c["PackageType"]
            if pkg in pkg_items:
                child = QTreeWidgetItem([c["Component_Name"]])
                child.setData(0, Qt.UserRole, c["Component_Name"])
                w, h = c.get("Component_Width", 0) or 0, c.get("Component_Height", 0) or 0
                cn_pkg = self.PACKAGE_CN.get(pkg, pkg)
                child.setToolTip(0, f"名称: {c['Component_Name']}\n封装: {cn_pkg}\n尺寸: {w:.3f}×{h:.3f} mm")
                pkg_items[pkg].addChild(child)
        self._tree.expandAll()

    # ═════════════════════════════════════════════════════════════
    #  交互
    # ═════════════════════════════════════════════════════════════

    def _on_tree_clicked(self, item: QTreeWidgetItem, col: int):
        comp_name = item.data(0, Qt.UserRole)
        if comp_name is None: return
        self._current_component = comp_name
        self._current_algo_table = None
        self._status_label.setText(f"已选择: {comp_name}")
        self._show_component_info(comp_name)
        self._show_component_image(comp_name)
        self._populate_ng_table(comp_name)
        self._algor_table.setRowCount(0)
        self._algo_type_badge.setText("")
        self._algo_ng_badge.setText("")
        editor = self._editors.get("generic")
        if editor and isinstance(editor, AlgorithmParamEditor):
            editor._show_placeholder("点击上方检测项 → 查看算法参数 → 点击参数行编辑")

    def _on_search(self, text: str):
        text = text.strip().lower()
        for i in range(self._tree.topLevelItemCount()):
            pkg_item = self._tree.topLevelItem(i)
            any_visible = False
            for j in range(pkg_item.childCount()):
                child = pkg_item.child(j)
                match = (not text) or (text in child.text(0).lower())
                child.setHidden(not match)
                if match: any_visible = True
            pkg_item.setHidden(not any_visible)

    def _show_component_info(self, comp_name: str):
        comp = self._db.get_component_by_name(comp_name)
        if not comp: return
        fields = [
            ("名称", comp.get("Component_Name", "")),
            ("封装类型", self.PACKAGE_CN.get(comp.get("PackageType", ""), comp.get("PackageType", ""))),
            ("宽度", f"{comp.get('Component_Width', 0):.4f} mm"),
            ("高度", f"{comp.get('Component_Height', 0):.4f} mm"),
            ("裁剪区 XY", f"({comp.get('Crop_Area_X', 0):.1f}, {comp.get('Crop_Area_Y', 0):.1f})"),
            ("裁剪角度", f"{comp.get('Crop_Area_Angle', 0):.2f}°"),
            ("图像尺寸", f"{comp.get('Component_Image_Width', 0):.0f}×{comp.get('Component_Image_Height', 0):.0f} px"),
            ("模板标记", "是 ✓" if comp.get("Template_Flag") else "否"),
            ("模板图", "有" if comp.get("Component_Image") else "无"),
            ("HG图", "有" if comp.get("HG_Image") else "无"),
        ]
        self._info_table.setRowCount(len(fields))
        for i, (k, v) in enumerate(fields):
            self._info_table.setItem(i, 0, QTableWidgetItem(k))
            vi = QTableWidgetItem(str(v))
            if i == 0: f = QFont(); f.setBold(True); vi.setFont(f)
            self._info_table.setItem(i, 1, vi)
        self._info_table.resizeColumnsToContents()
        self._info_table.horizontalHeader().setStretchLastSection(True)

    def _show_component_image(self, comp_name: str):
        comp = self._db.get_component_by_name(comp_name)
        if not comp:
            return

        for blob_key in ("Component_Image", "HG_Image"):
            blob = comp.get(blob_key)
            if not blob:
                continue
            try:
                w = int(comp.get("Component_Image_Width", 0))
                h = int(comp.get("Component_Image_Height", 0))
                # 数据库存储的是原始 RGB 像素数据（参考原C++: aoi::Color::RGB）
                if w > 0 and h > 0 and len(blob) == w * h * 3:
                    img = QImage(bytes(blob), w, h, w * 3, QImage.Format_RGB888)
                else:
                    # 尝试作为编码图像解码
                    img = QImage.fromData(bytes(blob))
                if img.isNull():
                    continue
                pixmap = QPixmap.fromImage(img)
                mw = max(self._image_label.width() - 16, 200)
                mh = max(self._image_label.height() - 16, 100)
                scaled = pixmap.scaled(mw, mh, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self._image_label.setPixmap(scaled)
                self._image_label.setAlignment(Qt.AlignCenter)
                return
            except Exception:
                continue

        self._image_label.setText("无图像数据")

    # ═════════════════════════════════════════════════════════════
    #  检测项列表 & 算法参数列表（参考 RefCompoNGTable / RefCompAlgorTable）
    # ═════════════════════════════════════════════════════════════

    # 封装类型→中文
    PACKAGE_CN = {
        "CHIP_R": "电阻", "CHIP_C": "电容", "DIODE": "二极管",
        "TR": "三极管", "MELF": "色环电阻", "SOP": "SOP", "QFP": "QFP",
        "BGA": "BGA", "LED": "LED", "PLUGINUNIT": "插件",
        "SINGLERECT": "单框", "SOLDERJOINT": "焊点", "OTHER": "其它",
    }
    # 算法类型枚举(1-based)→名称
    ALGO_TYPE_NAMES = {
        1: "TOC", 2: "Match", 3: "Histogram", 4: "OCV",
        5: "Compare", 6: "Distance", 7: "Glue", 8: "Length",
        9: "Padplace", 10: "PIN", 11: "Pole", 12: "Short",
        13: "Match2", 14: "Other", 15: "ALOffset", 16: "Crest",
        17: "Hole", 18: "MacroSM", 19: "IC", 20: "Inspection3D",
    }
    # 缺陷类型枚举(1-based)→中文
    DEFECT_TYPE_NAMES = {
        1: "偏移", 2: "缺件", 3: "错件", 4: "少锡",
        5: "空焊", 6: "反向", 7: "旋转", 8: "异物",
        9: "损坏", 10: "多锡", 11: "多件", 12: "虚焊",
        13: "溢胶", 14: "起翘", 15: "短路", 16: "立碑",
        17: "反白", 18: "漏铜", 19: "锡少", 20: "全检",
        21: "润湿不良", 22: "侧立",
    }

    def _populate_ng_table(self, comp_name: str):
        """上方检测项列表: 每行=一个NG_ID，参考 RefCompoNGTable"""
        self._ng_table.setRowCount(0)
        rows = self._db.get_algorithm_params("COMMON_ALGORITHM_PARAMETER", comp_name)
        if not rows: return

        # 按 NG_ID 分组，每NG取 Use=1 的作为"当前使用算法"
        ng_groups: dict = {}
        for r in rows:
            ng_id = r.get("No_Good_Id", "")
            if ng_id not in ng_groups:
                ng_groups[ng_id] = {"defect_type": r.get("Defect_Type", 0),
                                    "use_algo": None, "all_algos": []}
            ng_groups[ng_id]["all_algos"].append(r)
            if r.get("Algorithm_Use_Flag"):
                ng_groups[ng_id]["use_algo"] = r.get("Algorithm_Type", 0)

        self._ng_table.setRowCount(len(ng_groups))
        for i, (ng_id, gdata) in enumerate(ng_groups.items()):
            dt = gdata["defect_type"]
            defect_cn = self.DEFECT_TYPE_NAMES.get(dt, str(dt))
            algo_type = gdata["use_algo"] or 0
            algo_name = self.ALGO_TYPE_NAMES.get(algo_type, str(algo_type))

            self._ng_table.setItem(i, 0, QTableWidgetItem(defect_cn))
            self._ng_table.setItem(i, 1, QTableWidgetItem(ng_id))
            self._ng_table.setItem(i, 2, QTableWidgetItem("Register"))
            self._ng_table.setItem(i, 3, QTableWidgetItem("—"))
            self._ng_table.setItem(i, 4, QTableWidgetItem(algo_name))
            # 存储
            self._ng_table.item(i, 0).setData(Qt.UserRole, {
                "ng_id": ng_id, "defect_type": dt, "use_algo": algo_type})

        self._ng_table.resizeColumnsToContents()
        if ng_groups:
            self._ng_table.selectRow(0)
            self._populate_algor_table(comp_name, list(ng_groups.keys())[0])

    def _on_ng_clicked(self, row: int, col: int):
        """点击检测项行 → 刷新下方算法参数列表，同时在模板图上绘制红色ROI框"""
        item = self._ng_table.item(row, 0)
        if not item: return
        data = item.data(Qt.UserRole)
        if not data: return
        ng_id = data["ng_id"]
        self._populate_algor_table(self._current_component, ng_id)
        # 绘制 ROI
        self._show_component_image_with_roi(self._current_component, ng_id)

    def _show_component_image_with_roi(self, comp_name: str, ng_id: str):
        """显示模板图像并绘制红色ROI框
           BD001(偏移)的ROI中心=图像中心，其他NG相对于BD001偏移"""
        comp = self._db.get_component_by_name(comp_name)
        if not comp: return

        # 获取分辨率
        ngs = self._db.get_ng_records(comp_name)
        resolution = 15.0
        for ng in ngs:
            if ng.get("Resolution"):
                resolution = float(ng["Resolution"])
                break
        factor = 1000.0 / resolution if resolution > 0 else 1.0

        # BD001(偏移)的ROI作为参考中心
        bd001_roi = self._db.get_ng_roi(comp_name, "BD001")
        has_bd001 = bd001_roi["w"] > 0

        # 当前NG的ROI
        current_roi = self._db.get_ng_roi(comp_name, ng_id)
        if not current_roi["w"] and not current_roi["h"]:
            return

        # 加载图像
        for blob_key in ("Component_Image", "HG_Image"):
            blob = comp.get(blob_key)
            if not blob: continue
            try:
                w = int(comp.get("Component_Image_Width", 0))
                h = int(comp.get("Component_Image_Height", 0))
                if w > 0 and h > 0 and len(blob) == w * h * 3:
                    img = QImage(bytes(blob), w, h, w * 3, QImage.Format_RGB888)
                else:
                    img = QImage.fromData(bytes(blob))
                if img.isNull(): continue

                mw = max(self._image_label.width() - 16, 200)
                mh = max(self._image_label.height() - 16, 100)
                scaled = img.scaled(mw, mh, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                pixmap = QPixmap.fromImage(scaled)

                sx = scaled.width() / img.width() if img.width() else 1
                sy = scaled.height() / img.height() if img.height() else 1

                # BD001中心=图像中心；其他NG=图像中心+(当前ROI偏移-BD001偏移)
                img_cx = w / 2.0
                img_cy = h / 2.0

                if has_bd001 and ng_id != "BD001":
                    dx_mm = current_roi["x"] - bd001_roi["x"]
                    dy_mm = current_roi["y"] - bd001_roi["y"]
                    cx_px = img_cx + dx_mm * factor
                    cy_px = img_cy + dy_mm * factor
                else:
                    cx_px = img_cx + current_roi["x"] * factor
                    cy_px = img_cy + current_roi["y"] * factor

                # 左上角=中心-半宽高
                rw_px = current_roi["w"] * factor
                rh_px = current_roi["h"] * factor

                if rw_px > 0 and rh_px > 0:
                    painter = QPainter(pixmap)
                    painter.setPen(QPen(QColor(255, 0, 0), 2))
                    rx = (cx_px - rw_px / 2) * sx
                    ry = (cy_px - rh_px / 2) * sy
                    painter.drawRect(int(rx), int(ry), int(rw_px * sx), int(rh_px * sy))
                    painter.setPen(QPen(QColor(255, 200, 0), 1))
                    painter.drawText(int(rx), max(0, int(ry) - 4), f"ROI {ng_id}")
                    painter.end()

                self._image_label.setPixmap(pixmap)
                self._image_label.setAlignment(Qt.AlignCenter)
                return
            except Exception:
                continue

        self._image_label.setText("无图像数据")

    def _populate_algor_table(self, comp_name: str, ng_id: str):
        """下方算法参数列表: 每行=一个AlgorithmType，参考 RefCompAlgorTable"""
        self._algor_table.setRowCount(0)
        rows = self._db.get_algorithm_params("COMMON_ALGORITHM_PARAMETER", comp_name)
        matched = [r for r in rows if r.get("No_Good_Id", "") == ng_id]
        if not matched: return

        pkg = self._current_component and self._db.get_component_by_name(comp_name)
        pkg_cn = self.PACKAGE_CN.get(pkg.get("PackageType", ""), "") if pkg else ""
        defect_type = matched[0].get("Defect_Type", 0)
        defect_cn = self.DEFECT_TYPE_NAMES.get(defect_type, str(defect_type))

        # 去重: 每个 AlgorithmType 一行
        seen, display = set(), []
        for r in matched:
            at = r.get("Algorithm_Type", 0)
            if at not in seen:
                seen.add(at)
                display.append(r)

        self._algor_table.setRowCount(len(display))
        for i, r in enumerate(display):
            at = r.get("Algorithm_Type", 0)
            algo_name = self.ALGO_TYPE_NAMES.get(at, str(at))
            use_flag = r.get("Algorithm_Use_Flag", 0)

            self._algor_table.setItem(i, 0, QTableWidgetItem(comp_name))
            self._algor_table.setItem(i, 1, QTableWidgetItem(pkg_cn))
            self._algor_table.setItem(i, 2, QTableWidgetItem(defect_cn))
            self._algor_table.setItem(i, 3, QTableWidgetItem(ng_id))
            self._algor_table.setItem(i, 4, QTableWidgetItem(algo_name))
            # Use checkbox — 互斥：同NG下只能一个激活
            cb = QCheckBox()
            cb.setChecked(bool(use_flag))
            cb.toggled.connect(lambda checked, r=i, ng=ng_id, at=at:
                               self._on_use_toggled(r, checked, ng))
            self._algor_table.setCellWidget(i, 5, cb)
            self._algor_table.setItem(i, 6, QTableWidgetItem(str(r.get("Search_Scope_X", ""))))
            self._algor_table.setItem(i, 7, QTableWidgetItem(str(r.get("Search_Scope_Y", ""))))
            self._algor_table.setItem(i, 8, QTableWidgetItem("—"))
            self._algor_table.setItem(i, 9, QTableWidgetItem("—"))
            # 存储
            self._algor_table.item(i, 0).setData(Qt.UserRole, {
                "table": "COMMON_ALGORITHM_PARAMETER",
                "algo_type": at, "ng_id": ng_id,
                "full_row": r})

        self._algor_table.resizeColumnsToContents()

    def _on_use_toggled(self, row: int, checked: bool, ng_id: str):
        """USE checkbox互斥：同NG_ID下只能一个算法激活"""
        if not checked:
            return  # 取消勾选不管
        # 取消其它行的勾选
        for i in range(self._algor_table.rowCount()):
            if i == row: continue
            w = self._algor_table.cellWidget(i, 5)
            if isinstance(w, QCheckBox):
                w.blockSignals(True)
                w.setChecked(False)
                w.blockSignals(False)
        # 直接写入DB
        try:
            self._db.clear_use_flags_for_ng(self._current_component, ng_id)
            item = self._algor_table.item(row, 0)
            new_algo_type = None
            if item:
                data = item.data(Qt.UserRole)
                if data:
                    new_algo_type = data["algo_type"]
                    self._db.update_algorithm_use_flag(
                        self._current_component, ng_id, new_algo_type, True)
            # 更新上方检测项列表的算法显示
            for i in range(self._ng_table.rowCount()):
                ng_item = self._ng_table.item(i, 1)
                if ng_item and ng_item.text() == ng_id:
                    algo_name = self.ALGO_TYPE_NAMES.get(new_algo_type or 0, str(new_algo_type or ""))
                    self._ng_table.setItem(i, 4, QTableWidgetItem(algo_name))
                    break
            self._status_label.setText(f"已切换默认算法 (NG:{ng_id})")
        except Exception as e:
            self._status_label.setText(f"USE写入失败: {e}")

    def _on_algor_clicked(self, row: int, col: int):
        """点击算法参数行 → 根据算法类型加载对应专用编辑器"""
        item = self._algor_table.item(row, 0)
        if not item: return
        data = item.data(Qt.UserRole)
        if not data: return

        algo_type = data["algo_type"]
        ng_id = data["ng_id"]
        common_row = data["full_row"]
        algo_name = self.ALGO_TYPE_NAMES.get(algo_type, f"Algo{algo_type}")

        # 算法表映射
        algo_table_map = {
            1: "TOC_ALGORITHM_PARAMETER", 2: "MATCH_ALGORITHM_PARAMETER",
            3: "HISTOGRAM_ALGORITHM_PARAMETER", 4: "OCV_ALGORITHM_PARAMETER",
            5: "COMPARE_ALGORITHM_PARAMETER", 7: "GLUE_ALGORITHM_PARAMETER",
            8: "LENGTH_ALGORITHM_PARAMETER", 10: "PIN_ALGORITHM_PARAMETER",
            12: "SHORT_ALGORITHM_PARAMETER", 13: "MATCH2_ALGORITHM_PARAMETER",
            14: "OTHER_ALGORITHM_PARAMETER", 15: "ALOFFSET_ALGORITHM_PARAMETER",
            16: "CREST_ALGORITHM_PARAMETER", 19: "IC_ALGORITHM_PARAMETER",
        }
        target_table = algo_table_map.get(algo_type, "COMMON")

        self._current_algo_table = target_table

        # ── 获取目标表参数 ──
        params = self._db.get_algorithm_params(target_table, self._current_component)
        matched = [p for p in params if p.get("No_Good_Id", "") == ng_id]
        param_row = matched[0] if matched else {}

        # ── 获取/创建专用编辑器 ──
        editor_cls = self._editor_map.get(algo_type)
        if editor_cls is None:
            editor_cls = AlgorithmParamEditor

        editor_key = f"{algo_type}"
        if editor_key not in self._editors:
            ed = editor_cls()
            self._editor_stack.addWidget(ed)
            self._editors[editor_key] = ed

        editor = self._editors[editor_key]

        # ── 加载参数 ──
        if algo_type == 1:  # TOC: 特殊处理
            toc_params_list = self._db.get_algorithm_params("TOC_ALGORITHM_PARAMETER", self._current_component)
            toc_matched = [p for p in toc_params_list if p.get("No_Good_Id", "") == ng_id]
            toc_params = toc_matched[0] if toc_matched else {}
            editor.load_params(common_row, toc_params)
        elif isinstance(editor, AlgorithmParamEditor):
            editor.load_algorithm(target_table, matched)
        else:
            # 合并 COMMON 和目标表参数
            merged = dict(common_row)
            merged.update(param_row)
            editor.load_params(merged)

        self._editor_stack.setCurrentWidget(editor)
        # 更新顶部标签
        self._algo_title.setText(f"算法参数编辑")
        self._algo_type_badge.setText(algo_name)
        self._algo_ng_badge.setText(f"NG:{ng_id}")
        self._status_label.setText(f"编辑中: {self._current_component} → {algo_name} (NG:{ng_id})")

    def _save_to_db(self):
        """将当前编辑器的修改写回数据库"""
        if not self._current_algo_table or not self._current_component:
            QMessageBox.information(self, "提示", "请先选择元器件和算法参数")
            return

        editor = self._editor_stack.currentWidget()
        if not editor:
            return

        # 获取当前NG_ID
        ng_id = ""
        for i in range(self._algor_table.rowCount()):
            item = self._algor_table.item(i, 0)
            if item:
                data = item.data(Qt.UserRole)
                if data and f"{data.get('algo_type','')}" == f"{self._current_algo_table or ''}":
                    pass  # not quite right, use first NG_ID instead
                if data:
                    ng_id = data.get("ng_id", "")
                    break

        if not ng_id:
            QMessageBox.warning(self, "警告", "无法确定当前NG_ID")
            return

        try:
            if isinstance(editor, AlgorithmParamEditor):
                values = editor.collect_values()
                for row_data in values:
                    self._db.update_algorithm_param(
                        self._current_algo_table, self._current_component, ng_id, row_data)
                    self._db.update_cache(
                        self._current_algo_table, self._current_component, ng_id, row_data)
            elif isinstance(editor, TocAlgorithmEditor):
                vals = editor.collect_values()
                # Update COMMON
                self._db.update_algorithm_param("COMMON_ALGORITHM_PARAMETER",
                    self._current_component, ng_id, vals["common"])
                self._db.update_cache("COMMON_ALGORITHM_PARAMETER",
                    self._current_component, ng_id, vals["common"])
                # Update TOC
                self._db.update_algorithm_param("TOC_ALGORITHM_PARAMETER",
                    self._current_component, ng_id, vals["toc"])
                self._db.update_cache("TOC_ALGORITHM_PARAMETER",
                    self._current_component, ng_id, vals["toc"])
            else:
                # Other custom editors
                vals = editor.collect_values()
                self._db.update_algorithm_param(self._current_algo_table,
                    self._current_component, ng_id, vals)
                self._db.update_cache(self._current_algo_table,
                    self._current_component, ng_id, vals)

            QMessageBox.information(self, "保存成功",
                f"已更新参数到数据库\n表: {self._current_algo_table}")
            self._status_label.setText(f"已保存: {self._current_algo_table}")
        except Exception as e:
            QMessageBox.critical(self, "保存失败", str(e))

    def _export_csv(self):
        from datetime import datetime
        import csv
        try:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            fn = f"元器件模板库_导出_{ts}.csv"
            comps = self._db.get_all_components()
            with open(fn, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.DictWriter(f, fieldnames=comps[0].keys())
                w.writeheader(); w.writerows(comps)
            QMessageBox.information(self, "导出成功", f"已导出 {len(comps)} 条到:\n{os.path.abspath(fn)}")
            self._status_label.setText(f"已导出: {fn}")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", str(e))

    def _show_about(self):
        QMessageBox.about(self, "关于",
            "<h2>元器件模板库管理系统 v3.0</h2>"
            "<p>AOI 元器件模板库管理，支持算法参数编辑。</p>"
            "<p>启动全量缓存 · 动态算法编辑 · 深色主题</p>"
            "<hr><p style='color:#8b949e;'>Python + PySide6 + SQLite</p>")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._current_component:
            self._show_component_image(self._current_component)


def run_app(db_path: str):
    app = QApplication(sys.argv)
    app.setApplicationName("ComponentTemplateManager")
    app.setFont(QFont("Microsoft YaHei", 10))
    window = MainWindow(db_path)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    # 直接运行时自动找数据库
    import os as _os
    _this_dir = _os.path.dirname(_os.path.abspath(__file__))
    _db = _os.path.join(_this_dir, "..", "..", "素材库", "Component.db")
    if not _os.path.exists(_db):
        _db = _os.path.join(_this_dir, "..", "Component.db")
    if not _os.path.exists(_db):
        print("错误: 未找到 Component.db，请用 main.py 启动并指定 --db 路径")
        sys.exit(1)
    run_app(_os.path.abspath(_db))
