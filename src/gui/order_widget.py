from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QMessageBox,
)
from PySide6.QtCore import Qt, Slot, QTimer
import logging

from ..database.cache import SupabaseCache

from ..printer.manager import PrinterManager

class OrderWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.printer_manager = PrinterManager()
        self.cache = SupabaseCache()
        self.cache.setup_sqlite()
        self.setup_ui()
        self.orders = []

        # 주문 갱신을 위한 단일 타이머
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.check_for_updates)
        self.update_timer.start(5000)

        # 초기 주문 로드
        self.refresh_orders()
        
    def setup_ui(self):
        # 메인 레이아웃
        layout = QVBoxLayout(self)
        
        # 상단 레이아웃 (제목 + 버튼)
        top_layout = QHBoxLayout()
        title_label = QLabel("실시간 주문 현황")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_layout.addWidget(title_label)
        
        refresh_btn = QPushButton("새로고침")
        refresh_btn.clicked.connect(self.refresh_orders)
        top_layout.addWidget(refresh_btn)

        sync_btn = QPushButton("데이터 동기화")
        sync_btn.clicked.connect(self.sync_static_tables)
        top_layout.addWidget(sync_btn)

        print_btn = QPushButton("영수증 출력")
        print_btn.clicked.connect(self.print_receipt)
        top_layout.addWidget(print_btn, alignment=Qt.AlignRight)
        
        layout.addLayout(top_layout)
        
        # 주문 테이블
        self.order_table = QTableWidget()
        self.order_table.setColumnCount(6)
        self.order_table.setHorizontalHeaderLabels([
            "주문번호", "회사명", "메뉴", "매장식사", "총액", "상태"
        ])
        self.order_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.order_table)

        # 알림 레이블
        self.notice_label = QLabel("")
        layout.addWidget(self.notice_label)
        
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
    def refresh_orders(self):
        """주문 목록을 새로고침합니다."""
        try:
            # 주문 관련 테이블 동기화
            for table in ["order", "order_item", "order_item_option"]:
                self.cache.fetch_and_store_table(table)

            orders = self.cache.get_recent_orders()

            # 테이블 초기화
            self.order_table.setRowCount(0)
            self.orders = []

            # 새로운 주문 데이터 추가
            for order in orders:
                detail = self.cache.join_order_detail(order["order_id"])
                self.add_order(detail)

            self.notice_label.setText("")

        except Exception as e:
            QMessageBox.warning(self, "오류", f"주문 목록 갱신 중 오류가 발생했습니다: {str(e)}")
    
    @Slot()
    def print_receipt(self):
        # 선택된 주문의 영수증 출력
        current_row = self.order_table.currentRow()
        if current_row >= 0:
            order_item = self.order_table.item(current_row, 0)
            order_data = order_item.data(Qt.UserRole)
            if order_data:
                success = self.printer_manager.print_receipt(order_data)
                if not success:
                    QMessageBox.warning(self, "출력 실패", "영수증 출력 중 오류가 발생했습니다.")
    
    def add_order(self, order_data):
        """새로운 주문을 테이블에 추가"""
        try:
            row_position = self.order_table.rowCount()
            self.order_table.insertRow(row_position)

            # 주문 데이터 설정
            item_id = QTableWidgetItem(order_data.get("order_id", "N/A"))
            item_id.setData(Qt.UserRole, order_data)
            self.order_table.setItem(row_position, 0, item_id)
            
            # 회사명
            company_name = order_data.get("company_name", "N/A")
            self.order_table.setItem(row_position, 1, QTableWidgetItem(company_name))
            
            # 메뉴 항목 구성
            items = order_data.get("items", [])
            items_text = "\n".join([
                f"{item.get('name', 'N/A')} x{item.get('quantity', 1)}"
                for item in items
            ])
            self.order_table.setItem(row_position, 2, QTableWidgetItem(items_text))
            
            # 매장식사 여부
            is_dine_in = "매장식사" if order_data.get("is_dine_in", True) else "포장"
            self.order_table.setItem(row_position, 3, QTableWidgetItem(is_dine_in))
            
            # 총액
            total_price = f"{order_data.get('total_price', 0):,}원"
            self.order_table.setItem(row_position, 4, QTableWidgetItem(total_price))
            
            # 상태
            status = "출력완료" if order_data.get("is_printed", False) else "신규"
            self.order_table.setItem(row_position, 5, QTableWidgetItem(status))
            
            self.orders.append(order_data)
        except Exception as e:
            QMessageBox.warning(self, "오류", f"주문 추가 중 오류가 발생했습니다: {str(e)}")

    @Slot()
    def sync_static_tables(self):
        """고정 테이블을 수동 동기화합니다."""
        tables = [
            "company",
            "menu_category",
            "menu_item",
            "menu_item_option_group",
            "option_group",
            "option_group_item",
            "option_item",
        ]
        try:
            for table in tables:
                self.cache.fetch_and_store_table(table)
            QMessageBox.information(self, "동기화", "고정 데이터 동기화가 완료되었습니다.")
        except Exception as e:
            QMessageBox.warning(self, "오류", f"동기화 중 오류가 발생했습니다: {str(e)}")

    def check_for_updates(self):
        """새 주문을 확인하고 필요한 경우 목록을 갱신"""
        try:
            if self.cache.poll_new_orders():
                self.notice_label.setText("새 주문이 있습니다. 새로고침해주세요.")
                self.refresh_orders()
            else:
                self.notice_label.setText("")
        except Exception as e:
            logging.error(f"Error while polling new orders: {e}")
            self.notice_label.setText("주문 확인 중 오류가 발생했습니다.")
            pass