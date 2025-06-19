import json
import logging
from pathlib import Path
from typing import List
import win32print
from datetime import datetime, time

from src.printer.escpos_printer import print_receipt_esc_usb  # USB 프린터 출력 함수
from src.printer.file_printer import print_receipt as file_print_receipt, print_receipt_win  # 파일/윈도우 프린터 출력 함수
from src.printer.network_printer import print_receipt_network  # 네트워크 프린터 출력 함수
from src.printer.com_printer import print_receipt_com, print_kitchen_receipt_com, test_com_printer  # COM 포트 프린터 출력 함수

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
                    
                    # 기존 설정에서 마이그레이션 필요한지 확인
                    if "customer_printer" not in config and "printer_type" in config:
                        logger.info("기존 설정을 새 형식으로 마이그레이션합니다.")
                        # 기존 설정을 새 형식으로 변환
                        old_printer_type = config.get("printer_type", "escpos")
                        old_printer_name = config.get("printer_name")
                        old_usb_info = config.get("usb_info", {})
                        old_network_info = config.get("network_info", {})
                        
                        self.customer_printer = {
                            "printer_type": old_printer_type,
                            "printer_name": old_printer_name,
                            "usb_info": old_usb_info,
                            "network_info": old_network_info
                        }
                        
                        # 기존 호환성 유지
                        self.printer_type = old_printer_type
                        self.printer_name = old_printer_name
                        self.usb_info = old_usb_info
                        self.network_info = old_network_info
                        
                        logger.info(f"마이그레이션된 손님용 설정: {self.customer_printer}")
                    else:
                        # 새 형식 설정 로드
                        self.customer_printer = config.get("customer_printer", {
                            "printer_type": "escpos",
                            "printer_name": None,
                            "usb_info": {},
                            "network_info": {}
                        })
                        # 기존 호환성을 위한 설정
                        self.printer_type = self.customer_printer.get("printer_type", "escpos")
                        self.printer_name = self.customer_printer.get("printer_name")
                        self.usb_info = self.customer_printer.get("usb_info", {})
                        self.network_info = self.customer_printer.get("network_info", {})
                    
                    # 주방용 프린터 설정
                    self.kitchen_printer = config.get("kitchen_printer", {
                        "printer_type": "com",
                        "com_port": "COM3",
                        "baudrate": 9600,
                        "enabled": True
                    })
                    
                    self.auto_print_config = config.get("auto_print", {
                        "enabled": False,
                        "retry_count": 3,
                        "retry_interval": 30,
                        "check_printer_status": True
                    })
                    
                    # 마이그레이션이 발생했다면 설정을 다시 저장
                    if "customer_printer" not in config:
                        self.save_config()
                        
            else:
                # 설정 파일이 없는 경우
                try:
                    default_printer = win32print.GetDefaultPrinter()
                except:
                    default_printer = "기본 프린터"
                
                self.customer_printer = {
                    "printer_type": "escpos",
                    "printer_name": default_printer,
                    "usb_info": {},
                    "network_info": {}
                }
                self.kitchen_printer = {
                    "printer_type": "com",
                    "com_port": "COM3",
                    "baudrate": 9600,
                    "enabled": True
                }
                # 기존 호환성
                self.printer_name = default_printer
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
            try:
                default_printer = win32print.GetDefaultPrinter()
            except:
                default_printer = "기본 프린터"
                
            self.customer_printer = {
                "printer_type": "default",
                "printer_name": default_printer,
                "usb_info": {},
                "network_info": {}
            }
            self.kitchen_printer = {
                "printer_type": "com",
                "com_port": "COM3",
                "baudrate": 9600,
                "enabled": True
            }
            # 기존 호환성
            self.printer_name = default_printer
            self.printer_type = "default"
            self.usb_info = {}
            self.network_info = {}
            self.auto_print_config = {
                "enabled": False,
                "retry_count": 3,
                "retry_interval": 30,
                "check_printer_status": True
            }
            
        logger.info(f"설정 로드 완료 - 손님용: {self.customer_printer}")
        logger.info(f"설정 로드 완료 - 주방용: {self.kitchen_printer}")

    def save_config(self) -> None:
        """프린터 설정을 저장합니다."""
        try:
            config = {
                "customer_printer": getattr(self, "customer_printer", {}),
                "kitchen_printer": getattr(self, "kitchen_printer", {}),
                "auto_print": getattr(self, "auto_print_config", {}),
                # 기존 호환성을 위한 설정
                "printer_type": self.printer_type,
                "printer_name": self.printer_name,
                "usb_info": getattr(self, "usb_info", {}),
                "network_info": getattr(self, "network_info", {})
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
        """프린터 타입을 설정합니다. 추가 정보도 저장 가능. (기존 호환성 유지)"""
        self.set_customer_printer_type(printer_type, extra_info)

    def set_customer_printer_type(self, printer_type: str, extra_info: dict = None) -> None:
        """손님용 프린터 타입을 설정합니다."""
        if printer_type not in ["escpos", "default", "network"]:
            raise ValueError("프린터 타입은 'escpos', 'default', 'network'여야 합니다.")
        
        if not hasattr(self, 'customer_printer'):
            self.customer_printer = {}
        
        self.customer_printer["printer_type"] = printer_type
        self.printer_type = printer_type  # 기존 호환성
        
        if extra_info:
            if printer_type == "escpos":
                self.customer_printer["usb_info"] = {
                    "vendor_id": extra_info.get("vendor_id", ""),
                    "product_id": extra_info.get("product_id", ""),
                    "interface": extra_info.get("interface", "0")
                }
                self.usb_info = self.customer_printer["usb_info"]  # 기존 호환성
            elif printer_type == "network":
                self.customer_printer["network_info"] = {
                    "address": extra_info.get("address", ""),
                    "port": extra_info.get("port", "9100")
                }
                self.network_info = self.customer_printer["network_info"]  # 기존 호환성
        else:
            # extra_info가 없을 때는 기존 설정을 유지
            if printer_type == "escpos" and hasattr(self, 'usb_info'):
                self.customer_printer["usb_info"] = self.usb_info.copy()
            elif printer_type == "network" and hasattr(self, 'network_info'):
                self.customer_printer["network_info"] = self.network_info.copy()
        
        logger.info(f"손님용 프린터 타입 설정: {printer_type}, 정보: {extra_info}")
        logger.info(f"설정 후 customer_printer: {self.customer_printer}")
        self.save_config()

    def set_kitchen_printer_config(self, com_port: str = "COM3", baudrate: int = 9600, enabled: bool = True) -> None:
        """주방용 프린터 설정을 업데이트합니다."""
        if not hasattr(self, 'kitchen_printer'):
            self.kitchen_printer = {}
        
        self.kitchen_printer.update({
            "printer_type": "com",
            "com_port": com_port,
            "baudrate": baudrate,
            "enabled": enabled
        })
        self.save_config()

    def get_customer_printer_config(self) -> dict:
        """손님용 프린터 설정을 반환합니다."""
        return getattr(self, "customer_printer", {}).copy()

    def get_kitchen_printer_config(self) -> dict:
        """주방용 프린터 설정을 반환합니다."""
        return getattr(self, "kitchen_printer", {}).copy()

    def test_kitchen_printer(self) -> bool:
        """주방용 프린터 연결을 테스트합니다."""
        kitchen_config = getattr(self, "kitchen_printer", {})
        com_port = kitchen_config.get("com_port", "COM3")
        baudrate = kitchen_config.get("baudrate", 9600)
        return test_com_printer(com_port, baudrate)

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
        """주문 데이터를 기반으로 영수증을 출력합니다. (기존 호환성 유지)"""
        return self.print_customer_receipt(order_data)

    def print_customer_receipt(self, order_data: dict) -> bool:
        """손님용 영수증을 출력합니다."""
        result = False
        error_msg = None

        customer_config = getattr(self, "customer_printer", {})
        printer_type = customer_config.get("printer_type", self.printer_type)
        
        logger.info(f"손님용 프린터 출력 시작 - 타입: {printer_type}")
        logger.info(f"customer_config: {customer_config}")
        logger.info(f"기존 호환성 printer_type: {self.printer_type}")

        # 손님용 프린터 출력 시도
        if printer_type == "escpos":
            usb_info = customer_config.get("usb_info", getattr(self, "usb_info", {}))
            logger.info(f"ESC/POS USB 정보: {usb_info}")
            
            if usb_info.get("vendor_id") and usb_info.get("product_id"):
                try:
                    vendor_id = int(usb_info.get("vendor_id"), 16)
                    product_id = int(usb_info.get("product_id"), 16)
                    interface = usb_info.get("interface", 0)
                    
                    logger.info(f"ESC/POS 프린터 연결 시도: VID={vendor_id:04X}, PID={product_id:04X}, Interface={interface}")
                    
                    result = print_receipt_esc_usb(
                        order_data,
                        vendor_id,
                        product_id,
                        interface
                    )
                    if result:
                        logger.info("손님용 ESC/POS 프린터 출력 성공")
                    else:
                        error_msg = "손님용 ESC/POS 프린터 연결 실패"
                except ValueError as e:
                    error_msg = f"손님용 ESC/POS 프린터 USB ID 변환 오류: {e}"
                    logger.error(error_msg)
            else:
                error_msg = f"손님용 ESC/POS 프린터 USB 정보 없음 - VID: {usb_info.get('vendor_id')}, PID: {usb_info.get('product_id')}"
                logger.error(error_msg)
        elif printer_type == "network":
            network_info = customer_config.get("network_info", getattr(self, "network_info", {}))
            address = network_info.get("address", "127.0.0.1")
            port = network_info.get("port", 9100)
            logger.info(f"네트워크 프린터 연결 시도: {address}:{port}")
            result = print_receipt_network(order_data, address, port)
            if not result:
                error_msg = f"손님용 네트워크 프린터({address}:{port}) 출력 실패"
        elif printer_type == "default":
            printer_name = customer_config.get("printer_name", self.printer_name)
            logger.info(f"윈도우 프린터 출력 시도: {printer_name}")
            result = print_receipt_win(order_data, printer_name)
            if not result:
                error_msg = f"손님용 윈도우 프린터({printer_name}) 출력 실패"
        else:
            error_msg = f"알 수 없는 손님용 프린터 타입: {printer_type}"

        # 실패 시 오류 로그 작성
        if error_msg:
            logger.error(error_msg)

        # 어떤 경우든 파일로 출력
        file_result = file_print_receipt(order_data)
        if not file_result:
            logger.error("파일 프린터 출력도 실패하였습니다.")
        else:
            logger.info("파일 프린터 출력 성공")

        # 손님용 프린터 출력 성공 여부 반환
        logger.info(f"손님용 프린터 출력 결과: 실제프린터={result}, 파일={file_result}")
        return result or file_result

    def print_kitchen_receipt(self, order_data: dict) -> bool:
        """주방용 영수증을 출력합니다."""
        kitchen_config = getattr(self, "kitchen_printer", {})
        
        # 주방 프린터가 비활성화된 경우
        if not kitchen_config.get("enabled", True):
            logger.info("주방 프린터가 비활성화되어 있습니다.")
            return True

        printer_type = kitchen_config.get("printer_type", "com")
        
        if printer_type == "com":
            com_port = kitchen_config.get("com_port", "COM3")
            baudrate = kitchen_config.get("baudrate", 9600)
            result = print_kitchen_receipt_com(order_data, com_port, baudrate)
            if result:
                logger.info(f"주방용 영수증 출력 성공: {com_port}")
            else:
                logger.error(f"주방용 COM 포트 프린터({com_port}) 출력 실패")
            return result
        else:
            logger.warning(f"지원하지 않는 주방 프린터 타입: {printer_type}")
            return False

    def print_both_receipts(self, order_data: dict) -> dict:
        """손님용과 주방용 영수증을 모두 출력합니다."""
        results = {
            "customer": False,
            "kitchen": False
        }
        
        # 손님용 영수증 출력
        try:
            results["customer"] = self.print_customer_receipt(order_data)
        except Exception as e:
            logger.error(f"손님용 영수증 출력 오류: {e}")
            results["customer"] = False
        
        # 주방용 영수증 출력
        try:
            results["kitchen"] = self.print_kitchen_receipt(order_data)
        except Exception as e:
            logger.error(f"주방용 영수증 출력 오류: {e}")
            results["kitchen"] = False
        
        return results

    @staticmethod
    def list_printers() -> List[str]:
        """사용 가능한 프린터 목록을 반환합니다."""
        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        return [p[2] for p in win32print.EnumPrinters(flags)]

    @staticmethod
    def get_default_printer() -> str:
        """기본 프린터 이름을 반환합니다."""
        return win32print.GetDefaultPrinter()