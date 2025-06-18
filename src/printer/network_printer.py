import logging
import socket
from src.printer.receipt_template import format_receipt_string

logger = logging.getLogger(__name__)

def print_receipt_network(order, address, port, timeout=5):
    """네트워크 프린터로 영수증을 출력합니다."""
    try:
        receipt_text = format_receipt_string(order)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((address, int(port)))
        sock.sendall(receipt_text.encode('cp949'))
        sock.close()
        logger.info(f"네트워크 프린터({address}:{port})로 영수증 전송 완료")
        return True
    except Exception as e:
        logger.error(f"네트워크 프린터 출력 실패: {e}")
        return False 