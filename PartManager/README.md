# 元器件模板库管理系统

**Component Template Library Management System**

---

## 📋 项目简介

本系统是一款**元器件模板库管理软件**，用于AOI（自动光学检测）系统中的元器件模板浏览、参数查看和数据管理。支持多种封装类型的元器件信息展示、模板图像预览、检测算法参数配置查阅等功能。

项目基于原始AOI检测系统的元器件模板库模块重构而来，采用 **Python + PySide6** 实现，保留了核心业务逻辑并进行了UI现代化改造。

---

## ✨ 功能特性

- 📦 **元器件分类浏览** — 按封装类型树状展示所有元器件
- 📋 **详细信息查看** — 元器件尺寸、裁剪区域、模板状态等完整信息
- 🖼️ **模板图像预览** — 自动解析并显示元器件模板的灰度图像
- ⚙️ **算法参数查阅** — 多标签页展示各类检测算法配置参数
- 🔍 **快速搜索** — 支持元器件名称实时过滤
- 📊 **统计摘要** — 数据库整体统计一目了然
- 📤 **数据导出** — 支持导出元器件列表为CSV文件
- 🎨 **现代化深色主题** — GitHub风格暗色UI，适合工业场景

---

## 🚀 快速开始

### 环境要求

- Python 3.9+
- PySide6 ≥ 6.5.0

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
# 自动查找数据库（优先查找 ../素材库/Component.db）
python main.py

# 指定数据库路径
python main.py --db "D:/path/to/Component.db"
```

---

## 📁 项目结构

```
PartManager/
├── main.py                 # 程序入口
├── requirements.txt        # Python依赖
├── build.spec              # PyInstaller打包配置
├── README.md               # 本文件
├── db/
│   ├── __init__.py
│   └── database.py         # SQLite数据库访问层
├── ui/
│   ├── __init__.py
│   ├── main_window.py      # 主窗口UI与逻辑
│   └── styles.py           # QSS样式定义
└── resources/              # 资源文件（图标、背景等）
```

---

## 📦 打包为独立可执行文件

用于软件著作权递交或分发：

```bash
# 安装PyInstaller
pip install pyinstaller

# 使用spec文件打包
pyinstaller build.spec

# 或直接命令行打包
pyinstaller --onefile --windowed --name "ComponentTemplateManager" main.py
```

打包后的 `dist/ComponentTemplateManager.exe` 即为独立可执行程序。

**注意**：打包时会将 `Component.db` 嵌入exe。如果数据库需要单独分发，请将 `Component.db` 放在 exe 同目录下。

---

## 🗃️ 数据库说明

使用 SQLite 3 数据库 `Component.db`（源文件约437MB），包含以下主要数据表：

| 表名 | 说明 | 记录数 |
|------|------|--------|
| COMPONENT | 元器件模板信息 | 13 |
| COMPONENT_NG | NG缺陷记录 | 49 |
| COMMON_ALGORITHM_PARAMETER | 通用算法参数 | 156 |
| MATCH_ALGORITHM_PARAMETER | 模板匹配参数 | 32 |
| CREST_ALGORITHM_PARAMETER | 波峰焊检测参数 | 16 |
| TOC_ALGORITHM_PARAMETER | TOC检测参数 | 21 |
| OTHER_ALGORITHM_PARAMETER | 其他缺陷参数 | 22 |
| ... | 共24张表 | ~350行参数 |

---

## 🖥️ 技术架构

```
┌─────────────────────────────────────┐
│          main.py (入口)              │
├─────────────────────────────────────┤
│  ui/main_window.py (主窗口)         │
│  ├── QTreeWidget   (元器件树)       │
│  ├── QTableWidget  (信息表格)       │
│  ├── QTabWidget    (算法面板)       │
│  └── QLabel        (图像预览)       │
├─────────────────────────────────────┤
│  ui/styles.py (QSS样式)             │
├─────────────────────────────────────┤
│  db/database.py (数据访问层)        │
│  └── sqlite3 + Component.db         │
└─────────────────────────────────────┘
```

---

## 📝 版权声明

本软件为独立开发的元器件模板库管理工具，适用于软件著作权登记申请。

© 2025 Component Template Manager. All rights reserved.
