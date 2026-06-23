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
from PySide6.QtGui import QFont, QPixmap, QImage, QAction

from db import ComponentDatabase
from ui.styles import GLOBAL_STYLE, TITLE_STYLE, STATUS_STYLE, CARD_STYLE, SUMMARY_STYLE, PARAM_PANEL_STYLE
from ui.algorithm_editor import AlgorithmParamEditor, ALGORITHM_SHORT_NAMES


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
        self._btn_save_algo = QPushButton("💾 收集修改")
        self._btn_save_algo.setObjectName("btnPrimary")
        self._btn_export = QPushButton("📊 导出CSV")
        btn_row.addWidget(self._btn_save_algo)
        btn_row.addWidget(self._btn_export)
        layout.addLayout(btn_row)

        return frame

    def _build_right_panel(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("cardFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(2, 2, 2, 2)

        lbl = QLabel("🔧 算法参数编辑")
        lbl.setStyleSheet("font-weight:bold; font-size:13px; color:#58a6ff; padding:2px 4px;")
        layout.addWidget(lbl)

        self._algo_editor = AlgorithmParamEditor()
        layout.addWidget(self._algo_editor)
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
        self._btn_save_algo.clicked.connect(self._on_save_algo)
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
        self._algo_editor._show_placeholder("点击上方检测项 → 查看算法参数 → 点击参数行编辑")

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
        """点击检测项行 → 刷新下方算法参数列表"""
        item = self._ng_table.item(row, 0)
        if not item: return
        data = item.data(Qt.UserRole)
        if not data: return
        self._populate_algor_table(self._current_component, data["ng_id"])

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
            # Use checkbox
            cb = QCheckBox()
            cb.setChecked(bool(use_flag))
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

    def _on_algor_clicked(self, row: int, col: int):
        """点击算法参数行 → 加载对应算法表的具体参数到编辑器"""
        item = self._algor_table.item(row, 0)
        if not item: return
        data = item.data(Qt.UserRole)
        if not data: return

        algo_type = data["algo_type"]
        ng_id = data["ng_id"]
        algo_name = self.ALGO_TYPE_NAMES.get(algo_type, f"Algo{algo_type}")

        # 根据算法类型找到对应的算法参数表
        algo_table_map = {
            1: "TOC_ALGORITHM_PARAMETER", 2: "MATCH_ALGORITHM_PARAMETER",
            3: "HISTOGRAM_ALGORITHM_PARAMETER", 4: "OCV_ALGORITHM_PARAMETER",
            5: "COMPARE_ALGORITHM_PARAMETER", 6: "DISTANCE_ALGORITHM_PARAMETER",
            7: "GLUE_ALGORITHM_PARAMETER", 8: "LENGTH_ALGORITHM_PARAMETER",
            9: "PADPLACE_ALGORITHM_PARAMETER", 10: "PIN_ALGORITHM_PARAMETER",
            11: "POLE_ALGORITHM_PARAMETER", 12: "SHORT_ALGORITHM_PARAMETER",
            13: "MATCH2_ALGORITHM_PARAMETER", 14: "OTHER_ALGORITHM_PARAMETER",
            15: "ALOFFSET_ALGORITHM_PARAMETER", 16: "CREST_ALGORITHM_PARAMETER",
            17: "HOLE_ALGORITHM_PARAMETER", 18: "MACROSM_ALGORITHM_PARAMETER",
            19: "IC_ALGORITHM_PARAMETER", 20: "INSPECTION3D_ALGORITHM_PARAMETER",
        }
        target_table = algo_table_map.get(algo_type)
        if not target_table:
            # 回退到 COMMON
            target_table = "COMMON_ALGORITHM_PARAMETER"

        self._current_algo_table = target_table
        params = self._db.get_algorithm_params(target_table, self._current_component)
        matched = [p for p in params if p.get("No_Good_Id", "") == ng_id]

        self._status_label.setText(
            f"编辑中: {self._current_component} → {algo_name} (NG:{ng_id})")
        self._algo_editor.load_algorithm(target_table, matched)

    def _on_save_algo(self):
        if not self._current_algo_table or not self._algo_editor.current_table:
            QMessageBox.information(self, "提示", "请先在算法参数列表中点击一行选择算法")
            return
        values = self._algo_editor.collect_values()
        QMessageBox.information(self, "参数收集完成",
            f"算法: {self._algo_editor.current_table}\n"
            f"元器件: {self._current_component}\n"
            f"共 {len(values)} 条记录\n\n"
            f"当前为只读模式，写入功能可后续扩展。")
        self._status_label.setText(f"已收集 {len(values)} 条参数修改")

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
