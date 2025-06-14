import os
import win32print
import json
from pathlib import Path

from .escpos_printer import print_receipt as escpos_print_receipt


class PrinterManager:
    def __init__(self):
        self.config_file = Path("printer_config.json")
        self.load_config()

    def load_config(self):
        """프린터 설정을 로드합니다."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.printer_name = config.get("printer_name")
                    self.printer_type = config.get("printer_type", "default")
            else:
                self.printer_name = win32print.GetDefaultPrinter()
                self.printer_type = "default"
        except Exception as e:
            print(f"설정 로드 오류: {e}")
            self.printer_name = win32print.GetDefaultPrinter()
            self.printer_type = "default"

    def save_config(self):
        """프린터 설정을 저장합니다."""
        try:
            config = {
                "printer_name": self.printer_name,
                "printer_type": self.printer_type
            }
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"설정 저장 오류: {e}")

    def get_current_printer(self):
        """현재 선택된 프린터 이름을 반환합니다."""
        return self.printer_name

    def get_printer_type(self):
        """현재 프린터 타입을 반환합니다."""
        return self.printer_type

    def set_printer(self, name):
        """프린터를 설정합니다."""
        self.printer_name = name
        self.save_config()

    def set_printer_type(self, printer_type):
        """프린터 타입을 설정합니다."""
        if printer_type not in ["escpos", "default"]:
            raise ValueError("프린터 타입은 'escpos' 또는 'default'여야 합니다.")
        self.printer_type = printer_type
        self.save_config()

    def print_receipt(self, order_data):
        """주문 데이터를 기반으로 영수증 출력"""
        if self.printer_type == "escpos":
            try:
                escpos_print_receipt(order_data)
                return True
            except Exception as e:
                print(f"ESC/POS 프린터 오류: {e}")
                print("윈도우 기본 프린터로 출력을 시도합니다...")
                # ESC/POS 실패 시 윈도우 프린터로 폴백
                self.printer_type = "default"
                return self.print_receipt(order_data)

        try:
            handle = win32print.OpenPrinter(self.printer_name)
            try:
                content = self._generate_receipt_content(order_data)
                job = win32print.StartDocPrinter(handle, 1, ("Receipt", None, "RAW"))
                try:
                    win32print.StartPagePrinter(handle)
                    encoded_content = content.encode("cp949", errors="replace")
                    win32print.WritePrinter(handle, encoded_content)
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
        """사용 가능한 프린터 목록을 반환합니다."""
        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        return [p[2] for p in win32print.EnumPrinters(flags)]

    @staticmethod
    def get_default_printer():
        """기본 프린터 이름을 반환합니다."""
        return win32print.GetDefaultPrinter()

    def _generate_receipt_content(self, order_data):
        """영수증 내용을 생성합니다."""
        lines = [
            "=" * 40,
            "주문 영수증",
            "=" * 40,
            f"주문번호: {order_data['order_id']}",
            f"회사명: {order_data['company_name']}",
            f"주문시간: {order_data['created_at']}",
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
                    lines.append(f"  - {option['name']}: {option['price']:,}원")

        lines.extend([
            "-" * 40,
            f"총 금액: {total:,}원",
            f"매장식사: {'예' if order_data['is_dine_in'] else '아니오'}",
            "=" * 40,
            "\n" * 5,
            "\x1B\x69",  # ESC i - 자동 절단 명령어
            "\x1D\x56\x41",  # GS V A - 전체 절단 명령어
        ])

        return "\n".join(lines)
