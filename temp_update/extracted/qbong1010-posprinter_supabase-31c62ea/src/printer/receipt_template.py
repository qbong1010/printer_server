# -*- coding: utf-8 -*-
"""Common receipt printing utilities."""
from typing import Any, Dict
import logging
from datetime import datetime

# escpos 모듈은 선택적으로 로드 (에러 발생 시 우회)
try:
    from escpos.printer import file as escpos_file
    ESCPOS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ escpos 모듈 로드 실패 (receipt_template): {e}")
    print("   escpos 관련 기능은 비활성화됩니다.")
    ESCPOS_AVAILABLE = False

logger = logging.getLogger(__name__)

def format_receipt_string(order: Dict[str, Any]) -> str:
    lines = []

    # 기본값 일관성 유지
    company_name = order.get('company_name', '')
    order_id = order.get('order_id', '')
    created_at = order.get('created_at', '')
    is_dine_in = order.get('is_dine_in', True)

    # Header
    lines.append(company_name)
    lines.append("*** 주문 영수증 ***")
    lines.append("")  # 빈 줄

    # Order info
    lines.append(f"주문번호: {order_id}")
    lines.append(f"주문일시: {created_at}")
    lines.append(f"주문유형: {'매장 식사' if is_dine_in else '포장'}")
    lines.append("")  # 빈 줄

    lines.append("-" * 32)

    total = 0
    for item in order.get("items", []):
        name = item.get("name")
        qty = item.get("quantity", 0)
        price = item.get("price", 0)
        item_total = qty * price
        total += item_total

        lines.append(f"{name}")
        for opt in item.get("options", []):
            opt_line = f"- {opt['name']}"
            if opt.get("price", 0) > 0:
                opt_line += f" (+{opt['price']:,}원)"
            lines.append(opt_line)
        lines.append(f"수량: {qty}개 x {price:,}원 = {item_total:,}원")
        lines.append("")  # 아이템 간 빈 줄

    lines.append("-" * 32)
    tax = int(total * 0.1)
    lines.append(f"소계: {total:,}원")
    lines.append(f"총 금액: {total:,}원")
    lines.append("")  # 빈 줄
    lines.append("감사합니다!")
    lines.append("")  # 빈 줄

    current_time = datetime.now()
    lines.append(f"출력시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")  # 마지막 빈 줄

    return "\n".join(lines)
