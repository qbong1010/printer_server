# -*- coding: utf-8 -*-
"""Common receipt printing utilities."""
from typing import Any, Dict
import logging
from escpos.printer import file

logger = logging.getLogger(__name__)

'''
def format_receipt(p: Any, order: Dict[str, Any]) -> int:
    try:
        # Header
        p.set(align="center", bold=True, width=2, height=2)
        p.text(f"{order.get('company_name', '')}\n")
        p.set(align="center", bold=True)
        p.text("*** 주문 영수증 ***\n\n")

        # Order info
        p.set(align="left")
        p.text(f"주문번호: {order.get('order_id', '')}\n")
        p.text(f"주문일시: {order.get('created_at', '')}\n")
        p.text(
            f"주문유형: {'매장 식사' if order.get('is_dine_in', True) else '포장'}\n\n"
        )

        # Separator
        p.text("-" * 32 + "\n")

        # Items
        p.set(align="left")
        total = 0
        for item in order.get("items", []):
            name = item.get("name")
            qty = item.get("quantity", 0)
            price = item.get("price", 0)
            item_total = qty * price
            total += item_total

            p.text(f"{name}\n")
            for opt in item.get("options", []):
                p.text(f"- {opt['name']}")
                if opt.get("price", 0) > 0:
                    p.text(f" (+{opt['price']:,}원)")
                p.text("\n")

            p.text(
                f"수량: {qty}개 x {price:,}원 = {item_total:,}원\n\n"
            )

        # Separator
        p.text("-" * 32 + "\n")

        # Totals
        p.set(align="left")
        p.text(f"소계: {total:,}원\n")
        tax = int(total * 0.1)
        p.text(f"부가세: {tax:,}원\n")
        p.set(bold=True)
        p.text(f"총 금액: {total:,}원\n\n")

        # Footer
        p.set(align="center")
        p.text("감사합니다!\n")

        from datetime import datetime
        current_time = datetime.now()
        p.set(font='a', width=1, height=1)
        p.text(f"출력시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Cut
        p.cut()

        return total
    except Exception:
        logger.exception("영수증 포맷팅 중 오류 발생")
        raise
'''

def format_receipt_string(order: Dict[str, Any]) -> str:
    lines = []

    # Header
    lines.append(f"{order.get('company_name', '')}")
    lines.append("*** 주문 영수증 ***\n")

    # Order info
    lines.append(f"주문번호: {order.get('order_id', '')}")
    lines.append(f"주문일시: {order.get('created_at', '')}")
    lines.append(f"주문유형: {'매장 식사' if order.get('is_dine_in', True) else '포장'}\n")

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
    lines.append(f"부가세: {tax:,}원")
    lines.append(f"총 금액: {total:,}원\n")
    lines.append("감사합니다!\n")

    from datetime import datetime
    current_time = datetime.now()
    lines.append(f"출력시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    return "\n".join(lines)

