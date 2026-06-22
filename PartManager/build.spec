# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置文件
生成独立可执行程序，用于软件著作权递交

用法:
    pyinstaller build.spec          # 从spec构建
    或
    pyinstaller --onefile --windowed --name "ComponentManager" --add-data "..\素材库\Component.db;." main.py
"""

import sys
from pathlib import Path

block_cipher = None

# 数据库源路径
DB_SOURCE = Path(__file__).parent.parent / "素材库" / "Component.db"

# 打包数据文件
datas = []
if DB_SOURCE.exists():
    datas.append((str(DB_SOURCE), "."))
else:
    # 尝试同级目录
    db_alt = Path(__file__).parent / "Component.db"
    if db_alt.exists():
        datas.append((str(db_alt), "."))
    else:
        print(f"警告: 未找到数据库文件 {DB_SOURCE}，打包将不含数据库")
        print("请手动将 Component.db 放到 exe 同目录下")

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'sqlite3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'PIL',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ComponentTemplateManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
