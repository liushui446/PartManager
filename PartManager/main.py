"""
元器件模板库管理系统 - 入口
Component Template Library Management System - Entry Point

用法:
    python main.py                          # 自动查找数据库
    python main.py --db <数据库路径>         # 指定数据库路径
"""

import sys
import os
import argparse

# 将项目根目录添加到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import run_app


def find_database() -> str:
    """自动查找 Component.db"""
    search_paths = [
        os.path.join(os.path.dirname(__file__), "..", "素材库", "Component.db"),
        os.path.join(os.path.dirname(__file__), "Component.db"),
        os.path.join(os.path.dirname(__file__), "..", "Component.db"),
        os.path.join(os.path.dirname(__file__), "resources", "Component.db"),
    ]
    for p in search_paths:
        abs_path = os.path.abspath(p)
        if os.path.exists(abs_path):
            return abs_path
    return ""


def main():
    parser = argparse.ArgumentParser(
        description="元器件模板库管理系统 v1.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python main.py
    python main.py --db "D:/data/Component.db"
        """
    )
    parser.add_argument("--db", "-d", type=str, default="",
                        help="Component.db 数据库文件路径")
    args = parser.parse_args()

    db_path = args.db or find_database()
    if not db_path:
        print("错误: 未找到 Component.db 数据库文件")
        print("请将数据库文件放到以下任一位置:")
        print("  1. 项目根目录/Component.db")
        print("  2. 项目根目录/素材库/Component.db")
        print("  3. 使用 --db 参数指定路径")
        print(f"\n  例如: python main.py --db \"素材库{os.sep}Component.db\"")
        sys.exit(1)

    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        sys.exit(1)

    db_path = os.path.abspath(db_path)
    print(f"数据库路径: {db_path}")
    print(f"数据库大小: {os.path.getsize(db_path) / 1024 / 1024:.1f} MB")
    print("启动应用程序...")
    run_app(db_path)


if __name__ == "__main__":
    main()
