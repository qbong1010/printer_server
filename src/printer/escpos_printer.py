"""ESC/POS 프린터 출력 유틸리티."""

from escpos.printer import Usb, Network, Serial
import os, serial
import logging
import usb.core
import usb.util
import sys
import win32print

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

def _get_printer():
    """환경변수에 지정된 설정을 바탕으로 프린터 인스턴스를 반환한다."""
    conn_type = os.getenv("POS_PRINTER_TYPE", "usb")
    address = os.getenv("POS_PRINTER_ADDRESS", "")
    
    logger.debug(f"Printer connection type: {conn_type}")
    logger.debug(f"Printer address: {address}")
    
    try:
        # 네트워크 프린터 연결
        if conn_type == "network" and address:
            logger.info(f"Attempting to connect to network printer at {address}")
            return Network(address)
            
        # 시리얼 프린터 연결
        elif conn_type == "serial" and address:
            logger.info(f"Attempting to connect to serial printer at {address}")
            return Serial(address)
            
        # USB 프린터 연결 (기본값)
        else:
            # 기본값 설정
            vendor_id = 0x0525  # VID_0525
            product_id = 0xA700  # PID_A700
            interface = 0
            
            if address:
                try:
                    # VID_0525&PID_A700 형식 처리
                    if '&' in address:
                        vid_pid = address.split('&')
                        if len(vid_pid) == 2:
                            vendor_id = int(vid_pid[0].replace('VID_', ''), 16)
                            product_id = int(vid_pid[1].replace('PID_', ''), 16)
                    else:
                        # 기존 형식 처리 (vendor:product:interface)
                        parts = address.split(":")
                        if len(parts) >= 2:
                            vendor_id = int(parts[0], 16)
                            product_id = int(parts[1], 16)
                            if len(parts) >= 3:
                                interface = int(parts[2])
                except ValueError as e:
                    logger.error(f"Invalid USB address format: {address}")
                    raise

            logger.info(f"Attempting to connect to USB printer with vendor_id={vendor_id:04x}, product_id={product_id:04x}, interface={interface}")
            
            # 사용 가능한 USB 장치 목록 로깅
            try:
                devices = usb.core.find(find_all=True)
                logger.info("Available USB devices:")
                for dev in devices:
                    logger.info(f"VID:{dev.idVendor:04x} PID:{dev.idProduct:04x}")
            except Exception as e:
                logger.warning(f"Failed to list USB devices: {e}")

            # 여러 백엔드 시도
            backends = ['libusb1', 'pyusb', 'openusb']
            last_error = None
            
            for backend in backends:
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

def print_receipt(order):
    """주문 정보를 받아 ESC/POS 프린터로 영수증을 출력한다."""
    try:
        printer = _get_printer()
        p = printer

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
        
        # 부분 커트 실행
        p.text("\n")
        p.text("----------------------------\n")
        p.text(f"총 합계: {total:,}원\n")
        p.text("\n감사합니다!\n")
        p.text("\n")
        p.cut(mode='partial')  # 부분 커트
        
        # 전체 커트 실행
        p.text("\n")
        p.text("----------------------------\n")
        p.text("영수증 끝\n")
        p.text("\n")
        p.cut(mode='full')  # 전체 커트
        
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

