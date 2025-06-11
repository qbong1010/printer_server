import win32print
import win32con
import os

class PrinterManager:
    def __init__(self):
        self.printer_name = os.getenv('DEFAULT_PRINTER_NAME')
        if not self.printer_name:
            # 기본 프린터 가져오기
            self.printer_name = win32print.GetDefaultPrinter()
    
    def print_receipt(self, order_data):
        """주문 데이터를 기반으로 영수증 출력"""
        try:
            # 프린터 핸들 얻기
            printer_handle = win32print.OpenPrinter(self.printer_name)
            try:
                # 영수증 내용 생성
                receipt_content = self._generate_receipt_content(order_data)
                
                # 인쇄 작업 시작
                job = win32print.StartDocPrinter(printer_handle, 1, ("Receipt", None, "RAW"))
                try:
                    win32print.StartPagePrinter(printer_handle)
                    win32print.WritePrinter(printer_handle, receipt_content.encode('utf-8'))
                    win32print.EndPagePrinter(printer_handle)
                finally:
                    win32print.EndDocPrinter(printer_handle)
            finally:
                win32print.ClosePrinter(printer_handle)
            return True
        except Exception as e:
            print(f"프린터 오류: {e}")
            return False
    
    def _generate_receipt_content(self, order_data):
        """영수증 내용 생성"""
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
        
        # 주문 항목 추가
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
            "\n" * 5  # 여백 추가
        ])
        
        return "\n".join(lines) 