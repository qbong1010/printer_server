import os
import asyncio
import requests
from PySide6.QtCore import QObject, Signal

class SupabaseClient(QObject):
    """Poll Supabase for new orders and emit them."""

    order_received = Signal(dict)

    def __init__(self, poll_interval=5):
        super().__init__()
        project_id = os.getenv("SUPABASE_PROJECT_ID")
        self.base_url = os.getenv("SUPABASE_URL") or f"https://{project_id}.supabase.co"
        self.api_key = os.getenv("SUPABASE_API_KEY")
        self.poll_interval = poll_interval
        self.running = False
        self.last_seen_id = None

    async def connect(self):
        self.running = True
        while self.running:
            try:
                await self._check_new_order()
            except Exception as exc:
                print(f"Supabase poll error: {exc}")
            await asyncio.sleep(self.poll_interval)

    async def _check_new_order(self):
        headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
        }
        params = {
            "select": "*",
            "order": "created_at.desc",
            "limit": "1",
        }
        resp = requests.get(f"{self.base_url}/rest/v1/order", headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return
        order = data[0]
        if self.last_seen_id == order["order_id"]:
            return
        self.last_seen_id = order["order_id"]
        self.order_received.emit(order)

    def stop(self):
        self.running = False
