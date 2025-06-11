from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QPushButton, QLabel)
from PySide6.QtCore import Qt, Slot

class OrderWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        # 메인 레이아웃
        layout = QVBoxLayout(self)
        
        # 상단 레이아웃 (제목 + 버튼)
        top_layout = QHBoxLayout()
        title_label = QLabel("실시간 주문 현황")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_layout.addWidget(title_label)
        
        print_btn = QPushButton("영수증 출력")
        print_btn.clicked.connect(self.print_receipt)
        top_layout.addWidget(print_btn, alignment=Qt.AlignRight)
        
        layout.addLayout(top_layout)
        
        # 주문 테이블
        self.order_table = QTableWidget()
        self.order_table.setColumnCount(5)
        self.order_table.setHorizontalHeaderLabels([
            "주문번호", "고객명", "메뉴", "결제방법", "상태"
        ])
        self.order_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.order_table)
        
        # 스타일 설정
        self.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
    
    @Slot()
    def print_receipt(self):
        # 선택된 주문의 영수증 출력
        current_row = self.order_table.currentRow()
        if current_row >= 0:
            # TODO: 프린터 관리자를 통해 영수증 출력
            pass
    
    def add_order(self, order_data):
        """새로운 주문을 테이블에 추가"""
        row_position = self.order_table.rowCount()
        self.order_table.insertRow(row_position)
        
        # 주문 데이터 설정
        self.order_table.setItem(row_position, 0, QTableWidgetItem(order_data["order_id"]))
        self.order_table.setItem(row_position, 1, QTableWidgetItem(order_data["customer_name"]))
        
        # 메뉴 항목 구성
        items_text = "\n".join([
            f"{item['name']} x{item['quantity']}"
            for item in order_data["items"]
        ])
        self.order_table.setItem(row_position, 2, QTableWidgetItem(items_text))
        
        self.order_table.setItem(row_position, 3, QTableWidgetItem(order_data["payment_method"]))
        self.order_table.setItem(row_position, 4, QTableWidgetItem("신규")) 