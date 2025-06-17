# -*- coding: utf-8 -*-
"""Common receipt printing utilities."""

from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


def format_receipt(p: Any, order: Dict[str, Any]) -> int:
    """Print receipt content using an ESC/POS compatible printer object.

    Parameters
    ----------
    p: Any
        Printer instance providing ``set`` and ``text`` methods.
    order: Dict[str, Any]
        Order information to render.

    Returns
    -------
    int
        Calculated total price of the order.
    """
    try:
        def encode_text(text: str) -> bytes:
            try:
                return text.encode("cp949")
            except UnicodeEncodeError as e:
                logger.error("CP949 인코딩 오류: %s", e)
                return text.encode("euc-kr", errors="replace")

        # Header
        p.set(align="center", bold=True, width=2, height=2)
        p.text(encode_text(f"{order.get('company_name', '')}\n"))
        p.set(align="center", bold=True)
        p.text(encode_text("*** 주문 영수증 ***\n\n"))

        # Order info
        p.set(align="left")
        p.text(encode_text(f"주문번호: {order.get('order_id', '')}\n"))
        p.text(encode_text(f"주문일시: {order.get('created_at', '')}\n"))
        p.text(encode_text(
            f"주문유형: {'매장 식사' if order.get('is_dine_in', True) else '포장'}\n\n"
        ))

        # Separator
        p.text(encode_text("-" * 32 + "\n"))

        # Items
        p.set(align="left")
        total = 0
        for item in order.get("items", []):
            name = item.get("name")
            qty = item.get("quantity", 0)
            price = item.get("price", 0)
            item_total = qty * price
            total += item_total

            p.text(encode_text(f"{name}\n"))
            for opt in item.get("options", []):
                p.text(encode_text(f"• {opt['name']}"))
                if opt.get("price", 0) > 0:
                    p.text(encode_text(f" (+{opt['price']:,}원)"))
                p.text(encode_text("\n"))

            p.text(encode_text(
                f"수량: {qty}개 x {price:,}원 = {item_total:,}원\n\n"
            ))

        # Separator
        p.text(encode_text("-" * 32 + "\n"))

        # Totals
        p.set(align="left")
        p.text(encode_text(f"소계: {total:,}원\n"))
        tax = int(total * 0.1)
        p.text(encode_text(f"부가세: {tax:,}원\n"))
        p.set(bold=True)
        p.text(encode_text(f"총 금액: {total:,}원\n\n"))

        # Footer
        p.set(align="center")
        p.text(encode_text("감사합니다!\n"))
        p.text(encode_text("맛있게 드세요~\n\n"))

        from datetime import datetime
        current_time = datetime.now()
        p.set(font='a', width=1, height=1)
        p.text(encode_text(f"출력시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"))

        # Cut
        p.cut()

        return total
    except Exception:
        logger.exception("영수증 포맷팅 중 오류 발생")
        raise
