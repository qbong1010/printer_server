import logging
import os
from escpos.printer import File
from .receipt_template import format_receipt

logger = logging.getLogger(__name__)

def print_receipt(order_data: dict) -> bool:
    """주문 데이터를 기반으로 파일로 영수증 출력"""
    try:
        # 현재 스크립트의 디렉토리를 기준으로 출력 파일 경로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(current_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "test_print_output.bin")
        
        p = File(output_file, encoding='cp949')
        format_receipt(p, order_data)
        return True
    except Exception as e:
        logger.exception("파일 프린터 오류: %s", e)
        return False 