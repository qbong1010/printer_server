import logging
from escpos.printer import Usb
import usb.backend.libusb1
from src.printer.receipt_template import format_receipt_string

logger = logging.getLogger(__name__)

def print_receipt_esc_usb(order, vendor_id, product_id, interface):
    """libusb DLL을 사용하여 USB 프린터로 영수증을 출력합니다."""
    receipt_text = format_receipt_string(order)

    # libusb DLL을 현재 디렉토리에서 로드
    backend = usb.backend.libusb1.get_backend(find_library=lambda x: "./libusb-1.0.dll")

    if backend is None:
        logger.error("libusb-1.0.dll을 로드할 수 없습니다. 백엔드 생성 실패.")
        return False

    try:
        # 백엔드를 명시적으로 전달
        printer = Usb(idVendor=vendor_id, idProduct=product_id, interface=interface, backend=backend)

        printer.text(receipt_text + '\n')
        printer.cut(mode='partial')
        printer.close()  # 명시적으로 닫기

        logger.info(f"USB 프린터(vID={vendor_id:04x}, pID={product_id:04x})로 영수증 전송 완료")
        return True

    except PermissionError as e:
        logger.error(f"USB 접근 권한이 없습니다: {e}")
    except usb.core.USBError as e:
        logger.error(f"USB 통신 오류: {e}")
    except Exception as e:
        logger.error(f"USB 프린터 출력 중 알 수 없는 오류 발생: {e}")

    return False
