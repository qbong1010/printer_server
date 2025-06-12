"""ESC/POS 프린터 출력 유틸리티."""

from escpos.printer import Usb, Network
import os


def _get_printer():
    """환경변수에 지정된 설정을 바탕으로 프린터 인스턴스를 반환한다."""
    conn_type = os.getenv("POS_PRINTER_TYPE", "usb")
    address = os.getenv("POS_PRINTER_ADDRESS", "")
    if conn_type == "network" and address:
        return Network(address)

    vendor_id = 0x1504
    product_id = 0x0006
    interface = 0
    if address:
        try:
            parts = address.split(":")
            if len(parts) >= 2:
                vendor_id = int(parts[0], 16)
                product_id = int(parts[1], 16)
                if len(parts) >= 3:
                    interface = int(parts[2])
        except ValueError:
            pass
    return Usb(vendor_id, product_id, interface)


def print_receipt(order):
    """주문 정보를 받아 ESC/POS 프린터로 영수증을 출력한다."""
    printer = _get_printer()
    p = printer

    p.set(align="center", bold=True, width=2, height=2)
    p.text(f"픽업번호 : {order['pickup_number']}\n")

    p.set(align="center")
    p.text("-" * 32 + "\n")

    p.set(align="left", bold=False)
    p.text(f"유형 : {order['order_type']}\n")
    p.text(f"주문접수시간 : {order['timestamp']}\n")

    p.text("-" * 32 + "\n")
    p.text("메뉴           수량   금액\n")

    total = 0
    for item in order["items"]:
        name = item["name"]
        qty = item["quantity"]
        price = item["price"]
        total += qty * price

        p.text(f"{name:<14} {qty:<3} {price:>6,}\n")
        if "note" in item:
            p.text(f"{item['note']}\n")

    p.text("-" * 32 + "\n")
    p.set(align="right", bold=True)
    p.text(f"합계      {total:,.0f}\n")
    p.set(align="left", bold=False)
    p.text("-" * 32 + "\n")

    if 'disposable_needed' in order:
        p.text(f"일회용수저필요 : {order['disposable_needed']}\n")
    p.cut()

    p.text("----------------------------\n")
    p.text(f"총 합계: {total:,}원\n")
    p.text("\n감사합니다!\n")
    p.cut()

