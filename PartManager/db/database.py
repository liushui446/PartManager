"""
元器件模板库管理系统 - 数据库访问层（内存缓存版）
Component Template Library Management System - Database Access Layer (In-Memory Cache)
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional


class ComponentDatabase:
    """SQLite数据库封装，启动时全量加载到内存，后续查询零IO"""

    def __init__(self, db_path: str):
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"数据库文件不存在: {db_path}")
        self._db_path = db_path
        self._db_size_mb = round(os.path.getsize(db_path) / 1024 / 1024, 1)

        # ── 内存缓存 ──
        self._components: Dict[str, Dict] = {}          # name → row
        self._component_list: List[Dict] = []            # 全量列表
        self._package_types: List[str] = []              # 封装类型列表
        self._ng_records: List[Dict] = []                # 全量NG记录
        self._ng_by_component: Dict[str, List[Dict]] = {}  # name → [ng...]
        self._algorithm_params: Dict[str, Dict[str, List[Dict]]] = {}  # table → {name → [params]}
        self._algorithm_schemas: Dict[str, List[Dict]] = {}  # table → [column info]

        # ── 启动时加载 ──
        self._load_all()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(f"file:{self._db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        return conn

    # ─── 全量加载 ─────────────────────────────────────────────────

    def _load_all(self):
        """启动时一次性加载所有数据到内存"""
        with self._connect() as conn:
            self._load_components(conn)
            self._load_ng(conn)
            self._load_algorithm_params(conn)

    def _load_components(self, conn: sqlite3.Connection):
        """加载元器件表"""
        rows = conn.execute("""
            SELECT Component_Name, PackageType, PackageType_ID,
                   Component_Width, Component_Height,
                   Crop_Area_X, Crop_Area_Y, Crop_Area_Angle,
                   Component_Image, Component_Image_Width, Component_Image_Height,
                   HG_Image, HG_Image_Width, HG_Image_Height,
                   Template_Flag
            FROM COMPONENT ORDER BY PackageType, Component_Name
        """).fetchall()

        self._component_list = []
        for r in rows:
            d = dict(r)
            self._component_list.append(d)
            self._components[d["Component_Name"]] = d

        # 封装类型
        self._package_types = sorted(set(c["PackageType"] for c in self._component_list))

    def _load_ng(self, conn: sqlite3.Connection):
        """加载NG记录"""
        rows = conn.execute(
            "SELECT Component_Name, No_Good_Id FROM COMPONENT_NG ORDER BY Component_Name, No_Good_Id"
        ).fetchall()
        self._ng_records = [dict(r) for r in rows]
        self._ng_by_component = {}
        for r in self._ng_records:
            name = r["Component_Name"]
            self._ng_by_component.setdefault(name, []).append(r)

    def _load_algorithm_params(self, conn: sqlite3.Connection):
        """加载所有算法参数表"""
        all_tables = [
            "MATCH_ALGORITHM_PARAMETER", "MATCH2_ALGORITHM_PARAMETER",
            "HISTOGRAM_ALGORITHM_PARAMETER", "LENGTH_ALGORITHM_PARAMETER",
            "COMPARE_ALGORITHM_PARAMETER", "CREST_ALGORITHM_PARAMETER",
            "SHORT_ALGORITHM_PARAMETER", "OCV_ALGORITHM_PARAMETER",
            "IC_ALGORITHM_PARAMETER", "TOC_ALGORITHM_PARAMETER",
            "OTHER_ALGORITHM_PARAMETER", "ALOFFSET_ALGORITHM_PARAMETER",
            "PIN_ALGORITHM_PARAMETER", "CODEDETECT_ALGORITHM_PARAMETER",
            "MACROSM_ALGORITHM_PARAMETER", "COMMON_ALGORITHM_PARAMETER",
        ]

        for table in all_tables:
            # schema
            cols = conn.execute(f"PRAGMA table_info([{table}])").fetchall()
            self._algorithm_schemas[table] = [
                {"name": c[1], "type": c[2], "nullable": not c[3]} for c in cols
            ]

            # data
            try:
                rows = conn.execute(f"SELECT * FROM [{table}]").fetchall()
            except Exception:
                rows = []

            col_names = [c["name"] for c in self._algorithm_schemas[table]]
            self._algorithm_params[table] = {}
            for r in rows:
                d = dict(zip(col_names, r))
                comp_name = d.get("Component_Name", "")
                self._algorithm_params[table].setdefault(comp_name, []).append(d)

    # ─── 查询接口（全部从缓存读取）─────────────────────────────────

    def get_all_components(self) -> List[Dict[str, Any]]:
        """获取所有元器件（不含BLOB）"""
        return [{k: v for k, v in c.items() if k not in ("Component_Image", "HG_Image")}
                for c in self._component_list]

    def get_component_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """按名称获取完整元器件数据"""
        return self._components.get(name)

    def get_components_by_package_type(self, pkg_type: str) -> List[Dict[str, Any]]:
        """按封装类型获取元器件"""
        return [c for c in self._component_list if c["PackageType"] == pkg_type]

    def get_package_types(self) -> List[str]:
        return self._package_types

    def get_ng_records(self, component_name: str) -> List[Dict[str, Any]]:
        return self._ng_by_component.get(component_name, [])

    def get_all_ng_records(self) -> List[Dict[str, Any]]:
        return self._ng_records

    def get_algorithm_tables_with_data(self) -> List[str]:
        """获取有数据的算法参数表"""
        return [t for t, data in self._algorithm_params.items() if data]

    def get_algorithms_for_component(self, component_name: str) -> Dict[str, List[Dict]]:
        """获取某个元器件所有算法参数，返回 {table_name: [params]}"""
        result = {}
        for table, comp_map in self._algorithm_params.items():
            if component_name in comp_map:
                result[table] = comp_map[component_name]
        return result

    def get_algorithm_params(self, table_name: str, component_name: str) -> List[Dict[str, Any]]:
        """获取指定表和元器件的算法参数"""
        comp_map = self._algorithm_params.get(table_name, {})
        return comp_map.get(component_name, [])

    def get_algorithm_params_schema(self, table_name: str) -> List[Dict[str, Any]]:
        return self._algorithm_schemas.get(table_name, [])

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "component_count": len(self._component_list),
            "ng_record_count": len(self._ng_records),
            "package_type_count": len(self._package_types),
            "algorithm_table_count": len(self.get_algorithm_tables_with_data()),
            "algorithm_param_rows": sum(
                sum(len(v) for v in comp_map.values())
                for comp_map in self._algorithm_params.values()
            ),
            "db_size_mb": self._db_size_mb,
            "cache_ready": True,
        }

    # ─── 写入支持 ───────────────────────────────────────────────

    def _connect_rw(self) -> sqlite3.Connection:
        """读写连接"""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def update_algorithm_use_flag(self, component_name: str, ng_id: str,
                                   algo_type: int, use_flag: bool):
        """设置某元器件+NG_ID+算法类型的Use标记"""
        with self._connect_rw() as conn:
            conn.execute("""
                UPDATE COMMON_ALGORITHM_PARAMETER
                SET Algorithm_Use_Flag = ?
                WHERE Component_Name = ? AND No_Good_Id = ?
                  AND Algorithm_Type = ?
            """, (1 if use_flag else 0, component_name, ng_id, algo_type))
            conn.commit()

    def clear_use_flags_for_ng(self, component_name: str, ng_id: str):
        """清除某元器件+NG_ID下所有算法的Use标记"""
        with self._connect_rw() as conn:
            conn.execute("""
                UPDATE COMMON_ALGORITHM_PARAMETER
                SET Algorithm_Use_Flag = 0
                WHERE Component_Name = ? AND No_Good_Id = ?
            """, (component_name, ng_id))
            conn.commit()

    def update_algorithm_param(self, table_name: str, component_name: str,
                                ng_id: str, params: Dict[str, Any]):
        """更新算法参数表中的一行"""
        if not params:
            return
        # 去掉 Component_Name 和 No_Good_Id 从 SET 子句
        set_parts = []
        values = []
        for k, v in params.items():
            if k in ("Component_Name", "No_Good_Id"):
                continue
            set_parts.append(f"[{k}] = ?")
            values.append(v)
        if not set_parts:
            return
        values.extend([component_name, ng_id])
        sql = f"UPDATE [{table_name}] SET {', '.join(set_parts)} WHERE Component_Name = ? AND No_Good_Id = ?"
        with self._connect_rw() as conn:
            conn.execute(sql, values)
            conn.commit()

    def update_cache(self, table_name: str, component_name: str,
                     ng_id: str, params: Dict[str, Any]):
        """同步更新内存缓存"""
        comp_map = self._algorithm_params.get(table_name, {})
        records = comp_map.get(component_name, [])
        for r in records:
            if r.get("No_Good_Id") == ng_id:
                r.update(params)
                break
