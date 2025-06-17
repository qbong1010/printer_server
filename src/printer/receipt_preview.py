# -*- coding: utf-8 -*-
"""Receipt preview utility.

`test_print_output.bin` 과 같은 ESC/POS 출력 파일에서 한글 영수증 텍스트만 추출해
미리보기 용 문자열로 반환한다.

파일 내부는 다음과 같은 특징을 가진다.
1. 실제 ESC/POS 제어 시퀀스 (ESC, GS 등)가 포함돼 있다.
2. 텍스트는 파이썬의 bytes literal 형태인  b'...<cp949 bytes>...' 로 삽입돼 있다.
   - 일부 경우 ESC, a, M 등의 알파벳이 bytes literal 앞에 붙어있는 형태(E, a, M, d, V 등)
3. 우리는 제어 명령을 건너뛰고  b' 와 ' 사이에 있는 순수 바이트를 모아 cp949 로 디코딩한다.
"""
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
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(current_dir, "output", "test_receipt_output.bin")

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