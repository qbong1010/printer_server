import logging
from escpos.printer import Usb
import usb.backend.libusb1
from src.printer.receipt_template import format_receipt_string

logger = logging.getLogger(__name__)

# ESC/POS 프린터 스타일 명령어
STYLE_COMMANDS = {
    'init': b'\x1b\x40',  # 프린터 초기화
    'center': b'\x1b\x61\x01',  # 가운데 정렬
    'left': b'\x1b\x61\x00',  # 왼쪽 정렬
    'right': b'\x1b\x61\x02',  # 오른쪽 정렬
    'text_2x': b'\x1d\x21\x11',  # 글자 크기 2배
    'text_normal': b'\x1d\x21\x00',  # 기본 글자 크기
    'cut': b'\x1d\x56\x41\x00'  # 용지 자르기
}

def print_receipt_esc_usb(order, vendor_id, product_id, interface, codepage=0x13):
    """libusb DLL을 사용하여 USB 프린터로 영수증을 출력합니다.
    
    Args:
        order: 주문 정보 딕셔너리
        vendor_id: USB 벤더 ID
        product_id: USB 제품 ID
        interface: USB 인터페이스 번호
        codepage: 프린터 코드페이지 (기본값: 0x13 = 19)
            - 0x03 (3): CP949 / 완성형 한글
            - 0x13 (19): CP949 / 조합형 한글
    """
    try:
        receipt_text = format_receipt_string(order)
    except Exception as e:
        logger.error(f"영수증 텍스트 포맷팅 중 오류 발생: {e}")
        return False

    # libusb DLL을 현재 디렉토리에서 로드
    backend = usb.backend.libusb1.get_backend(find_library=lambda x: "./libusb-1.0.dll")

    if backend is None:
        logger.error("libusb-1.0.dll을 로드할 수 없습니다. 백엔드 생성 실패.")
        return False

    try:
        # 백엔드를 명시적으로 전달
        printer = Usb(idVendor=vendor_id, idProduct=product_id, interface=interface, backend=backend)
        
        # 프린터 초기화 및 인코딩 설정
        printer._raw(STYLE_COMMANDS['init'])  # 프린터 초기화
        printer._raw(bytes([0x1b, 0x74, codepage]))  # 코드페이지 설정
        printer.encoding = 'cp949'  # python-escpos의 인코딩 속성 지정

        try:
            # 영수증 텍스트를 CP949로 직접 인코딩하여 바이트로 전송
            lines = receipt_text.split('\n')
            for line in lines:
                if '*** 주문 영수증 ***' in line:
                    printer._raw(STYLE_COMMANDS['center'])  # 가운데 정렬
                    printer._raw(STYLE_COMMANDS['text_2x'])  # 글자 크기 2배
                    printer._raw(line.encode('cp949', errors='strict') + b'\n')
                    printer._raw(STYLE_COMMANDS['text_normal'])  # 기본 글자 크기
                    printer._raw(STYLE_COMMANDS['left'])  # 왼쪽 정렬
                else:
                    printer._raw(line.encode('cp949', errors='strict') + b'\n')
            
            printer._raw(STYLE_COMMANDS['cut'])  # 용지 자르기
        except UnicodeEncodeError as e:
            logger.error(f"텍스트 인코딩 중 오류 발생: {e}")
            logger.error(f"인코딩 실패한 텍스트: {receipt_text}")
            return False
        finally:
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
