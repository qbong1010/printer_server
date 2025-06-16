import logging
import os
from escpos.printer import File

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
        p.set(align='center', bold=True, width=2, height=2)
        p.text("ATOKETO\n")
        p.set(align='left', bold=False, width=1, height=1)
        p.text("주문번호: 123\n")
        p.text("메뉴: 아보카도 포케 x1\n")
        p.text("가격: 10,900원\n")
        p.text("결제: 현장결제\n")
        p.cut()
        return True
    except Exception as e:
        logger.exception("파일 프린터 오류: %s", e)
        return False 