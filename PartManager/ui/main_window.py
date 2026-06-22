"""
元器件模板库管理系统 - 主窗口 v3
"""

import sys, os
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem,
    QTabWidget, QLabel, QPushButton, QStatusBar,
    QHeaderView, QFrame, QGridLayout, QGroupBox, QMessageBox,
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

        # ── 上方：元件总标准表 ──
        master_lbl = QLabel("📋 元件总标准表（点击行查看分项检测项）")
        master_lbl.setStyleSheet("font-weight:bold; font-size:12px; color:#58a6ff; padding:1px 4px;")
        layout.addWidget(master_lbl)

        self._master_table = QTableWidget()
        self._master_table.setColumnCount(8)
        self._master_table.setHorizontalHeaderLabels(
            ["NG_ID", "算法", "Use", "ROI_X", "ROI_Y", "角度", "缺陷类型", "表达式"])
        self._master_table.horizontalHeader().setStretchLastSection(True)
        self._master_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._master_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._master_table.verticalHeader().setVisible(False)
        self._master_table.setMaximumHeight(140)
        layout.addWidget(self._master_table)

        # ── 下方：分项检测项表 ──
        detail_lbl = QLabel("🔍 分项检测项表（点击行编辑算法参数）")
        detail_lbl.setStyleSheet("font-weight:bold; font-size:12px; color:#58a6ff; padding:1px 4px;")
        layout.addWidget(detail_lbl)

        self._detail_table = QTableWidget()
        self._detail_table.setColumnCount(5)
        self._detail_table.setHorizontalHeaderLabels(
            ["检测项", "子名称(NG)", "算法表", "NG_ID", "参数预览"])
        self._detail_table.horizontalHeader().setStretchLastSection(True)
        self._detail_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._detail_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._detail_table.verticalHeader().setVisible(False)
        layout.addWidget(self._detail_table)

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
        self._master_table.itemClicked.connect(self._on_master_clicked)
        self._detail_table.itemClicked.connect(self._on_detail_clicked)
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
            item = QTreeWidgetItem([pkg])
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
                child.setToolTip(0, f"名称: {c['Component_Name']}\n封装: {pkg}\n尺寸: {w:.3f}×{h:.3f} mm\n模板: {'✓' if c.get('Template_Flag') else '✗'}")
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
        self._populate_master_table(comp_name)
        self._detail_table.setRowCount(0)
        self._algo_editor._show_placeholder("点击上方总标准表行→查看分项检测项→点击分项行编辑参数")

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
            ("封装类型", comp.get("PackageType", "")),
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
    #  总标准表 & 分项检测项表
    # ═════════════════════════════════════════════════════════════

    # 算法类型名称映射
    ALGO_TYPE_NAMES = {2: "Match", 13: "TOC", 14: "OCV", 1: "定位", 3: "少锡", 4: "错件"}
    DEFECT_TYPE_NAMES = {1: "偏移", 2: "少锡", 3: "错件", 4: "极性", 5: "其他"}

    def _populate_master_table(self, comp_name: str):
        """填充上方总标准表：从 COMMON_ALGORITHM_PARAMETER 载入"""
        self._master_table.setRowCount(0)
        rows = self._db.get_algorithm_params("COMMON_ALGORITHM_PARAMETER", comp_name)
        if not rows:
            return

        # 按 NG_ID + Algorithm_Type 去重展示
        seen = set()
        display_rows = []
        for r in rows:
            key = (r.get("No_Good_Id", ""), r.get("Algorithm_Type", 0))
            if key not in seen:
                seen.add(key)
                display_rows.append(r)

        self._master_table.setRowCount(len(display_rows))
        for i, r in enumerate(display_rows):
            algo_type = r.get("Algorithm_Type", 0)
            algo_name = self.ALGO_TYPE_NAMES.get(algo_type, str(algo_type))
            use_flag = "✓" if r.get("Algorithm_Use_Flag") else "✗"
            defect = self.DEFECT_TYPE_NAMES.get(r.get("Defect_Type", 0), str(r.get("Defect_Type", "")))

            self._master_table.setItem(i, 0, QTableWidgetItem(str(r.get("No_Good_Id", ""))))
            self._master_table.setItem(i, 1, QTableWidgetItem(algo_name))
            self._master_table.setItem(i, 2, QTableWidgetItem(use_flag))
            self._master_table.setItem(i, 3, QTableWidgetItem(str(r.get("Search_Scope_X", ""))))
            self._master_table.setItem(i, 4, QTableWidgetItem(str(r.get("Search_Scope_Y", ""))))
            self._master_table.setItem(i, 5, QTableWidgetItem(str(r.get("Search_Scope_Angle", ""))))
            self._master_table.setItem(i, 6, QTableWidgetItem(defect))
            self._master_table.setItem(i, 7, QTableWidgetItem(str(r.get("Error_Exp", ""))[:30]))

            # 存储完整数据
            self._master_table.item(i, 0).setData(Qt.UserRole, r)

        self._master_table.resizeColumnsToContents()

    def _on_master_clicked(self, item: QTableWidgetItem):
        """点击总标准表行 → 填充分项检测项表"""
        row = item.row()
        master_data = self._master_table.item(row, 0).data(Qt.UserRole)
        if not master_data: return

        ng_id = master_data.get("No_Good_Id", "")
        comp_name = self._current_component
        if not comp_name: return

        self._populate_detail_table(comp_name, ng_id)

    def _populate_detail_table(self, comp_name: str, ng_id: str):
        """填充下方分项检测项表：所有匹配此 NG_ID 的算法表记录"""
        self._detail_table.setRowCount(0)
        algos = self._db.get_algorithms_for_component(comp_name)
        if not algos: return

        detail_rows = []
        for table_name, params in algos.items():
            for p in params:
                if p.get("No_Good_Id", "") == ng_id:
                    short = ALGORITHM_SHORT_NAMES.get(table_name, table_name)
                    # 参数预览：取前3个非基础字段的值
                    preview_parts = []
                    for k, v in p.items():
                        if k in ("Component_Name", "No_Good_Id"): continue
                        preview_parts.append(f"{k}={v}")
                        if len(preview_parts) >= 3: break
                    preview = ", ".join(preview_parts) if preview_parts else "—"

                    detail_rows.append({
                        "table": table_name,
                        "short": short,
                        "ng_id": ng_id,
                        "preview": preview,
                        "params": params,  # all params for this table
                        "full_row": p,
                    })

        self._detail_table.setRowCount(len(detail_rows))
        for i, dr in enumerate(detail_rows):
            self._detail_table.setItem(i, 0, QTableWidgetItem(dr["short"]))
            self._detail_table.setItem(i, 1, QTableWidgetItem(dr["ng_id"]))
            self._detail_table.setItem(i, 2, QTableWidgetItem(dr["table"]))
            self._detail_table.setItem(i, 3, QTableWidgetItem(dr["ng_id"]))
            self._detail_table.setItem(i, 4, QTableWidgetItem(dr["preview"]))
            self._detail_table.item(i, 0).setData(Qt.UserRole, dr)

        self._detail_table.resizeColumnsToContents()

    def _on_detail_clicked(self, item: QTableWidgetItem):
        """点击分项检测项行 → 加载算法编辑器"""
        row = item.row()
        dr = self._detail_table.item(row, 0).data(Qt.UserRole)
        if not dr: return

        self._current_algo_table = dr["table"]
        # 只加载当前点击的那一条记录
        self._status_label.setText(f"编辑中: {self._current_component} → {dr['short']} (NG:{dr['ng_id']})")
        self._algo_editor.load_algorithm(dr["table"], [dr["full_row"]])

    def _on_save_algo(self):
        if not self._current_algo_table or not self._algo_editor.current_table:
            QMessageBox.information(self, "提示", "请先在分项检测项表中点击一行选择算法")
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
