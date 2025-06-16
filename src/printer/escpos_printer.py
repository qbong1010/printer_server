from escpos.printer import Usb, Network, Serial
import os, serial
import logging
import usb.core
import usb.util
import sys
import win32print
from typing import Optional, Dict, Any, Tuple
from functools import lru_cache
import socket

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('printer_debug.log')
    ]
)
logger = logging.getLogger(__name__)

# 프린터 설정 상수
DEFAULT_VENDOR_ID = 0x0525
DEFAULT_PRODUCT_ID = 0xA700
DEFAULT_INTERFACE = 0
BACKENDS = ['libusb1', 'pyusb', 'openusb']

# 네트워크 프린터 설정
DEFAULT_NETWORK_PORT = 9100
DEFAULT_NETWORK_TIMEOUT = 5
DEFAULT_NETWORK_RETRY_COUNT = 3
DEFAULT_NETWORK_RETRY_DELAY = 1

def _check_network_printer(address: str, port: int = DEFAULT_NETWORK_PORT, timeout: int = DEFAULT_NETWORK_TIMEOUT) -> bool:
    """네트워크 프린터 연결 가능 여부를 확인"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((address, port))
        sock.close()
        return result == 0
    except Exception as e:
        logger.warning(f"Network printer check failed: {e}")
        return False

def _parse_network_address(address: str) -> Tuple[str, int]:
    """네트워크 주소 문자열을 파싱하여 호스트와 포트 반환"""
    if not address:
        raise ValueError("Network address cannot be empty")
        
    try:
        if ':' in address:
            host, port_str = address.rsplit(':', 1)
            port = int(port_str)
        else:
            host = address
            port = DEFAULT_NETWORK_PORT
            
        return host, port
    except ValueError as e:
        logger.error(f"Invalid network address format: {address}")
        raise

@lru_cache(maxsize=1)
def _get_usb_devices():
    """USB 장치 목록을 캐시하여 반환"""
    try:
        return list(usb.core.find(find_all=True))
    except Exception as e:
        logger.warning(f"Failed to list USB devices: {e}")
        return []

def _parse_usb_address(address: str) -> tuple[int, int, int]:
    """USB 주소 문자열을 파싱하여 vendor_id, product_id, interface 반환"""
    vendor_id = DEFAULT_VENDOR_ID
    product_id = DEFAULT_PRODUCT_ID
    interface = DEFAULT_INTERFACE
    
    if not address:
        return vendor_id, product_id, interface
        
    try:
        if '&' in address:
            vid_pid = address.split('&')
            if len(vid_pid) == 2:
                vendor_id = int(vid_pid[0].replace('VID_', ''), 16)
                product_id = int(vid_pid[1].replace('PID_', ''), 16)
        else:
            parts = address.split(":")
            if len(parts) >= 2:
                vendor_id = int(parts[0], 16)
                product_id = int(parts[1], 16)
                if len(parts) >= 3:
                    interface = int(parts[2])
    except ValueError as e:
        logger.error(f"Invalid USB address format: {address}")
        raise
        
    return vendor_id, product_id, interface

def _get_printer():
    """환경변수에 지정된 설정을 바탕으로 프린터 인스턴스를 반환한다."""
    conn_type = os.getenv("POS_PRINTER_TYPE", "usb")
    address = os.getenv("POS_PRINTER_ADDRESS", "")
    
    logger.debug(f"Printer connection type: {conn_type}")
    logger.debug(f"Printer address: {address}")
    
    try:
        if conn_type == "network" and address:
            host, port = _parse_network_address(address)
            logger.info(f"Attempting to connect to network printer at {host}:{port}")
            
            # 네트워크 프린터 연결 가능 여부 확인
            if not _check_network_printer(host, port):
                raise ConnectionError(f"Cannot connect to network printer at {host}:{port}")
                
            return Network(host, port=port, timeout=DEFAULT_NETWORK_TIMEOUT)
            
        elif conn_type == "serial" and address:
            logger.info(f"Attempting to connect to serial printer at {address}")
            return Serial(address)
            
        else:
            vendor_id, product_id, interface = _parse_usb_address(address)
            logger.info(f"Attempting to connect to USB printer with vendor_id={vendor_id:04x}, product_id={product_id:04x}, interface={interface}")
            
            # USB 장치 목록 로깅 (캐시된 결과 사용)
            devices = _get_usb_devices()
            if devices:
                logger.info("Available USB devices:")
                for dev in devices:
                    logger.info(f"VID:{dev.idVendor:04x} PID:{dev.idProduct:04x}")

            last_error = None
            for backend in BACKENDS:
                try:
                    logger.info(f"Trying backend: {backend}")
                    printer = Usb(vendor_id, product_id, interface, backend=backend)
                    logger.info(f"Successfully connected using {backend} backend")
                    return printer
                except Exception as e:
                    last_error = e
                    logger.warning(f"Failed with backend {backend}: {str(e)}")
                    continue
            
            if last_error:
                logger.error(f"All backends failed. Last error: {last_error}")
                raise last_error

    except Exception as e:
        logger.error(f"Failed to initialize printer: {str(e)}")
        raise

def _format_receipt_content(p: Any, order: Dict[str, Any]) -> None:
    """영수증 내용을 포맷팅하여 출력"""
    # 회사명 출력
    p.set(align="center", bold=True, width=2, height=2)
    p.text(f"{order.get('company_name', '')}\n")
    p.text(f"픽업번호 : {order['pickup_number']}\n")

    p.set(align="center")
    p.text("-" * 32 + "\n")

    p.set(align="left", bold=False)
    p.text(f"유형 : {order['order_type']}\n")
    p.text(f"주문접수시간 : {order['timestamp']}\n")

    p.text("-" * 32 + "\n")
    p.text("메뉴           수량   금액\n")

    total = 0
    for item in order["items"]:
        name = item["name"]
        qty = item["quantity"]
        price = item["price"]
        total += qty * price

        p.text(f"{name:<14} {qty:<3} {price:>6,}\n")
        if "note" in item:
            p.text(f"{item['note']}\n")

    p.text("-" * 32 + "\n")
    p.set(align="right", bold=True)
    p.text(f"합계      {total:,.0f}\n")
    p.set(align="left", bold=False)
    p.text("-" * 32 + "\n")

    if 'disposable_needed' in order:
        p.text(f"일회용수저필요 : {order['disposable_needed']}\n")
    
    p.text("\n")
    p.text("----------------------------\n")
    p.text(f"총 합계: {total:,}원\n")
    p.text("\n감사합니다!\n")
    p.text("\n")
    
    return total

def print_receipt(order):
    """주문 정보를 받아 ESC/POS 프린터로 영수증을 출력한다."""
    try:
        printer = _get_printer()
        p = printer

        # 영수증 내용 출력
        _format_receipt_content(p, order)
        
        # 부분 커트만 실행 (전체 커트는 불필요)
        p.cut(mode='partial')
        
    except Exception as e:
        logger.error(f"Failed to print receipt: {str(e)}")
        # ESC/POS 프린터 실패 시 윈도우 프린터로 폴백
        try:
            from .manager import PrinterManager
            printer_manager = PrinterManager()
            printer_manager.set_printer_type("default")
            return printer_manager.print_receipt(order)
        except Exception as fallback_error:
            logger.error(f"Fallback to Windows printer also failed: {str(fallback_error)}")
            raise

