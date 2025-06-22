import ast
import logging
import os
import re
from typing import Optional

logger = logging.getLogger(__name__)


def clean_escpos_bytes(data: bytes) -> bytes:
    # 0x00~0x1F (제어문자), 0x7F(DEL) 제거
    return bytes([b for b in data if b >= 0x20 or b in (0x0a, 0x0d)])

def try_decodings(data: bytes):
    for enc in ['cp949', 'euc-kr', 'utf-8']:
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode('latin1', errors='replace')

def read_receipt_file() -> Optional[str]:
    """`test_print_output.bin` 파일을 읽어 영수증 텍스트를 반환한다."""
    try:
        # gui 폴더에서 printer/output 폴더로의 상대 경로 수정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(current_dir, "..", "printer", "output", "test_receipt_output.bin")

        if not os.path.exists(path):
            return "영수증 파일이 없습니다."

        # 바이너리 모드로 읽기 (encoding, errors 옵션 X)
        with open(path, "rb") as f:
            content = f.read()

        cleaned = clean_escpos_bytes(content)
        decoded = try_decodings(cleaned)
        return decoded

    except Exception as e:
        logger.exception("영수증 파일 미리보기 생성 중 오류 발생")
        return f"오류가 발생했습니다: {e}" 