"""
元器件模板库管理系统 - 算法参数编辑器（Slider/CheckBox/RadioButton 版）
"""

from ui.range_slider import RangeSlider

from typing import Dict, List, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea,
    QGroupBox, QLabel, QSlider, QSpinBox, QDoubleSpinBox,
    QPushButton, QFrame, QLineEdit, QCheckBox, QRadioButton, QButtonGroup,
)
from PySide6.QtCore import Qt, Signal

# ─── 算法中文名 ───

ALGORITHM_CN_NAMES: Dict[str, str] = {
    "CREST_ALGORITHM_PARAMETER": "波峰焊检测",
    "SHORT_ALGORITHM_PARAMETER": "短路检测",
    "MATCH_ALGORITHM_PARAMETER": "模板匹配",
    "MATCH2_ALGORITHM_PARAMETER": "二次匹配",
    "PIN_ALGORITHM_PARAMETER": "引脚检测",
    "IC_ALGORITHM_PARAMETER": "IC检测",
    "OCV_ALGORITHM_PARAMETER": "OCV字符检测",
    "TOC_ALGORITHM_PARAMETER": "TOC检测",
    "OTHER_ALGORITHM_PARAMETER": "其他缺陷检测",
    "LENGTH_ALGORITHM_PARAMETER": "长度检测",
    "ALOFFSET_ALGORITHM_PARAMETER": "偏移检测",
    "HISTOGRAM_ALGORITHM_PARAMETER": "直方图检测",
    "COMMON_ALGORITHM_PARAMETER": "通用算法参数",
    "COMPARE_ALGORITHM_PARAMETER": "对比检测",
    "CODEDETECT_ALGORITHM_PARAMETER": "条码检测",
    "MACROSM_ALGORITHM_PARAMETER": "宏观检测",
    "INSPECTION3D_ALGORITHM_PARAMETER": "3D检测",
    "DISTANCE_ALGORITHM_PARAMETER": "距离检测",
    "GLUE_ALGORITHM_PARAMETER": "胶水检测",
    "PADPLACE_ALGORITHM_PARAMETER": "焊盘放置",
    "POLE_ALGORITHM_PARAMETER": "极性检测",
    "HOLE_ALGORITHM_PARAMETER": "孔检测",
}

ALGORITHM_SHORT_NAMES: Dict[str, str] = {k: v for k, v in ALGORITHM_CN_NAMES.items()}

# 字段中文名映射
FIELD_CN: Dict[str, str] = {
    "Brightness": "亮度", "Contrast": "对比度", "Enhance": "增强",
    "Gray": "灰度", "Value": "阈值", "Correct_Mode": "校正模式",
    "Detection_Type": "检测类型", "Board_Color": "板材颜色",
    "Mini_Width": "最小宽度", "Pin_Width": "引脚宽度",
    "Project_Threshold": "投影阈值", "Diff_Threshold": "差值阈值",
    "Allow_Auto_Calculate": "自动计算", "Solder_Brige_Method": "锡桥检测法",
    "Average_Brightness": "平均亮度", "Observe": "观察模式",
    "Defect_Type": "缺陷类型", "Algorithm_Type": "算法类型",
    "Algorithm_Use_Flag": "启用算法", "Color_Channel": "颜色通道",
    "Color_Method": "颜色方法", "Search_Scope_X": "搜索X",
    "Search_Scope_Y": "搜索Y", "Search_Scope_Angle": "搜索角度",
    "Color_Red_High": "红色上限", "Color_Red_Low": "红色下限",
    "Color_Green_High": "绿色上限", "Color_Green_Low": "绿色下限",
    "Color_Blue_High": "蓝色上限", "Color_Blue_Low": "蓝色下限",
    "Color_Gray_High": "灰度上限", "Color_Gray_Low": "灰度下限",
    "Retrun_Value_High": "返回值上限", "Retrun_Value_Low": "返回值下限",
    "Return_Value": "返回值", "Error_Exp": "错误表达式",
    "Img_Type": "图像类型", "Filter_Level": "滤波级别",
    "Binary_Threshold": "二值化阈值", "Match_Angle": "匹配角度",
    "Match_Score": "匹配分数", "Match_Ratio": "匹配比例",
    "Contour_NumThre": "轮廓数阈值", "Enhanced_Detect_State": "增强检测",
    "Zoom_Value": "缩放值", "Char_Ratio": "字符比例",
    "Stand_Image_Width": "标准图宽", "Stand_Image_Height": "标准图高",
    "Polarity": "极性", "Model_Type": "模板类型",
    "Char_DiffThreshold": "字符差分阈值",
    "Lead_Fix": "引脚修正", "Pin_To_Box_Ratio": "引脚盒比例",
    "Upper_Boundary": "上边界", "Lower_Boundary": "下边界",
    "Auto_CalBoundary_Flag": "自动边界", "Auto_Calculate_Flag": "自动计算",
    "Min_Width": "最小宽度", "Pin_Width_Threshold": "引脚宽阈值",
    "BinThreshold": "二值化阈值",
    "Template_Gray_Mean": "模板灰度均值",
    "Auto_Extract_Color": "自动提取颜色",
    "Histo_Percentile_Pt": "直方图百分位",
    "Intense_Resolution": "强度分辨率", "Hue_Resolution": "色调分辨率",
    "Intense_Vary_Tolerance_Factor": "强度容差",
    "Hue_Vary_Tolerance_Factor": "色调容差",
    "Param_Adapt_Method": "自适应方法",
    "Pin_Mode_Choose": "引脚模式",
    "Less_Tin_Red_Low": "少锡红下限", "Less_Tin_Red_High": "少锡红上限",
    "Less_Tin_Green_Low": "少锡绿下限", "Less_Tin_Green_High": "少锡绿上限",
    "Less_Tin_Blue_Low": "少锡蓝下限", "Less_Tin_Blue_High": "少锡蓝上限",
    "Less_Tin_Gray_Low": "少锡灰下限", "Less_Tin_Gray_High": "少锡灰上限",
    "Less_Tin_Judge_High": "少锡判定上限", "Less_Tin_Judge_Low": "少锡判定下限",
    "Empty_Welding_Red_Low": "空焊红下限", "Empty_Welding_Red_High": "空焊红上限",
    "Empty_Welding_Green_Low": "空焊绿下限", "Empty_Welding_Green_High": "空焊绿上限",
    "Empty_Welding_Blue_Low": "空焊蓝下限", "Empty_Welding_Blue_High": "空焊蓝上限",
    "Empty_Welding_Gray_Low": "空焊灰下限", "Empty_Welding_Gray_High": "空焊灰上限",
    "Empty_Welding_Judge_High": "空焊判定上限", "Empty_Welding_Judge_Low": "空焊判定下限",
    "Detected_Rect_Left_Top_X": "检测左上X", "Detected_Rect_Left_Top_Y": "检测左上Y",
    "Detected_Rect_Right_Down_X": "检测右下X", "Detected_Rect_Right_Down_Y": "检测右下Y",
    "Position_Rect_Left_Top_X": "定位左上X", "Position_Rect_Left_Top_Y": "定位左上Y",
    "Position_Rect_Right_Down_X": "定位右下X", "Position_Rect_Right_Down_Y": "定位右下Y",
    "Rotio": "旋转比例", "Detect_Method": "检测方法",
    "Gray_Lower": "灰度下限", "Gray_Average": "灰度均值", "Gray_Upper": "灰度上限",
    "Init_Judge_Upper": "初始判定上限", "Init_Judge_Lower": "初始判定下限",
    "Total_Gray_Average": "总灰度均值", "Output_Gray": "输出灰度",
    "Det_Length": "检测长度", "M_Register_Width": "配准宽度",
    "M_Register_Height": "配准高度", "M_Modelimg_Type": "模板图类型",
    "M_Errorpixelnum_Factor": "错误像素因子",
    "M_Init_Var_Ratio": "初始方差比", "Diff_Thre": "差分阈值",
    "M_Least_Error_Area": "最小错误区域",
    "Detect_DisTAB": "检测距离", "Standard_Length": "标准长度",
    "Adjust_Intensity": "调节强度", "Adjust_Contrast": "调节对比度",
    "Judge_High": "判定上限", "Judge_Low": "判定下限",
    "Solder_Brige_Method": "锡桥检测法", "Straight_Thread_Number": "直线引脚数",
    "Straight_Thread_Number_Current": "当前直线引脚数",
    "Diff_Current": "差值电流",
}

SKIP_COLUMNS = {"Component_Name", "No_Good_Id"}

# ─── 创建控件的辅助函数 ──────────────────────────────────────────

def _make_slider_spin(val: int, lo: int, hi: int, parent):
    """创建 Slider + SpinBox 联动组件，返回 (layout, slider, spinbox)"""
    w = QWidget(parent)
    layout = QHBoxLayout(w)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)

    slider = QSlider(Qt.Horizontal)
    slider.setRange(lo, hi)
    slider.setValue(val)

    spin = QSpinBox()
    spin.setRange(lo, hi)
    spin.setValue(val)
    spin.setFixedWidth(60)

    slider.valueChanged.connect(spin.setValue)
    spin.valueChanged.connect(slider.setValue)

    layout.addWidget(slider, 1)
    layout.addWidget(spin)
    return w, slider, spin


class AlgorithmParamEditor(QScrollArea):
    """根据算法类型自动生成编辑表单，使用 Slider/CheckBox/RadioButton"""

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
        title.setObjectName("paramTitle")
        self._layout.addWidget(title)

        # 所有算法都走统一编辑器
        for idx, param in enumerate(params):
            group = QGroupBox()
            grid = QGridLayout(group)
            grid.setSpacing(6)
            grid.setContentsMargins(8, 12, 8, 8)

            # 显示 NG_ID
            ng = param.get("No_Good_Id", "")
            if ng:
                ng_lbl = QLabel(f"NG_ID: {ng}")
                ng_lbl.setStyleSheet("color:#8b949e; font-size:11px;")
                grid.addWidget(ng_lbl, 0, 0, 1, 4)

            # 检测 High/Low 配对
            high_low_pairs = set()
            all_keys = list(param.keys())
            for k in all_keys:
                if k.endswith("_Low") and k.replace("_Low", "_High") in param:
                    base = k[:-4]
                    high_low_pairs.add(base)
            skip_keys = set()
            for base in high_low_pairs:
                skip_keys.add(base + "_Low")
                skip_keys.add(base + "_High")

            row = 1
            for key, value in param.items():
                if key in SKIP_COLUMNS:
                    continue

                # High/Low 配对 → 一个双把手 RangeSlider
                if key.endswith("_Low") and key[:-4] in high_low_pairs:
                    base = key[:-4]
                    lo_val = int(param.get(base + "_Low", 0) or 0)
                    hi_val = int(param.get(base + "_High", 255) or 255)
                    lo, hi = 0, 255
                    if "Gray" in base: lo, hi = 0, 255
                    elif "Red" in base or "Green" in base or "Blue" in base: lo, hi = 0, 180
                    elif "Judge" in base: lo, hi = 0, 255
                    elif "Retrun" in base or "Return" in base: lo, hi = 0, 9999
                    else: lo, hi = 0, 255

                    rs = RangeSlider()
                    rs.setMinimum(lo); rs.setMaximum(hi)
                    rs.setLowerValue(lo_val); rs.setUpperValue(hi_val)

                    cn = FIELD_CN.get(base + "_Low", base)
                    lbl = QLabel(cn.replace("下限", "").replace("Low", "").strip())
                    lbl.setObjectName("paramLabel")
                    grid.addWidget(lbl, row, 0)
                    grid.addWidget(rs, row, 1, 1, 3)
                    self._widgets[f"{idx}_{base}_Low"] = rs  # store for collect
                    row += 1
                    continue

                if key in skip_keys:
                    continue

                cn_label = FIELD_CN.get(key, key)
                lbl = QLabel(cn_label)
                lbl.setObjectName("paramLabel")

                wid = self._create_widget(key, value, idx, group)
                if isinstance(wid, QWidget) and wid.layout():
                    grid.addWidget(lbl, row, 0)
                    grid.addWidget(wid, row, 1, 1, 3)
                elif isinstance(wid, QCheckBox):
                    grid.addWidget(lbl, row, 0)
                    grid.addWidget(wid, row, 1)
                else:
                    grid.addWidget(lbl, row, 0)
                    grid.addWidget(wid, row, 1, 1, 3)
                row += 1

            self._layout.addWidget(group)

        self._layout.addStretch()

    def _create_widget(self, key: str, value, idx: int, parent):
        """根据字段名和值智能创建控件"""
        wk = f"{idx}_{key}"

        # ── bool → CheckBox ──
        if isinstance(value, bool) or key.endswith("_Flag"):
            cb = QCheckBox()
            cb.setChecked(bool(value))
            self._widgets[wk] = cb
            return cb

        # ── High/Low 范围型 → Slider+SpinBox ──
        is_high_low = key.endswith("_High") or key.endswith("_Low")

        if is_high_low and isinstance(value, (int, float)):
            v = int(value)
            lo, hi = 0, 255
            # 根据字段名推断范围
            if "Angle" in key:
                hi = 360
            elif "Judge" in key or "Return" in key or "Retrun" in key:
                hi = 255
            elif "Threshold" in key or "Thre" in key:
                hi = 255
            elif "Ratio" in key or "Factor" in key or "Score" in key:
                # 百分比值用 double
                ds = QDoubleSpinBox()
                ds.setDecimals(2)
                ds.setRange(0, 99999)
                try: ds.setValue(float(value))
                except: ds.setValue(0)
                self._widgets[wk] = ds
                return ds
            elif "Percentile" in key:
                lo, hi = 0, 100
            elif "Width" in key or "Height" in key or "Length" in key:
                hi = 9999
            elif "Resolution" in key:
                hi = 100

            w, slider, spin = _make_slider_spin(v, lo, hi, parent)
            self._widgets[wk] = spin  # 以 spinbox 为准
            return w

        # ── float → DoubleSpinBox ──
        if isinstance(value, float):
            ds = QDoubleSpinBox()
            ds.setDecimals(3)
            ds.setRange(-99999, 99999)
            try: ds.setValue(float(value))
            except: ds.setValue(0)
            self._widgets[wk] = ds
            return ds

        # ── int → SpinBox ──
        if isinstance(value, int):
            s = QSpinBox()
            s.setRange(-99999, 99999)
            s.setValue(int(value))
            self._widgets[wk] = s
            return s

        # ── string → LineEdit ──
        if isinstance(value, str):
            le = QLineEdit(str(value))
            self._widgets[wk] = le
            return le

        # ── default ──
        le = QLineEdit(str(value)[:60])
        self._widgets[wk] = le
        return le

    # ═════════════════════════════════════════════════════════════
    #  收集值
    # ═════════════════════════════════════════════════════════════

    def collect_values(self) -> List[Dict[str, Any]]:
        result = []
        for idx, param in enumerate(self._current_params):
            row = {}
            for key, value in param.items():
                if key in SKIP_COLUMNS:
                    row[key] = value; continue
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
                elif isinstance(w, RangeSlider):
                    # stored as base_Low key, we need both High and Low
                    if key.endswith("_Low"):
                        base = key[:-4]
                        row[base + "_Low"] = w.lowerValue()
                        row[base + "_High"] = w.upperValue()
                else:
                    row[key] = value
            result.append(row)
        return result

    @property
    def current_table(self) -> str:
        return self._current_table
