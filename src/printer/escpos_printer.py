from escpos.printer import Usb
from escpos.printer import Network
from escpos.printer import Usb
import datetime


#--------------------------------USB 프린터
VENDOR_ID = 0x1504  # 예시: Sewoo
PRODUCT_ID = 0x0006
INTERFACE = 0  # 기본 0

printer = Usb(VENDOR_ID, PRODUCT_ID, INTERFACE)


#--------------------------------네트워크 프린터
printer = Network("192.168.0.123")  # 프린터 IP 주소


# 프린터 연결
# 정의되어야하는 json 인자(order)
# 예시
# {
#     "pickup_number": "1234567890",
#     "order_type": "픽업",
#     "timestamp": "2025-01-01 12:00:00",
#     "items": [{"name": "메뉴1", "quantity": 1, "price": 10000}, {"name": "메뉴2", "quantity": 2, "price": 20000}]
def print_receipt(order):
    p = printer
    p.set(align='center', bold=True, width=2, height=2)
    p.text(f"픽업번호 : {order['pickup_number']}\n")
    
    p.set(align='center')
    p.text("-" * 32 + "\n")

    p.set(align='left', bold=False)
    p.text(f"유형 : {order['order_type']}\n")
    p.text(f"주문접수시간 : {order['timestamp']}\n")

    p.text("-" * 32 + "\n")
    p.text("메뉴           수량   금액\n")

    total = 0
    for item in order['items']:
        name = item['name']
        qty = item['quantity']
        price = item['price']
        total += qty * price

        # 첫 줄 (메인 메뉴 또는 옵션)
        p.text(f"{name:<14} {qty:<3} {price:>6,}\n")

        # 추가 설명이 있는 경우
        if 'note' in item:
            p.text(f"{item['note']}\n")

    p.text("-" * 32 + "\n")
    p.set(align='right', bold=True)
    p.text(f"합계      {total:,.0f}\n")
    p.set(align='left', bold=False)
    p.text("-" * 32 + "\n")

    p.text(f"일회용수저필요 : {order['disposable_needed']}\n")
    p.cut()

    p.text("----------------------------\n")
    p.text(f"총 합계: {total:,}원\n")
    p.text("\n감사합니다!\n")
    p.cut()
