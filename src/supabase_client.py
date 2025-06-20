import os
import logging
import platform
import socket
import uuid
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)

class SupabaseClient(QObject):
    """Supabase 데이터베이스와 연동하여 주문 데이터를 가져오고 로그를 전송합니다."""

    def __init__(self) -> None:
        super().__init__()
        project_id = os.getenv("SUPABASE_PROJECT_ID")
        self.base_url = os.getenv("SUPABASE_URL") or f"https://{project_id}.supabase.co"
        self.api_key = os.getenv("SUPABASE_API_KEY")
        self.headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        # 클라이언트 고유 정보 생성
        self.client_info = self._generate_client_info()

    def _generate_client_info(self) -> Dict[str, str]:
        """클라이언트 고유 정보를 생성합니다."""
        try:
            # 클라이언트 ID 생성 (MAC 주소 기반)
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0,2*6,2)][::-1])
            client_id = f"pos_client_{mac.replace(':', '')}"
            
            # 컴퓨터 이름 획득
            try:
                client_name = socket.gethostname()
            except:
                client_name = "Unknown"
            
            # OS 정보
            os_info = f"{platform.system()} {platform.release()} {platform.architecture()[0]}"
            
            # 앱 버전 (version.json에서 읽기)
            app_version = "1.0.0"  # 기본값
            try:
                with open("version.json", "r", encoding="utf-8") as f:
                    version_data = json.load(f)
                    app_version = version_data.get("version", "1.0.0")
            except:
                pass
            
            return {
                "client_id": client_id,
                "client_name": client_name,
                "os_info": os_info,
                "app_version": app_version
            }
        except Exception as e:
            logger.warning(f"클라이언트 정보 생성 실패: {e}")
            return {
                "client_id": f"pos_client_{uuid.uuid4().hex[:12]}",
                "client_name": "Unknown",
                "os_info": "Unknown",
                "app_version": "1.0.0"
            }

    def send_log(
        self, 
        log_level: str,
        log_type: str,
        message: str,
        error_details: Optional[str] = None,
        module_name: Optional[str] = None,
        function_name: Optional[str] = None,
        line_number: Optional[int] = None
    ) -> bool:
        """로그를 Supabase에 전송합니다."""
        try:
            log_data = {
                "client_id": self.client_info["client_id"],
                "client_name": self.client_info["client_name"],
                "log_level": log_level.upper(),
                "log_type": log_type,
                "message": message,
                "error_details": error_details,
                "module_name": module_name,
                "function_name": function_name,
                "line_number": line_number,
                "app_version": self.client_info["app_version"],
                "os_info": self.client_info["os_info"]
            }
            
            # None 값 제거
            log_data = {k: v for k, v in log_data.items() if v is not None}
            
            response = requests.post(
                f"{self.base_url}/rest/v1/app_logs",
                headers=self.headers,
                json=log_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return True
            else:
                logger.warning(f"로그 전송 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.warning(f"로그 전송 중 오류 발생: {e}")
            return False

    def send_startup_log(self) -> bool:
        """애플리케이션 시작 로그를 전송합니다."""
        return self.send_log(
            log_level="INFO",
            log_type="startup",
            message="POS 프린터 애플리케이션이 시작되었습니다.",
            module_name="main"
        )

    def send_shutdown_log(self) -> bool:
        """애플리케이션 종료 로그를 전송합니다."""
        return self.send_log(
            log_level="INFO",
            log_type="shutdown",
            message="POS 프린터 애플리케이션이 종료되었습니다.",
            module_name="main"
        )

    def send_error_log(
        self, 
        message: str, 
        error_details: str, 
        module_name: str = None,
        function_name: str = None,
        line_number: int = None
    ) -> bool:
        """오류 로그를 전송합니다."""
        return self.send_log(
            log_level="ERROR",
            log_type="error",
            message=message,
            error_details=error_details,
            module_name=module_name,
            function_name=function_name,
            line_number=line_number
        )

    def get_client_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """현재 클라이언트의 로그를 조회합니다."""
        try:
            params = {
                "select": "*",
                "client_id": f"eq.{self.client_info['client_id']}",
                "order": "created_at.desc",
                "limit": str(limit)
            }
            
            response = requests.get(
                f"{self.base_url}/rest/v1/app_logs",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"로그 조회 실패: {response.status_code}")
                return []
                
        except Exception as e:
            logger.warning(f"로그 조회 중 오류 발생: {e}")
            return []

    def get_orders(self, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 주문 목록을 가져옵니다."""
        try:
            # 주문 기본 정보 조회
            params = {
                "select": """
                    order_id,
                    company_id,
                    is_dine_in,
                    total_price,
                    created_at,
                    is_printed,
                    company!inner(company_name),
                    order_items!inner(
                        order_item_id,
                        quantity,
                        item_price,
                        menu_item!inner(menu_name),
                        options!inner(
                            option_item!inner(
                                option_item_name,
                                option_price
                            )
                        )
                    )
                """,
                "order": "created_at.desc",
                "limit": str(limit),
            }
            resp = requests.get(f"{self.base_url}/rest/v1/order", headers=self.headers, params=params)
            resp.raise_for_status()
            orders = resp.json()
            
            # 데이터 구조 변환
            formatted_orders = []
            for order in orders:
                try:
                    # 회사 정보 추출
                    company_info = order.get("company", {})
                    company_name = company_info.get("company_name", "N/A") if company_info else "N/A"
                    
                    formatted_order = {
                        "order_id": str(order.get("order_id", "N/A")),
                        "company_name": company_name,
                        "is_dine_in": order.get("is_dine_in", True),
                        "total_price": order.get("total_price", 0),
                        "created_at": order.get("created_at"),
                        "is_printed": order.get("is_printed", False),
                        "items": []
                    }
                    
                    # 주문 항목 처리
                    order_items = order.get("order_items", [])
                    for item in order_items:
                        menu_item_info = item.get("menu_item", {})
                        menu_name = menu_item_info.get("menu_name", "N/A") if menu_item_info else "N/A"
                        
                        menu_item = {
                            "name": menu_name,
                            "quantity": item.get("quantity", 1),
                            "price": item.get("item_price", 0),
                            "options": []
                        }
                        
                        # 옵션 처리
                        options = item.get("options", [])
                        for option in options:
                            option_item_info = option.get("option_item", {})
                            if option_item_info:
                                menu_item["options"].append({
                                    "name": option_item_info.get("option_item_name", "N/A"),
                                    "price": option_item_info.get("option_price", 0)
                                })
                        
                        formatted_order["items"].append(menu_item)
                    
                    formatted_orders.append(formatted_order)
                except Exception as e:
                    logger.exception("주문 데이터 변환 중 오류: %s", e)
                    continue
            
            return formatted_orders
            
        except Exception as e:
            logger.exception("주문 데이터 조회 오류: %s", e)
            return []

    def get_order_by_id(self, order_id: int) -> Optional[Dict[str, Any]]:
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
            logger.exception("주문 상세 조회 오류: %s", e)
            return None
