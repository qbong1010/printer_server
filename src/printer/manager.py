import json
import logging
from pathlib import Path
from typing import List
import win32print
from datetime import datetime, time

from src.printer.escpos_printer import print_receipt_esc_usb  # USB 프린터 출력 함수
from src.printer.file_printer import print_receipt as file_print_receipt, print_receipt_win  # 파일/윈도우 프린터 출력 함수
from src.printer.network_printer import print_receipt_network  # 네트워크 프린터 출력 함수

logger = logging.getLogger(__name__)


class PrinterManager:
    def __init__(self) -> None:
        # 프린터 설정 파일 경로
        self.config_file = Path("printer_config.json")
        self.load_config()

    def load_config(self) -> None:
        """프린터 설정을 로드합니다."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.printer_type = config.get("printer_type", "escpos")
                    self.printer_name = config.get("printer_name")
                    self.usb_info = config.get("usb_info", {})
                    self.network_info = config.get("network_info", {})
                    self.auto_print_config = config.get("auto_print", {
                        "enabled": False,
                        "retry_count": 3,
                        "retry_interval": 30,
                        "check_printer_status": True
                    })
            else:
                self.printer_name = win32print.GetDefaultPrinter()
                self.printer_type = "escpos"
                self.usb_info = {}
                self.network_info = {}
                self.auto_print_config = {
                    "enabled": False,
                    "retry_count": 3,
                    "retry_interval": 30,
                    "check_printer_status": True
                }
        except Exception as e:
            logger.exception("설정 로드 오류: %s", e)
            self.printer_name = win32print.GetDefaultPrinter()
            self.printer_type = "default"
            self.usb_info = {}
            self.network_info = {}
            self.auto_print_config = {
                "enabled": False,
                "retry_count": 3,
                "retry_interval": 30,
                "check_printer_status": True
            }

    def save_config(self) -> None:
        """프린터 설정을 저장합니다."""
        try:
            config = {
                "printer_type": self.printer_type,
                "printer_name": self.printer_name,
                "usb_info": getattr(self, "usb_info", {}),
                "network_info": getattr(self, "network_info", {}),
                "auto_print": getattr(self, "auto_print_config", {})
            }
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.exception("설정 저장 오류: %s", e)

    def get_current_printer(self) -> str:
        """현재 선택된 프린터 이름을 반환합니다."""
        return self.printer_name

    def get_printer_type(self) -> str:
        """현재 프린터 타입을 반환합니다."""
        return self.printer_type

    def set_printer(self, name: str) -> None:
        """프린터를 설정합니다."""
        self.printer_name = name
        self.save_config()

    def set_usb_info(self, vendor_id: str, product_id: str, interface: str) -> None:
        """USB 프린터 정보 설정"""
        self.usb_info = {
            "vendor_id": vendor_id,
            "product_id": product_id,
            "interface": interface
        }
        self.save_config()

    def set_network_info(self, address: str, port: str) -> None:
        """네트워크 프린터 정보 설정"""
        self.network_info = {
            "address": address,
            "port": port
        }
        self.save_config()

    def set_printer_type(self, printer_type: str, extra_info: dict = None) -> None:
        """프린터 타입을 설정합니다. 추가 정보도 저장 가능."""
        if printer_type not in ["escpos", "default", "network"]:
            raise ValueError("프린터 타입은 'escpos', 'default', 'network'여야 합니다.")
        self.printer_type = printer_type
        if extra_info:
            if printer_type == "escpos":
                self.set_usb_info(
                    extra_info.get("vendor_id", ""),
                    extra_info.get("product_id", ""),
                    extra_info.get("interface", "0")
                )
            elif printer_type == "network":
                self.set_network_info(
                    extra_info.get("address", ""),
                    extra_info.get("port", "9100")
                )
        self.save_config()

    def get_auto_print_config(self) -> dict:
        """자동 출력 설정을 반환합니다."""
        return self.auto_print_config.copy()

    def set_auto_print_config(self, config: dict) -> None:
        """자동 출력 설정을 업데이트합니다."""
        self.auto_print_config.update(config)
        self.save_config()

    def is_auto_print_enabled(self) -> bool:
        """자동 출력이 활성화되어 있는지 확인합니다."""
        return self.auto_print_config.get("enabled", False)

    def should_auto_print(self, order_data: dict) -> bool:
        """주문이 자동 출력 조건을 만족하는지 확인합니다."""
        order_id = order_data.get("order_id", "N/A")
        
        if not self.is_auto_print_enabled():
            logger.info(f"주문 {order_id}: 자동 출력이 비활성화되어 있음")
            return False
        
        # 이미 출력된 주문인지 확인
        if order_data.get("is_printed", False):
            logger.info(f"주문 {order_id}: 이미 출력됨")
            return False
                
        logger.info(f"주문 {order_id}: 자동 출력 조건을 만족함")
        return True

    def check_printer_status(self) -> bool:
        """프린터 상태를 확인합니다."""
        if not self.auto_print_config.get("check_printer_status", True):
            return True
            
        try:
            if self.printer_type == "default":
                # 윈도우 프린터 상태 확인
                flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
                printers = [p[2] for p in win32print.EnumPrinters(flags)]
                return self.printer_name in printers
            elif self.printer_type == "escpos":
                # ESC/POS 프린터의 경우 USB 정보가 있는지 확인
                usb_info = getattr(self, "usb_info", {})
                vendor_id = usb_info.get("vendor_id")
                product_id = usb_info.get("product_id")
                if not vendor_id or not product_id:
                    logger.warning("ESC/POS 프린터의 USB 정보가 설정되지 않았습니다.")
                    return False
                # USB 정보가 설정되어 있으면 일단 True로 반환 (실제 연결 테스트는 출력 시에 수행)
                return True
            elif self.printer_type == "network":
                # 네트워크 프린터의 경우 주소 정보가 있는지 확인
                network_info = getattr(self, "network_info", {})
                address = network_info.get("address")
                if not address:
                    logger.warning("네트워크 프린터의 주소가 설정되지 않았습니다.")
                    return False
                return True
            else:
                # 알 수 없는 프린터 타입
                logger.warning(f"알 수 없는 프린터 타입: {self.printer_type}")
                return False
        except Exception as e:
            logger.error(f"프린터 상태 확인 오류: {e}")
            return False

    def print_receipt(self, order_data: dict) -> bool:
        """주문 데이터를 기반으로 영수증을 출력합니다."""
        result = False
        error_msg = None

        # 1차: 실제 프린터 출력 시도
        if self.printer_type == "escpos":
            usb_info = getattr(self, "usb_info", {})
            result = print_receipt_esc_usb(
                order_data,
                int(usb_info.get("vendor_id"), 16),
                int(usb_info.get("product_id"), 16),
                usb_info.get("interface", 0)
            )
            if not result:
                error_msg = "ESC/POS 프린터 연결 실패"
        elif self.printer_type == "network":
            info = getattr(self, "network_info", {})
            address = info.get("address", "127.0.0.1")
            port = info.get("port", 9100)
            result = print_receipt_network(order_data, address, port)
            if not result:
                error_msg = f"네트워크 프린터({address}:{port}) 출력 실패"
        elif self.printer_type == "default":
            result = print_receipt_win(order_data, self.printer_name)
            if not result:
                error_msg = f"윈도우 프린터({self.printer_name}) 출력 실패"
        else:
            error_msg = "알 수 없는 프린터 타입, 파일로만 출력"

        # 실패 시 오류 로그 작성
        if error_msg:
            logger.error(error_msg)

        # 어떤 경우든 파일로 출력
        file_result = file_print_receipt(order_data)
        if not file_result:
            logger.error("파일 프린터 출력도 실패하였습니다.")

        # 파일 출력 성공 여부 반환
        return file_result

    @staticmethod
    def list_printers() -> List[str]:
        """사용 가능한 프린터 목록을 반환합니다."""
        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        return [p[2] for p in win32print.EnumPrinters(flags)]

    @staticmethod
    def get_default_printer() -> str:
        """기본 프린터 이름을 반환합니다."""
        return win32print.GetDefaultPrinter()