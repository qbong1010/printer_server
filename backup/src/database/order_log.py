import sqlite3
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class OrderDatabase:
    def __init__(self, db_path: str = "orders.db") -> None:
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self):
        """필요한 테이블 생성"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 주문 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    customer_name TEXT,
                    payment_method TEXT,
                    total_amount INTEGER,
                    order_date TIMESTAMP,
                    order_data TEXT
                )
            """)
            
            conn.commit()
    
    def add_order(self, order_data: Dict[str, Any]) -> bool:
        """새로운 주문을 데이터베이스에 추가"""
        try:
            # 총액 계산
            total_amount = sum(
                item["price"] * item["quantity"]
                for item in order_data["items"]
            )
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO orders (
                        order_id,
                        customer_name,
                        payment_method,
                        total_amount,
                        order_date,
                        order_data
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    order_data["order_id"],
                    order_data["customer_name"],
                    order_data["payment_method"],
                    total_amount,
                    datetime.now(),
                    json.dumps(order_data, ensure_ascii=False)
                ))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            logger.warning("주문 ID %s 가 이미 존재합니다.", order_data['order_id'])
            return False
        except Exception as e:
            logger.exception("주문 저장 중 오류 발생: %s", e)
            return False
    
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """주문 ID로 주문 정보 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT order_data
                FROM orders
                WHERE order_id = ?
            """, (order_id,))
            
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])
            return None
    
    def get_recent_orders(self, limit: int = 50) -> List[Dict[str, Any]]:
        """최근 주문 목록 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT order_data
                FROM orders
                ORDER BY order_date DESC
                LIMIT ?
            """, (limit,))
            
            return [json.loads(row[0]) for row in cursor.fetchall()] 