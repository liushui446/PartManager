import sqlite3
import os

db_path = r"f:\claude_project\PartManager\素材库\Component.db"
print("DB file exists:", os.path.exists(db_path))

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 获取所有表
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print("Tables:", tables)

for table_name_tup in tables:
    table_name = table_name_tup[0]
    print(f"\n--- Table: {table_name} ---")
    
    # 获取表结构
    cur.execute(f"PRAGMA table_info({table_name})")
    columns = cur.fetchall()
    print("Columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
        
    # 获取前3条数据
    try:
        cur.execute(f"SELECT * FROM {table_name} LIMIT 3")
        rows = cur.fetchall()
        print("Sample data:")
        for r in rows:
            print("  ", r)
    except Exception as e:
        print("Error reading data:", e)

conn.close()
