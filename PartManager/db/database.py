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
        """加载NG记录（含ROI信息）"""
        rows = conn.execute("""
            SELECT Component_Name, No_Good_Id, No_Good_Type, Application_Type,
                   Roi_Width, Roi_Height, Roi_Position_x, Roi_Position_y,
                   Aoi_Angle, Resolution, Link_Flag, Link_Ng_Id,
                   NG_Image_Width, NG_Image_Height
            FROM COMPONENT_NG ORDER BY Component_Name, No_Good_Id
        """).fetchall()
        self._ng_records = [dict(r) for r in rows]
        self._ng_by_component = {}
        self._ng_roi = {}  # key: (comp_name, ng_id) → roi dict
        for r in self._ng_records:
            name = r["Component_Name"]
            self._ng_by_component.setdefault(name, []).append(r)
            key = (name, r["No_Good_Id"])
            self._ng_roi[key] = {
                "x": r.get("Roi_Position_x", 0) or 0,
                "y": r.get("Roi_Position_y", 0) or 0,
                "w": r.get("Roi_Width", 0) or 0,
                "h": r.get("Roi_Height", 0) or 0,
                "angle": r.get("Aoi_Angle", 0) or 0,
            }

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

    def get_ng_roi(self, component_name: str, ng_id: str) -> Dict[str, float]:
        """获取NG的ROI信息"""
        return self._ng_roi.get((component_name, ng_id), {"x":0,"y":0,"w":0,"h":0,"angle":0})

    def update_ng_roi(self, component_name: str, ng_id: str,
                      rx: float, ry: float, rw: float, rh: float):
        """更新NG的ROI到DB"""
        with self._connect_rw() as conn:
            conn.execute("""
                UPDATE COMPONENT_NG
                SET Roi_Position_x=?, Roi_Position_y=?, Roi_Width=?, Roi_Height=?
                WHERE Component_Name=? AND No_Good_Id=?
            """, (rx, ry, rw, rh, component_name, ng_id))
            conn.commit()

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

    # ─── 插入/删除 ──────────────────────────────────────────────

    def _sync_ng_cache(self, component_name, ng_id, defect_type, app_type):
        """同步NG缓存"""
        record = {
            "Component_Name": component_name, "No_Good_Id": ng_id,
            "No_Good_Type": defect_type, "Application_Type": app_type,
            "Roi_Width": 2.0, "Roi_Height": 2.0,
            "Roi_Position_x": 0.0, "Roi_Position_y": 0.0,
            "Aoi_Angle": 0.0, "Resolution": 15.0, "Link_Flag": 0,
        }
        self._ng_records.append(record)
        self._ng_by_component.setdefault(component_name, []).append(record)
        self._ng_roi[(component_name, ng_id)] = {"x": 0, "y": 0, "w": 2, "h": 2, "angle": 0}

    def insert_ng(self, component_name: str, ng_id: str,
                  defect_type: int, app_type: str = "10100"):
        """插入新的NG记录到COMPONENT_NG，DB+缓存"""
        with self._connect_rw() as conn:
            conn.execute("""
                INSERT INTO COMPONENT_NG
                (Component_Name, No_Good_Id, No_Good_Type, Application_Type,
                 Roi_Width, Roi_Height, Roi_Position_x, Roi_Position_y,
                 Aoi_Angle, Resolution, Link_Flag)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (component_name, ng_id, defect_type, app_type,
                  2.0, 2.0, 0.0, 0.0, 0.0, 15.0, 0))
            conn.commit()
        self._sync_ng_cache(component_name, ng_id, defect_type, app_type)

    def insert_ng_memonly(self, component_name: str, ng_id: str,
                          defect_type: int, app_type: str = "10100"):
        """插入新的NG — 仅缓存，不写DB"""
        self._sync_ng_cache(component_name, ng_id, defect_type, app_type)

    def _sync_algo_cache(self, component_name, ng_id, defect_type, algo_type):
        row = {"Component_Name": component_name, "No_Good_Id": ng_id,
               "Defect_Type": defect_type, "Algorithm_Type": algo_type,
               "Algorithm_Use_Flag": 1, "Color_Channel": 7, "Color_Method": 1,
               "Detection_Type": 1, "Search_Scope_X": 0.5, "Search_Scope_Y": 0.5,
               "Search_Scope_Angle": 6.0,
               "Color_Red_High": 255, "Color_Red_Low": 0,
               "Color_Green_High": 255, "Color_Green_Low": 0,
               "Color_Blue_High": 255, "Color_Blue_Low": 0,
               "Color_Gray_High": 255, "Color_Gray_Low": 0,
               "Retrun_Value_High": 0, "Retrun_Value_Low": 0,
               "Return_Value": 0, "Error_Exp": "OK"}
        self._algorithm_params.setdefault("COMMON_ALGORITHM_PARAMETER", {})
        self._algorithm_params["COMMON_ALGORITHM_PARAMETER"].setdefault(
            component_name, []).append(row)

    def insert_algorithm_to_common(self, component_name: str, ng_id: str,
                                    defect_type: int, algo_type: int):
        """插入新的算法记录到COMMON_ALGORITHM_PARAMETER，DB+缓存"""
        with self._connect_rw() as conn:
            conn.execute("""
                INSERT INTO COMMON_ALGORITHM_PARAMETER
                (Component_Name, No_Good_Id, Defect_Type, Algorithm_Type,
                 Algorithm_Use_Flag, Color_Channel, Color_Method,
                 Detection_Type, Search_Scope_X, Search_Scope_Y,
                 Search_Scope_Angle, Color_Red_High, Color_Red_Low,
                 Color_Green_High, Color_Green_Low, Color_Blue_High,
                 Color_Blue_Low, Color_Gray_High, Color_Gray_Low,
                 Retrun_Value_High, Retrun_Value_Low, Return_Value, Error_Exp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (component_name, ng_id, defect_type, algo_type,
                  1, 7, 1, 1, 0.5, 0.5, 6.0,
                  255, 0, 255, 0, 255, 0, 255, 0,
                  0, 0, 0, "OK"))
            conn.commit()
        self._sync_algo_cache(component_name, ng_id, defect_type, algo_type)

    def insert_algorithm_memonly(self, component_name: str, ng_id: str,
                                  defect_type: int, algo_type: int):
        """插入新的算法 — 仅缓存，不写DB"""
        self._sync_algo_cache(component_name, ng_id, defect_type, algo_type)

    def insert_component(self, comp_name: str, package_type: str,
                         img_data: bytes, img_w: int, img_h: int):
        """插入新元器件"""
        with self._connect_rw() as conn:
            conn.execute("""
                INSERT INTO COMPONENT
                (Component_Name, PackageType, Component_Width, Component_Height,
                 Crop_Area_X, Crop_Area_Y, Crop_Area_Angle,
                 Component_Image, Component_Image_Width, Component_Image_Height,
                 Template_Flag)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (comp_name, package_type, 0, 0, 1.2, 1.2, 0.0,
                  img_data, img_w, img_h, 0))
            conn.commit()
        # 更新缓存
        self._component_list.append({
            "Component_Name": comp_name, "PackageType": package_type,
            "Component_Width": 0, "Component_Height": 0,
            "Crop_Area_X": 1.2, "Crop_Area_Y": 1.2, "Crop_Area_Angle": 0,
            "Component_Image": img_data, "Component_Image_Width": img_w,
            "Component_Image_Height": img_h, "Template_Flag": 0,
        })
        self._components[comp_name] = self._component_list[-1]
        if package_type not in self._package_types:
            self._package_types.append(package_type)
            self._package_types.sort()

    def delete_component(self, comp_name: str):
        """删除元器件及其关联数据"""
        with self._connect_rw() as conn:
            conn.execute("DELETE FROM COMPONENT WHERE Component_Name=?", (comp_name,))
            conn.execute("DELETE FROM COMPONENT_NG WHERE Component_Name=?", (comp_name,))
            conn.execute("DELETE FROM COMMON_ALGORITHM_PARAMETER WHERE Component_Name=?", (comp_name,))
            conn.commit()
        # 更新缓存
        self._component_list = [c for c in self._component_list
                                if c["Component_Name"] != comp_name]
        self._components.pop(comp_name, None)
        self._ng_records = [r for r in self._ng_records
                            if r["Component_Name"] != comp_name]
        if comp_name in self._ng_by_component:
            del self._ng_by_component[comp_name]
        keys_to_del = [k for k in self._ng_roi if k[0] == comp_name]
        for k in keys_to_del:
            del self._ng_roi[k]
        for comp_map in self._algorithm_params.values():
            comp_map.pop(comp_name, None)

    def delete_ng(self, component_name: str, ng_id: str):
        """删除NG记录及其关联的算法参数"""
        with self._connect_rw() as conn:
            conn.execute(
                "DELETE FROM COMPONENT_NG WHERE Component_Name=? AND No_Good_Id=?",
                (component_name, ng_id))
            conn.execute(
                "DELETE FROM COMMON_ALGORITHM_PARAMETER WHERE Component_Name=? AND No_Good_Id=?",
                (component_name, ng_id))
            conn.commit()
        # 更新缓存
        self._ng_records = [r for r in self._ng_records
                            if not (r["Component_Name"] == component_name and r["No_Good_Id"] == ng_id)]
        if component_name in self._ng_by_component:
            self._ng_by_component[component_name] = [
                r for r in self._ng_by_component[component_name]
                if r["No_Good_Id"] != ng_id]
        self._ng_roi.pop((component_name, ng_id), None)
        comp_map = self._algorithm_params.get("COMMON_ALGORITHM_PARAMETER", {})
        if component_name in comp_map:
            comp_map[component_name] = [
                r for r in comp_map[component_name] if r["No_Good_Id"] != ng_id]

    def delete_algorithm_from_common(self, component_name: str, ng_id: str, algo_type: int):
        """从COMMON_ALGORITHM_PARAMETER删除指定算法"""
        with self._connect_rw() as conn:
            conn.execute("""
                DELETE FROM COMMON_ALGORITHM_PARAMETER
                WHERE Component_Name=? AND No_Good_Id=? AND Algorithm_Type=?
            """, (component_name, ng_id, algo_type))
            conn.commit()
        comp_map = self._algorithm_params.get("COMMON_ALGORITHM_PARAMETER", {})
        if component_name in comp_map:
            comp_map[component_name] = [
                r for r in comp_map[component_name]
                if not (r["No_Good_Id"] == ng_id and r.get("Algorithm_Type") == algo_type)]
