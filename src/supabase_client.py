import os
import requests
from PySide6.QtCore import QObject, Signal

class SupabaseClient(QObject):
    """Supabase 데이터베이스와 연동하여 주문 데이터를 가져옵니다."""

    def __init__(self):
        super().__init__()
        project_id = os.getenv("SUPABASE_PROJECT_ID")
        self.base_url = os.getenv("SUPABASE_URL") or f"https://{project_id}.supabase.co"
        self.api_key = os.getenv("SUPABASE_API_KEY")
        self.headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
        }

    def get_orders(self, limit=10):
        """최근 주문 목록을 가져옵니다."""
        try:
            params = {
                "select": "*",
                "order": "created_at.desc",
                "limit": str(limit),
            }
            resp = requests.get(f"{self.base_url}/rest/v1/order", headers=self.headers, params=params)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"주문 데이터 조회 오류: {e}")
            return []

    def get_order_by_id(self, order_id):
        """특정 주문 ID의 상세 정보를 가져옵니다."""
        try:
            params = {
                "select": "*",
                "order_id": f"eq.{order_id}",
            }
            resp = requests.get(f"{self.base_url}/rest/v1/order", headers=self.headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data[0] if data else None
        except Exception as e:
            print(f"주문 상세 조회 오류: {e}")
            return None
