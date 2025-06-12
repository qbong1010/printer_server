import os
import win32print

from .escpos_printer import print_receipt as escpos_print_receipt


class PrinterManager:
    def __init__(self):
        self.printer_name = os.getenv("DEFAULT_PRINTER_NAME") or win32print.GetDefaultPrinter()
        self.printer_type = os.getenv("PRINTER_TYPE", "default")

    def print_receipt(self, order_data):
        """주문 데이터를 기반으로 영수증 출력"""
        if self.printer_type == "escpos":
            try:
                escpos_print_receipt(order_data)
                return True
            except Exception as e:
                print(f"ESC/POS 프린터 오류: {e}")
                return False

        try:
            handle = win32print.OpenPrinter(self.printer_name)
            try:
                content = self._generate_receipt_content(order_data)
                job = win32print.StartDocPrinter(handle, 1, ("Receipt", None, "RAW"))
                try:
                    win32print.StartPagePrinter(handle)
                    win32print.WritePrinter(handle, content.encode("utf-8"))
                    win32print.EndPagePrinter(handle)
                finally:
                    win32print.EndDocPrinter(handle)
            finally:
                win32print.ClosePrinter(handle)
            return True
        except Exception as e:
            print(f"프린터 오류: {e}")
            return False

    @staticmethod
    def list_printers():
        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        return [p[2] for p in win32print.EnumPrinters(flags)]

    @staticmethod
    def get_default_printer():
        return win32print.GetDefaultPrinter()

    def set_printer(self, name):
        self.printer_name = name
        os.environ["DEFAULT_PRINTER_NAME"] = name

    def _generate_receipt_content(self, order_data):
        lines = [
            "=" * 40,
            "주문 영수증",
            "=" * 40,
            f"주문번호: {order_data['order_id']}",
            f"고객명: {order_data['customer_name']}",
            "-" * 40,
            "주문 내역:",
            "-" * 40,
        ]

        total = 0
        for item in order_data['items']:
            amount = item['price'] * item['quantity']
            total += amount
            lines.append(f"{item['name']} x {item['quantity']}")
            lines.append(f"  가격: {item['price']:,}원 x {item['quantity']} = {amount:,}원")
            if item.get('options'):
                for option in item['options']:
                    lines.append(f"  - {option}")

        lines.extend([
            "-" * 40,
            f"총 금액: {total:,}원",
            f"결제 방법: {order_data['payment_method']}",
            "=" * 40,
            "\n" * 5,
        ])

        return "\n".join(lines)
