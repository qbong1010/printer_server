from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QMessageBox,
    QProgressBar,
)
from PySide6.QtCore import Qt, Slot, QTimer
import logging
import sqlite3
import requests

# Use an absolute import so this module works when executed directly.
from src.database.cache import SupabaseCache

from src.printer.manager import PrinterManager

class OrderWidget(QWidget):
    def __init__(self, supabase_config, db_config):
        super().__init__()
        self.printer_manager = PrinterManager()
        self.cache = SupabaseCache(db_path=db_config['path'], supabase_config=supabase_config)
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
        title_label = QLabel("식권 주문 현황")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_layout.addWidget(title_label)
        
        self.refresh_btn = QPushButton("새로고침")
        self.refresh_btn.clicked.connect(self.refresh_orders)
        top_layout.addWidget(self.refresh_btn)

        self.sync_btn = QPushButton("데이터 동기화")
        self.sync_btn.clicked.connect(self.sync_static_tables)
        top_layout.addWidget(self.sync_btn)

        self.print_btn = QPushButton("영수증 출력")
        self.print_btn.clicked.connect(self.print_receipt)
        top_layout.addWidget(self.print_btn, alignment=Qt.AlignRight)
        
        layout.addLayout(top_layout)
        
        # 진행 상태 표시 바
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 주문 테이블
        self.order_table = QTableWidget()
        self.order_table.setColumnCount(7)
        self.order_table.setHorizontalHeaderLabels([
            "주문번호", "회사명", "메뉴", "매장식사", "총액", "상태", "주문일시"
        ])
        self.order_table.horizontalHeader().setStretchLastSection(True)
        self.order_table.setEditTriggers(QTableWidget.NoEditTriggers)  # 편집 비활성화
        self.order_table.setSelectionBehavior(QTableWidget.SelectRows)  # 행 전체 선택
        self.order_table.setSelectionMode(QTableWidget.SingleSelection)  # 단일 행 선택만 허용
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
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
    
    def set_loading_state(self, is_loading):
        """로딩 상태에 따라 UI 요소들을 업데이트합니다."""
        self.refresh_btn.setEnabled(not is_loading)
        self.sync_btn.setEnabled(not is_loading)
        self.print_btn.setEnabled(not is_loading)
        self.progress_bar.setVisible(is_loading)
        if is_loading:
            self.progress_bar.setRange(0, 0)  # 무한 로딩 표시
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
    
    @Slot()
    def refresh_orders(self):
        """주문 목록을 새로고침합니다."""
        try:
            self.set_loading_state(True)
            
            # 주문 관련 테이블 동기화
            for table in ["order", "order_item", "order_item_option"]:
                self.cache.fetch_and_store_table(table)

            orders = self.cache.get_recent_orders()

            # 테이블 초기화
            self.order_table.setRowCount(0)
            self.orders = []

            # 새로운 주문 데이터 추가 (최근 주문부터)
            for order in orders:
                detail = self.cache.join_order_detail(order["order_id"])
                self.add_order(detail)

            self.notice_label.setText("주문 목록이 갱신되었습니다.")

        except Exception as e:
            QMessageBox.warning(self, "오류", f"주문 목록 갱신 중 오류가 발생했습니다: {str(e)}")
        finally:
            self.set_loading_state(False)
    
    @Slot()
    def print_receipt(self):
        # 선택된 주문의 영수증 출력
        current_row = self.order_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "경고", "출력할 주문을 선택해주세요.")
            return
            
        order_item = self.order_table.item(current_row, 0)
        if not order_item:
            QMessageBox.warning(self, "경고", "선택한 주문 데이터를 찾을 수 없습니다.")
            return
            
        order_data = order_item.data(Qt.UserRole)
        if not order_data:
            QMessageBox.warning(self, "경고", "선택한 주문 데이터가 유효하지 않습니다.")
            return
            
        try:
            # 주문 데이터 형식 변환
            formatted_order = {
                "order_id": str(order_data.get("order_id", "N/A")),
                "company_name": order_data.get("company_name", "N/A"),
                "created_at": order_data.get("created_at", ""),
                "is_dine_in": order_data.get("is_dine_in", True),
                "items": []
            }
            
            # 주문 항목 처리
            for item in order_data.get("items", []):
                formatted_item = {
                    "name": item.get("name", "N/A"),
                    "quantity": item.get("quantity", 1),
                    "price": item.get("price", 0),
                    "options": item.get("options", [])
                }
                formatted_order["items"].append(formatted_item)
            
            # 프린터 출력 시도
            success = self.printer_manager.print_receipt(formatted_order)
            if success:
                # 실제로 출력이 되었는지 사용자에게 확인
                reply = QMessageBox.question(
                    self,
                    "출력 확인",
                    "영수증이 정상적으로 출력되었습니까?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    # 로컬 DB에 출력 상태 업데이트
                    with sqlite3.connect(self.cache.db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            'UPDATE "order" SET is_printed = 1 WHERE order_id = ?',
                            (order_data["order_id"],)
                        )
                        conn.commit()
                    
                    # Supabase에도 출력 상태 업데이트
                    if self.cache.base_url:
                        try:
                            response = requests.patch(
                                f"{self.cache.base_url}/rest/v1/order",
                                headers=self.cache.headers,
                                json={"is_printed": True},
                                params={"order_id": f"eq.{order_data['order_id']}"}
                            )
                            response.raise_for_status()
                        except Exception as e:
                            logging.error(f"Supabase 업데이트 실패: {e}")
                    
                    # UI 업데이트
                    self.order_table.setItem(current_row, 5, QTableWidgetItem("출력완료"))
                    QMessageBox.information(self, "성공", "영수증이 성공적으로 출력되었습니다.")
                else:
                    QMessageBox.warning(self, "출력 실패", "프린터 출력을 확인해주세요.")
            else:
                QMessageBox.warning(self, "출력 실패", "영수증 출력 중 오류가 발생했습니다.")
        except Exception as e:
            QMessageBox.warning(self, "오류", f"영수증 출력 중 예외가 발생했습니다: {str(e)}")

    def add_order(self, order_data):
        """새로운 주문을 테이블에 추가"""
        try:
            row_position = self.order_table.rowCount()
            self.order_table.insertRow(row_position)

            # 주문 데이터 설정
            order_id = str(order_data.get("order_id", "N/A"))
            item_id = QTableWidgetItem(order_id)
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
            
            # 주문일시
            created_at = order_data.get("created_at", "")
            if created_at:
                # ISO 형식의 날짜를 한국 시간으로 변환하여 표시
                from datetime import datetime
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    created_at = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
            self.order_table.setItem(row_position, 6, QTableWidgetItem(created_at))
            
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
            self.set_loading_state(True)
            
            changes = []
            for table in tables:
                old_data = self.cache.get_table_data(table)
                self.cache.fetch_and_store_table(table)
                new_data = self.cache.get_table_data(table)
                
                # 변경사항 확인
                if old_data != new_data:
                    changes.append(f"{table}: {len(new_data) - len(old_data)}개 항목 변경")
            
            if changes:
                QMessageBox.information(
                    self, 
                    "동기화 완료", 
                    "고정 데이터 동기화가 완료되었습니다.\n\n변경사항:\n" + "\n".join(changes)
                )
            else:
                QMessageBox.information(self, "동기화 완료", "모든 데이터가 최신 상태입니다.")
                
        except Exception as e:
            QMessageBox.warning(self, "오류", f"동기화 중 오류가 발생했습니다: {str(e)}")
        finally:
            self.set_loading_state(False)

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
