# -*- coding: utf-8 -*-
"""Common receipt printing utilities."""
from typing import Any, Dict
import logging
from escpos.printer import file
from datetime import datetime

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
    lines.append("*** 주문 영수증 ***\n")

    # Order info
    lines.append(f"주문번호: {order_id}")
    lines.append(f"주문일시: {created_at}")
    lines.append(f"주문유형: {'매장 식사' if is_dine_in else '포장'}\n")

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
        lines.append(f"수량: {qty}개 x {price:,}원 = {item_total:,}원\n")

    lines.append("-" * 32)
    tax = int(total * 0.1)
    lines.append(f"소계: {total:,}원")
    lines.append(f"총 금액: {total:,}원\n")
    lines.append("감사합니다!\n")

    current_time = datetime.now()
    lines.append(f"출력시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    return "\n".join(lines)


print(format_receipt_string(order))
