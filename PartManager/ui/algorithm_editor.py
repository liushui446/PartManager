"""
元器件模板库管理系统 - 动态算法参数编辑器（匹配真实数据库schema）
"""

from typing import Dict, List, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea,
    QGroupBox, QLabel, QSlider, QSpinBox, QDoubleSpinBox,
    QComboBox, QPushButton, QFrame, QLineEdit, QCheckBox,
)
from PySide6.QtCore import Qt, Signal

# ─── 算法中文名 ───

ALGORITHM_CN_NAMES: Dict[str, str] = {
    "CREST_ALGORITHM_PARAMETER": "波峰焊检测 (CREST)",
    "SHORT_ALGORITHM_PARAMETER": "短路检测 (SHORT)",
    "MATCH_ALGORITHM_PARAMETER": "模板匹配 (MATCH)",
    "MATCH2_ALGORITHM_PARAMETER": "二次匹配 (MATCH2)",
    "PIN_ALGORITHM_PARAMETER": "引脚检测 (PIN)",
    "IC_ALGORITHM_PARAMETER": "IC检测 (IC)",
    "OCV_ALGORITHM_PARAMETER": "OCV字符检测",
    "TOC_ALGORITHM_PARAMETER": "TOC检测",
    "OTHER_ALGORITHM_PARAMETER": "其他缺陷检测",
    "LENGTH_ALGORITHM_PARAMETER": "长度检测",
    "ALOFFSET_ALGORITHM_PARAMETER": "偏移检测",
    "CODEDETECT_ALGORITHM_PARAMETER": "条码检测",
    "MACROSM_ALGORITHM_PARAMETER": "宏观检测",
    "HISTOGRAM_ALGORITHM_PARAMETER": "直方图检测",
    "COMMON_ALGORITHM_PARAMETER": "通用算法参数",
    "COMPARE_ALGORITHM_PARAMETER": "对比检测",
}

ALGORITHM_SHORT_NAMES: Dict[str, str] = {
    "CREST_ALGORITHM_PARAMETER": "波峰焊", "SHORT_ALGORITHM_PARAMETER": "短路",
    "MATCH_ALGORITHM_PARAMETER": "匹配", "MATCH2_ALGORITHM_PARAMETER": "二次匹配",
    "PIN_ALGORITHM_PARAMETER": "引脚", "IC_ALGORITHM_PARAMETER": "IC",
    "OCV_ALGORITHM_PARAMETER": "OCV", "TOC_ALGORITHM_PARAMETER": "TOC",
    "OTHER_ALGORITHM_PARAMETER": "其他缺陷", "LENGTH_ALGORITHM_PARAMETER": "长度",
    "ALOFFSET_ALGORITHM_PARAMETER": "偏移", "CODEDETECT_ALGORITHM_PARAMETER": "条码",
    "MACROSM_ALGORITHM_PARAMETER": "宏观", "HISTOGRAM_ALGORITHM_PARAMETER": "直方图",
    "COMMON_ALGORITHM_PARAMETER": "通用", "COMPARE_ALGORITHM_PARAMETER": "对比",
}

# 算法表中需要跳过不显示的列
SKIP_COLUMNS = {"Component_Name", "No_Good_Id"}


def _spin(val, lo=-99999, hi=99999):
    """创建整数spinbox"""
    s = QSpinBox(); s.setRange(lo, hi)
    try: s.setValue(int(val or 0))
    except (ValueError, TypeError): s.setValue(0)
    return s


def _dspin(val, lo=-99999.0, hi=99999.0):
    """创建浮点spinbox"""
    s = QDoubleSpinBox(); s.setDecimals(3); s.setRange(lo, hi)
    try: s.setValue(float(val or 0))
    except (ValueError, TypeError): s.setValue(0.0)
    return s


def _make_field_label(key: str) -> str:
    """将数据库列名转为可读中文标签"""
    cn_map = {
        "Brightness": "亮度", "Contrast": "对比度", "Enhance": "增强",
        "Gray": "灰度", "Value": "阈值", "Correct_Mode": "校正模式",
        "Detection_Type": "检测类型", "Board_Color": "板材颜色",
        "Mini_Width": "最小宽度", "Pin_Width": "引脚宽度",
        "Project_Threshold": "投影阈值", "Diff_Threshold": "差值阈值",
        "Allow_Auto_Calculate": "允许自动计算",
        "Solder_Brige_Method": "锡桥检测法",
        "Diff_Current": "差值电流", "Average_Brightness": "平均亮度",
        "Straight_Thread_Number": "直线引脚数",
        "Straight_Thread_Number_Current": "当前直线引脚数",
        "Observe": "观察模式",
        "Defect_Type": "缺陷类型", "Algorithm_Type": "算法类型",
        "Algorithm_Use_Flag": "启用算法", "Color_Channel": "颜色通道",
        "Color_Method": "颜色方法", "Search_Scope_X": "搜索范围X",
        "Search_Scope_Y": "搜索范围Y", "Search_Scope_Angle": "搜索角度",
        "Color_Red_High": "红色上限", "Color_Red_Low": "红色下限",
        "Color_Green_High": "绿色上限", "Color_Green_Low": "绿色下限",
        "Color_Blue_High": "蓝色上限", "Color_Blue_Low": "蓝色下限",
        "Color_Gray_High": "灰度上限", "Color_Gray_Low": "灰度下限",
        "Retrun_Value_High": "返回值上限", "Retrun_Value_Low": "返回值下限",
        "Return_Value": "返回值", "Error_Exp": "错误表达式",
        "Img_Type": "图像类型", "Filter_Level": "滤波级别",
        "Binary_Threshold": "二值化阈值", "Match_Angle": "匹配角度",
        "Match_Score": "匹配分数", "Match_Ratio": "匹配比例",
        "Contour_NumThre": "轮廓数阈值",
        "Enhanced_Detect_State": "增强检测",
        "Zoom_Value": "缩放值", "Char_Ratio": "字符比例",
        "Stand_Image_Width": "标准图宽", "Stand_Image_Height": "标准图高",
        "Polarity": "极性", "Model_Type": "模板类型",
        "Char_DiffThreshold": "字符差分阈值",
        "Lead_Fix": "引脚修正", "Pin_To_Box_Ratio": "引脚盒比例",
        "Upper_Boundary": "上边界", "Lower_Boundary": "下边界",
        "Auto_CalBoundary_Flag": "自动计算边界",
        "Auto_Calculate_Flag": "自动计算",
        "Min_Width": "最小宽度", "Pin_Width_Threshold": "引脚宽阈值",
        "BinThreshold": "二值化阈值",
        "Template_Gray_Mean": "模板灰度均值",
        "Auto_Extract_Color": "自动提取颜色",
        "Histo_Percentile_Pt": "直方图百分位",
        "Intense_Resolution": "强度分辨率",
        "Hue_Resolution": "色调分辨率",
        "Intense_Vary_Tolerance_Factor": "强度变化容差",
        "Hue_Vary_Tolerance_Factor": "色调变化容差",
        "Param_Adapt_Method": "参数自适应方法",
        "Det_Length": "检测长度", "M_Register_Width": "配准宽度",
        "M_Register_Height": "配准高度", "M_Modelimg_Type": "模板图类型",
        "M_Bgr_Model_Meanimg": "BGR均值图",
        "M_Hsv_Model_Stdimg": "HSV标准差图",
        "M_Errorpixelnum_Factor": "错误像素因子",
        "M_Init_Var_Ratio": "初始方差比",
        "Diff_Thre": "差分阈值", "M_Least_Error_Area": "最小错误区域",
        "Detect_DisTAB": "检测距离", "Standard_Length": "标准长度",
        "Projection_Threshold": "投影阈值",
        "Adjust_Intensity": "调节强度", "Adjust_Contrast": "调节对比度",
        "Judge_High": "判定上限", "Judge_Low": "判定下限",
        "Rotio": "旋转比例", "Detect_Method": "检测方法",
        "Gray_Lower": "灰度下限", "Gray_Average": "灰度均值",
        "Gray_Upper": "灰度上限",
        "Init_Judge_Upper": "初始判定上限",
        "Init_Judge_Lower": "初始判定下限",
        "Total_Gray_Average": "总灰度均值",
        "Output_Gray": "输出灰度",
        "Barcode": "条码", "My_Brightness": "亮度",
        "My_Contrast": "对比度", "Color": "颜色模式",
        "Shape": "形状", "Edge_Thresh": "边缘阈值",
        "Pre_Process_Flag": "预处理器", "Auto_Thresh_Flag": "自动阈值",
        "Thresh": "阈值",
        "Detection_Length": "检测长度", "Train_Epoch": "训练轮次",
        "Error_Pixel_Number_Factor": "错误像素因子",
        "OK_Pixel_Ratio": "OK像素比", "Ncc_Match_Ratio": "NCC匹配比",
        "Ncc_Pyramid_Least_Region": "NCC金字塔最小区域",
        "Automatic_Train": "自动训练",
        "Ncc_Match_Lower_Angle": "NCC匹配下限角",
        "Ncc_Match_Upper_Angle": "NCC匹配上限角",
    }
    return cn_map.get(key, key)


class AlgorithmParamEditor(QScrollArea):
    """根据算法类型自动生成编辑表单"""

    param_changed = Signal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("paramScroll")
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)

        self._container = QWidget()
        self._container.setObjectName("paramContainer")
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(8, 8, 8, 8)
        self._layout.setSpacing(8)
        self.setWidget(self._container)

        self._current_table: str = ""
        self._current_params: List[Dict] = []
        self._widgets: Dict[str, Any] = {}

        self._show_placeholder("请选择元器件和算法类型")

    def _show_placeholder(self, text: str):
        self._clear()
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("color: #484f58; font-size: 14px; padding: 40px;")
        self._layout.addWidget(lbl)

    def _clear(self):
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self._widgets = {}

    # ═════════════════════════════════════════════════════════════
    #  主入口
    # ═════════════════════════════════════════════════════════════

    def load_algorithm(self, table_name: str, params: List[Dict]):
        self._clear()
        self._current_table = table_name
        self._current_params = params

        if not params:
            self._show_placeholder("该元器件无此算法参数")
            return

        cn_name = ALGORITHM_CN_NAMES.get(table_name, table_name)
        title = QLabel(f"⚙️  {cn_name}")
        title.setObjectName("paramTitle"); self._layout.addWidget(title)

        # 分发到专用编辑器
        if "PIN" in table_name:
            self._build_pin(params)
        elif "COMMON" in table_name:
            self._build_common(params)
        elif "SHORT" in table_name:
            self._build_short(params)
        elif "MATCH" in table_name and "MATCH2" not in table_name:
            self._build_match(params)
        elif "OCV" in table_name:
            self._build_generic_grouped(params, title_hint="OCV参数")
        elif "TOC" in table_name:
            self._build_generic_grouped(params, title_hint="TOC参数")
        else:
            self._build_generic_grouped(params)

        self._layout.addStretch()

    # ═════════════════════════════════════════════════════════════
    #  PIN — 引脚检测（少锡 + 空焊 + 检测矩形）
    # ═════════════════════════════════════════════════════════════

    def _build_pin(self, params: List[Dict]):
        for idx, param in enumerate(params):
            g = QGroupBox()
            v = QVBoxLayout(g); v.setSpacing(8)
            # NG ID
            ng_id = param.get("No_Good_Id", "")
            if ng_id:
                v.addWidget(QLabel(f"NG编号: {ng_id}"))

            # 少锡
            lt = QGroupBox("少锡检测 — RGB + 灰度范围")
            ltg = QGridLayout(lt); ltg.setSpacing(4)
            for r, (kf, lb) in enumerate([
                ("Less_Tin_Red", "红色"), ("Less_Tin_Green", "绿色"),
                ("Less_Tin_Blue", "蓝色"), ("Less_Tin_Gray", "灰度"),
            ]):
                ltg.addWidget(QLabel(lb), r, 0)
                lo = _spin(param.get(f"{kf}_Low", 0), 0, 255)
                ltg.addWidget(lo, r, 1); ltg.addWidget(QLabel("–"), r, 2)
                hi = _spin(param.get(f"{kf}_High", 255), 0, 255)
                ltg.addWidget(hi, r, 3)
                self._widgets[f"{idx}_{kf}_Low"] = lo
                self._widgets[f"{idx}_{kf}_High"] = hi
            ltg.addWidget(QLabel("判定上限"), 4, 0)
            jh = _spin(param.get("Less_Tin_Judge_High", 100), 0, 255)
            ltg.addWidget(jh, 4, 1); ltg.addWidget(QLabel("判定下限"), 4, 2)
            jl = _spin(param.get("Less_Tin_Judge_Low", 0), 0, 255)
            ltg.addWidget(jl, 4, 3)
            self._widgets[f"{idx}_Less_Tin_Judge_High"] = jh
            self._widgets[f"{idx}_Less_Tin_Judge_Low"] = jl
            v.addWidget(lt)

            # 空焊
            ew = QGroupBox("空焊检测 — RGB + 灰度范围")
            ewg = QGridLayout(ew); ewg.setSpacing(4)
            for r, (kf, lb) in enumerate([
                ("Empty_Welding_Red", "红色"), ("Empty_Welding_Green", "绿色"),
                ("Empty_Welding_Blue", "蓝色"), ("Empty_Welding_Gray", "灰度"),
            ]):
                ewg.addWidget(QLabel(lb), r, 0)
                lo = _spin(param.get(f"{kf}_Low", 0), 0, 255)
                ewg.addWidget(lo, r, 1); ewg.addWidget(QLabel("–"), r, 2)
                hi = _spin(param.get(f"{kf}_High", 255), 0, 255)
                ewg.addWidget(hi, r, 3)
                self._widgets[f"{idx}_{kf}_Low"] = lo
                self._widgets[f"{idx}_{kf}_High"] = hi
            ewg.addWidget(QLabel("判定上限"), 4, 0)
            ejh = _spin(param.get("Empty_Welding_Judge_High", 100), 0, 255)
            ewg.addWidget(ejh, 4, 1); ewg.addWidget(QLabel("判定下限"), 4, 2)
            ejl = _spin(param.get("Empty_Welding_Judge_Low", 0), 0, 255)
            ewg.addWidget(ejl, 4, 3)
            self._widgets[f"{idx}_Empty_Welding_Judge_High"] = ejh
            self._widgets[f"{idx}_Empty_Welding_Judge_Low"] = ejl
            v.addWidget(ew)

            # 检测矩形
            rect = QGroupBox("检测矩形区域")
            rg = QGridLayout(rect); rg.setSpacing(4)
            for row, (key, label) in enumerate([
                ("Detected_Rect_Left_Top_X", "检测 左上X"), ("Detected_Rect_Left_Top_Y", "检测 左上Y"),
                ("Detected_Rect_Right_Down_X", "检测 右下X"), ("Detected_Rect_Right_Down_Y", "检测 右下Y"),
                ("Position_Rect_Left_Top_X", "定位 左上X"), ("Position_Rect_Left_Top_Y", "定位 左上Y"),
                ("Position_Rect_Right_Down_X", "定位 右下X"), ("Position_Rect_Right_Down_Y", "定位 右下Y"),
            ]):
                r = row % 4; c = (row // 4) * 2
                rg.addWidget(QLabel(label), r, c)
                s = _spin(param.get(key, 0), 0, 99999)
                rg.addWidget(s, r, c + 1)
                self._widgets[f"{idx}_{key}"] = s
            v.addWidget(rect)

            # 其他
            other_keys = {k: v2 for k, v2 in param.items()
                          if k not in SKIP_COLUMNS and not k.startswith(("Less_Tin_", "Empty_Welding_", "Detected_", "Position_"))}
            if other_keys:
                self._add_simple_grid(v, idx, other_keys)

            self._layout.addWidget(g)

    # ═════════════════════════════════════════════════════════════
    #  COMMON — 通用参数（RGB + 灰度范围）
    # ═════════════════════════════════════════════════════════════

    def _build_common(self, params: List[Dict]):
        for idx, param in enumerate(params):
            g = QGroupBox()
            v = QVBoxLayout(g); v.setSpacing(8)

            # RGB 颜色范围
            rgb = QGroupBox("RGB + 灰度 颜色范围")
            rgg = QGridLayout(rgb); rgg.setSpacing(4)
            for r, (kf, lb) in enumerate([
                ("Color_Red", "红色"), ("Color_Green", "绿色"),
                ("Color_Blue", "蓝色"), ("Color_Gray", "灰度"),
            ]):
                rgg.addWidget(QLabel(lb), r, 0)
                lo = _spin(param.get(f"{kf}_Low", 0), 0, 255)
                rgg.addWidget(lo, r, 1); rgg.addWidget(QLabel("–"), r, 2)
                hi = _spin(param.get(f"{kf}_High", 255), 0, 255)
                rgg.addWidget(hi, r, 3)
                self._widgets[f"{idx}_{kf}_Low"] = lo
                self._widgets[f"{idx}_{kf}_High"] = hi
            v.addWidget(rgb)

            # 搜索范围
            sr = QGroupBox("搜索范围")
            sg = QGridLayout(sr); sg.setSpacing(4)
            for r, (key, label) in enumerate([
                ("Search_Scope_X", "搜索 X"), ("Search_Scope_Y", "搜索 Y"),
                ("Search_Scope_Angle", "搜索角度"),
            ]):
                sg.addWidget(QLabel(label), r, 0)
                ds = _dspin(param.get(key, 0))
                sg.addWidget(ds, r, 1)
                self._widgets[f"{idx}_{key}"] = ds
            v.addWidget(sr)

            # 其他
            skip = {"Color_Red_High", "Color_Red_Low", "Color_Green_High", "Color_Green_Low",
                    "Color_Blue_High", "Color_Blue_Low", "Color_Gray_High", "Color_Gray_Low",
                    "Search_Scope_X", "Search_Scope_Y", "Search_Scope_Angle"}
            skip.update(SKIP_COLUMNS)
            other = {k: v2 for k, v2 in param.items() if k not in skip}
            if other:
                self._add_simple_grid(v, idx, other)

            self._layout.addWidget(g)

    # ═════════════════════════════════════════════════════════════
    #  SHORT — 短路检测
    # ═════════════════════════════════════════════════════════════

    def _build_short(self, params: List[Dict]):
        for idx, param in enumerate(params):
            g = QGroupBox()
            v = QVBoxLayout(g); v.setSpacing(8)

            # 核心参数
            core = QGroupBox("核心参数")
            cg = QGridLayout(core); cg.setSpacing(4)
            for r, key in enumerate(["Mini_Width", "Pin_Width", "Project_Threshold", "Diff_Threshold"]):
                cg.addWidget(QLabel(_make_field_label(key)), r, 0)
                s = _spin(param.get(key, 0))
                cg.addWidget(s, r, 1)
                self._widgets[f"{idx}_{key}"] = s
            v.addWidget(core)

            # 其他
            skip = {"Mini_Width", "Pin_Width", "Project_Threshold", "Diff_Threshold"}
            skip.update(SKIP_COLUMNS)
            other = {k: v2 for k, v2 in param.items() if k not in skip}
            if other:
                self._add_simple_grid(v, idx, other)

            self._layout.addWidget(g)

    # ═════════════════════════════════════════════════════════════
    #  MATCH — 模板匹配
    # ═════════════════════════════════════════════════════════════

    def _build_match(self, params: List[Dict]):
        for idx, param in enumerate(params):
            g = QGroupBox()
            v = QVBoxLayout(g); v.setSpacing(8)

            core = QGroupBox("图像处理参数")
            cg = QGridLayout(core); cg.setSpacing(4)
            for r, key in enumerate(["Brightness", "Contrast", "Enhance", "Gray", "Value"]):
                cg.addWidget(QLabel(_make_field_label(key)), r, 0)
                s = _spin(param.get(key, 0))
                cg.addWidget(s, r, 1)
                self._widgets[f"{idx}_{key}"] = s
            v.addWidget(core)

            skip = {"Brightness", "Contrast", "Enhance", "Gray", "Value"}
            skip.update(SKIP_COLUMNS)
            other = {k: v2 for k, v2 in param.items() if k not in skip}
            if other:
                self._add_simple_grid(v, idx, other)

            self._layout.addWidget(g)

    # ═════════════════════════════════════════════════════════════
    #  通用分组
    # ═════════════════════════════════════════════════════════════

    def _build_generic_grouped(self, params: List[Dict], title_hint: str = ""):
        for idx, param in enumerate(params):
            g = QGroupBox()
            v = QVBoxLayout(g); v.setSpacing(4)
            filtered = {k: v2 for k, v2 in param.items() if k not in SKIP_COLUMNS}
            if filtered:
                self._add_simple_grid(v, idx, filtered)
            self._layout.addWidget(g)

    def _add_simple_grid(self, parent_layout, idx: int, data: dict):
        """将 dict 转为 label+widget 网格"""
        grid = QGridLayout(); grid.setSpacing(4)
        row = 0
        for key, value in data.items():
            lbl = QLabel(_make_field_label(key))
            lbl.setObjectName("paramLabel")
            grid.addWidget(lbl, row, 0)

            if isinstance(value, bool):
                w = QCheckBox(); w.setChecked(value)
            elif isinstance(value, float):
                w = _dspin(value)
            elif isinstance(value, int):
                w = _spin(value)
            elif isinstance(value, str) and len(value) < 40:
                w = QLineEdit(str(value))
            else:
                w = QLabel(str(value)[:60])
                w.setObjectName("paramValue")
                w.setWordWrap(True)
            grid.addWidget(w, row, 1)
            self._widgets[f"{idx}_{key}"] = w
            row += 1
        parent_layout.addLayout(grid)

    # ═════════════════════════════════════════════════════════════
    #  收集当前值
    # ═════════════════════════════════════════════════════════════

    def collect_values(self) -> List[Dict[str, Any]]:
        result = []
        for idx, param in enumerate(self._current_params):
            row = {}
            for key, value in param.items():
                wk = f"{idx}_{key}"
                w = self._widgets.get(wk)
                if w is None:
                    row[key] = value
                elif isinstance(w, QSpinBox):
                    row[key] = w.value()
                elif isinstance(w, QDoubleSpinBox):
                    row[key] = w.value()
                elif isinstance(w, QLineEdit):
                    row[key] = w.text()
                elif isinstance(w, QCheckBox):
                    row[key] = 1 if w.isChecked() else 0
                elif isinstance(w, QComboBox):
                    row[key] = w.currentIndex()
                else:
                    row[key] = value
            result.append(row)
        return result

    @property
    def current_table(self) -> str:
        return self._current_table
