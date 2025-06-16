from dataclasses import dataclass
from datetime import time

class OrderStatus:
    """주문 출력 상태 값"""
    NEW = "신규"
    PRINTING = "출력중"
    PRINTED = "출력완료"
    PRINT_FAILED = "출력실패"

@dataclass
class PrintSettings:
    """자동 출력 동작을 제어하는 설정"""
    auto_print_enabled: bool = True
    print_retry_count: int = 3
    print_retry_interval: int = 30  # seconds
    business_hours_start: time = time(0, 0)
    business_hours_end: time = time(23, 59)
    print_dine_in_only: bool = False
