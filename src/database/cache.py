import os
import sqlite3
from contextlib import suppress
from pathlib import Path
from typing import Any, Dict, List
import requests
import logging

SCHEMA_PATH = Path(__file__).parent / "supabase_schema.sql"
DB_PATH = Path("cache.db")

logger = logging.getLogger(__name__)
# Supabase 테이블 이름을 명시적으로 나열하여 허용 리스트를 구성합니다.
VALID_TABLES = {
    "company",
    "menu_category",
    "menu_item",
    "menu_item_option_group",
    "option_group",
    "option_group_item",
    "option_item",
    "order",
    "order_item",
    "order_item_option",
}

class SupabaseCache:
    """SQLite에 Supabase 테이블을 캐싱하고 최신 주문을 감지합니다."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)
        project_id = os.getenv("SUPABASE_PROJECT_ID")
        self.base_url = os.getenv("SUPABASE_URL") or (
            f"https://{project_id}.supabase.co" if project_id else None
        )
        self.api_key = os.getenv("SUPABASE_API_KEY")
        self.headers = {
            "apikey": self.api_key or "",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
        }
        self.last_order_id = 0
        self._load_last_order_id()

    # ------------------------------------------------------------------
    def _load_last_order_id(self) -> None:
        """캐시 DB에서 마지막 주문 ID를 불러옵니다."""
        if not self.db_path.exists():
            return
        with sqlite3.connect(self.db_path) as conn:
            with suppress(sqlite3.Error):
                row = conn.execute(
                    "SELECT value FROM cache_meta WHERE key='last_order_id'"
                ).fetchone()
                if row and row[0] is not None:
                    self.last_order_id = int(row[0])

    def _save_last_order_id(self) -> None:
        """마지막 주문 ID를 캐시 DB에 저장합니다."""
        with suppress(sqlite3.Error):
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO cache_meta (key, value) VALUES ('last_order_id', ?) "
                    "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    (str(self.last_order_id),),
                )
                conn.commit()

    # ------------------------------------------------------------------
    def setup_sqlite(self) -> None:
        """로컬 SQLite 데이터베이스와 테이블을 초기화합니다."""
        conn = sqlite3.connect(self.db_path)
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            sql = f.read()
        statements = [
            s.strip() for s in sql.split(";") if s.strip() and not s.strip().startswith("--")
        ]
        for stmt in statements:
            with suppress(sqlite3.Error):
                conn.execute(stmt + ";")
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    def fetch_and_store_table(self, table_name: str) -> None:
        """Supabase에서 테이블을 가져와 SQLite에 저장합니다."""
        if not self.base_url:
            return
        if table_name not in VALID_TABLES:
            raise ValueError(f"Invalid table name: {table_name}")
        params = {"select": "*"}
        try:
            resp = requests.get(
                f"{self.base_url}/rest/v1/{table_name}",
                headers=self.headers,
                params=params,
                timeout=10,
            )
            resp.raise_for_status()
        except requests.Timeout:
            logger.error("Timeout while fetching table '%s'", table_name)
            return
        rows = resp.json()
        if not rows:
            return
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f'DELETE FROM "{table_name}"')
        cols = list(rows[0].keys())
        placeholders = ",".join(["?"] * len(cols))
        quoted_cols = ",".join([f'"{c}"' for c in cols])
        insert_sql = f'INSERT INTO "{table_name}" ({quoted_cols}) VALUES ({placeholders})'
        for row in rows:
            values = [row.get(col) for col in cols]
            cursor.execute(insert_sql, values)
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    def poll_new_orders(self) -> bool:
        """가장 최근 주문 ID를 확인하여 변경 여부를 반환합니다."""
        if not self.base_url:
            return False
        params = {"select": "order_id", "order": "order_id.desc", "limit": "1"}
        try:
            resp = requests.get(
                f"{self.base_url}/rest/v1/order",
                headers=self.headers,
                params=params,
                timeout=10,
            )
            resp.raise_for_status()
        except requests.Timeout:
            logger.error("Timeout while polling for new orders")
            return False
        data = resp.json()
        if data:
            current_id = data[0].get("order_id", 0)
            if current_id != self.last_order_id:
                self.last_order_id = current_id
                self._save_last_order_id()
                return True
        return False

    # ------------------------------------------------------------------
    def join_order_detail(self, order_id: int) -> Dict[str, Any]:
        """주문과 관련 테이블을 조인하여 상세 정보를 반환합니다."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = """
        SELECT o.order_id, o.is_dine_in, o.total_price, o.created_at,
               c.company_name,
               oi.order_item_id, oi.quantity, oi.item_price,
               mi.menu_name,
               opt.option_item_name, opt.option_price
        FROM "order" o
        JOIN company c ON c.company_id = o.company_id
        LEFT JOIN order_item oi ON oi.order_id = o.order_id
        LEFT JOIN menu_item mi ON mi.menu_item_id = oi.menu_item_id
        LEFT JOIN order_item_option oio ON oio.order_item_id = oi.order_item_id
        LEFT JOIN option_item opt ON opt.option_item_id = oio.option_item_id
        WHERE o.order_id = ?
        ORDER BY oi.order_item_id
        """
        rows = cursor.execute(query, (order_id,)).fetchall()
        conn.close()
        if not rows:
            return {}
        order: Dict[str, Any] = {
            "order_id": rows[0]["order_id"],
            "company_name": rows[0]["company_name"],
            "is_dine_in": bool(rows[0]["is_dine_in"]),
            "total_price": rows[0]["total_price"],
            "created_at": rows[0]["created_at"],
            "items": [],
        }
        item_map: Dict[int, Dict[str, Any]] = {}
        for row in rows:
            item_id = row["order_item_id"]
            if item_id not in item_map:
                item_map[item_id] = {
                    "name": row["menu_name"],
                    "quantity": row["quantity"],
                    "price": row["item_price"],
                    "options": [],
                }
            if row["option_item_name"]:
                item_map[item_id]["options"].append(
                    {"name": row["option_item_name"], "price": row["option_price"]}
                )
        order["items"] = list(item_map.values())
        return order

    # ------------------------------------------------------------------
    def get_recent_orders(self, limit: int = 50) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = """
        SELECT o.order_id, o.company_id, o.is_dine_in, o.total_price, o.created_at,
               c.company_name
        FROM "order" o
        JOIN company c ON c.company_id = o.company_id
        ORDER BY o.created_at DESC
        LIMIT ?
        """
        rows = cursor.execute(query, (limit,)).fetchall()
        conn.close()
        return [dict(row) for row in rows]
