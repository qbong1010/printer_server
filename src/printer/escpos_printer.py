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

def _find_bulk_out_endpoint(vendor_id: int, product_id: int, interface: int = 0) -> Optional[int]:
    """지정된 VID/PID 장치에서 Bulk-OUT 엔드포인트 주소를 찾아 반환한다.
    실패 시 None 반환."""
    try:
        device = usb.core.find(idVendor=vendor_id, idProduct=product_id)
        if device is None:
            logger.warning("Target USB device not found while searching for Bulk-OUT endpoint")
            return None

        cfg = device.get_active_configuration()
        try:
            intf = cfg[(interface, 0)]  # 기본적으로 alternate setting 0 가정
        except KeyError:
            logger.warning(f"Interface {(interface, 0)} not found on device while searching for endpoint")
            return None

        for ep in intf:
            if (usb.util.endpoint_type(ep.bmAttributes) == usb.util.ENDPOINT_TYPE_BULK and
                    usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT):
                return ep.bEndpointAddress
    except Exception as e:
        logger.warning(f"Failed to detect Bulk-OUT endpoint: {e}")

    return None

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

            # Bulk-OUT 엔드포인트 자동 탐색
            out_ep = _find_bulk_out_endpoint(vendor_id, product_id, interface)
            if out_ep is not None:
                logger.info(f"Detected Bulk-OUT endpoint: 0x{out_ep:02X}")
            else:
                logger.warning("Bulk-OUT endpoint could not be detected automatically; letting escpos determine it")

            last_error = None
            for backend in BACKENDS:
                try:
                    logger.info(f"Trying backend: {backend}")
                    if out_ep is not None:
                        printer = Usb(vendor_id, product_id, interface, out_ep=out_ep, backend=backend)
                    else:
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
    try:
        def encode_text(text: str) -> bytes:
            """텍스트를 CP949로 인코딩"""
            try:
                return text.encode('cp949')
            except UnicodeEncodeError as e:
                logger.error(f"CP949 인코딩 오류: {e}")
                return text.encode('euc-kr', errors='replace')
        
        # 헤더
        p.set(align="center", bold=True, width=2, height=2)
        p.text(encode_text(f"{order.get('company_name', '')}\n"))
        p.set(align="center", bold=True)
        p.text(encode_text("*** 주문 영수증 ***\n\n"))
        
        # 주문 정보
        p.set(align="left")
        p.text(encode_text(f"주문번호: {order.get('order_id', '')}\n"))
        p.text(encode_text(f"주문일시: {order.get('created_at', '')}\n"))
        p.text(encode_text(f"주문유형: {'매장 식사' if order.get('is_dine_in', True) else '포장'}\n\n"))
        
        # 구분선
        p.text(encode_text("-" * 32 + "\n"))
        
        # 주문 항목
        p.set(align="left")
        total = 0
        for item in order["items"]:
            name = item["name"]
            qty = item["quantity"]
            price = item["price"]
            item_total = qty * price
            total += item_total
            
            p.text(encode_text(f"{name}\n"))
            # 옵션 출력
            for opt in item.get("options", []):
                p.text(encode_text(f"• {opt['name']}"))
                if opt['price'] > 0:
                    p.text(encode_text(f" (+{opt['price']:,}원)"))
                p.text(encode_text("\n"))
            
            p.text(encode_text(f"수량: {qty}개 x {price:,}원 = {item_total:,}원\n\n"))
        
        # 구분선
        p.text(encode_text("-" * 32 + "\n"))
        
        # 합계
        p.set(align="left")
        p.text(encode_text(f"소계: {total:,}원\n"))
        tax = int(total * 0.1)
        p.text(encode_text(f"부가세: {tax:,}원\n"))
        p.set(bold=True)
        p.text(encode_text(f"총 금액: {total:,}원\n\n"))
        
        # 푸터
        p.set(align="center")
        p.text(encode_text("감사합니다!\n"))
        p.text(encode_text("맛있게 드세요~\n\n"))
        
        # 출력 시간
        from datetime import datetime
        current_time = datetime.now()
        p.set(font='a', width=1, height=1)
        p.text(encode_text(f"출력시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"))
        
        # 커트
        p.cut()
        
        return total
        
    except Exception as e:
        logger.error(f"영수증 포맷팅 중 오류 발생: {str(e)}")
        raise

def print_receipt(order):
    """주문 정보를 받아 ESC/POS 프린터로 영수증을 출력한다."""
    try:
        logger.info("프린터 연결 시도...")
        printer = _get_printer()
        p = printer
        
        logger.info("영수증 출력 시작...")
        # 영수증 내용 출력
        total = _format_receipt_content(p, order)
        logger.info(f"영수증 출력 완료. 총액: {total:,}원")
        
        # 부분 커트만 실행
        p.cut(mode='partial')
        logger.info("프린터 커트 완료")
        
        return True
        
    except Exception as e:
        logger.error(f"프린터 출력 실패: {str(e)}")
        # ESC/POS 프린터 실패 시 윈도우 프린터로 폴백
        try:
            logger.info("윈도우 프린터로 폴백 시도...")
            from .manager import PrinterManager
            printer_manager = PrinterManager()
            printer_manager.set_printer_type("default")
            return printer_manager.print_receipt(order)
        except Exception as fallback_error:
            logger.error(f"윈도우 프린터 폴백도 실패: {str(fallback_error)}")
            raise

