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
    QCheckBox,
)
from PySide6.QtCore import Qt, Slot, QTimer
import logging
import sqlite3
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Use an absolute import so this module works when executed directly.
from src.database.cache import SupabaseCache

from src.printer.manager import PrinterManager

# 주문 상태 Enum
class OrderStatus:
    NEW = "신규"
    PRINTING = "출력중"
    PRINTED = "출력완료"
    PRINT_FAILED = "출력실패"

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
        
        # 자동 출력 체크박스 추가
        self.auto_print_checkbox = QCheckBox("자동 출력")
        
        # 초기 상태 설정 및 로깅
        initial_auto_print_state = self.printer_manager.is_auto_print_enabled()
        logging.info(f"GUI 초기화: 자동 출력 설정 상태 = {initial_auto_print_state}")
        
        self.auto_print_checkbox.setChecked(initial_auto_print_state)
        self.auto_print_checkbox.stateChanged.connect(self.toggle_auto_print)
        top_layout.addWidget(self.auto_print_checkbox)
        
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
        self.order_table.setColumnCount(8)
        self.order_table.setHorizontalHeaderLabels([
            "주문번호", "회사명", "메뉴", "매장식사", "총액", "상태", "출력상태", "주문일시"
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
            QCheckBox {
                font-weight: bold;
                color: #2E7D32;
            }
        """)
    
    @Slot()
    def toggle_auto_print(self, state):
        """자동 출력 기능을 토글합니다."""
        enabled = state == Qt.Checked
        logging.info(f"자동 출력 체크박스 상태 변경: {enabled}")
        
        # 현재 설정 가져오기
        config = self.printer_manager.get_auto_print_config()
        logging.info(f"변경 전 설정: {config}")
        
        # 설정 업데이트
        config["enabled"] = enabled
        self.printer_manager.set_auto_print_config(config)
        
        # 설정 저장 후 다시 확인
        updated_config = self.printer_manager.get_auto_print_config()
        logging.info(f"변경 후 설정: {updated_config}")
        
        status = "활성화" if enabled else "비활성화"
        self.notice_label.setText(f"자동 출력이 {status}되었습니다.")
        logging.info(f"자동 출력 {status} 완료")
    
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
    
    def update_order_status(self, order_id: int, status: str, print_attempts: int = None):
        """주문 상태를 업데이트합니다."""
        try:
            with sqlite3.connect(self.cache.db_path) as conn:
                cursor = conn.cursor()
                
                # 현재 시간
                now = datetime.now().isoformat()
                
                if print_attempts is not None:
                    cursor.execute(
                        'UPDATE "order" SET print_status = ?, print_attempts = ?, last_print_attempt = ? WHERE order_id = ?',
                        (status, print_attempts, now, order_id)
                    )
                else:
                    cursor.execute(
                        'UPDATE "order" SET print_status = ?, last_print_attempt = ? WHERE order_id = ?',
                        (status, now, order_id)
                    )
                
                conn.commit()
                logging.info(f"주문 {order_id}의 상태를 {status}로 업데이트")
                
                # Supabase에도 상태 업데이트 시도
                if self.cache.base_url and status == OrderStatus.PRINTED:
                    try:
                        response = requests.patch(
                            f"{self.cache.base_url}/rest/v1/order",
                            headers=self.cache.headers,
                            json={"is_printed": True},
                            params={"order_id": f"eq.{order_id}"}
                        )
                        response.raise_for_status()
                    except Exception as e:
                        logging.error(f"Supabase 업데이트 실패: {e}")
                        
        except Exception as e:
            logging.error(f"주문 상태 업데이트 오류: {e}")

    def check_for_updates(self):
        """미출력 주문을 확인하고 자동 출력을 처리합니다."""
        try:
            # 자동 출력이 비활성화된 경우 처리하지 않음
            if not self.printer_manager.is_auto_print_enabled():
                return
                
            # 주문 관련 테이블 동기화 (항상 수행)
            for table in ["order", "order_item", "order_item_option"]:
                self.cache.fetch_and_store_table(table)
            
            # 미출력 주문들 가져오기
            unprinteed_orders = self.get_unprinteed_orders()
            
            if unprinteed_orders:
                logging.info(f"미출력 주문 {len(unprinteed_orders)}개를 확인했습니다.")
                self.notice_label.setText(f"미출력 주문 {len(unprinteed_orders)}개 발견")
                
                # 각 미출력 주문에 대해 자동 출력 처리
                for order in unprinteed_orders:
                    order_detail = self.cache.join_order_detail(order["order_id"])
                    order_id = order_detail.get("order_id")
                    
                    logging.info(f"주문 {order_id} 자동 출력 시도")
                    
                    # 프린터 상태 확인
                    if not self.printer_manager.check_printer_status():
                        logging.warning(f"주문 {order_id}: 프린터 상태 불량으로 출력 건너뜀")
                        continue
                    
                    # 자동 출력 처리
                    success = self.process_auto_print(order_detail)
                    
                    if success:
                        logging.info(f"주문 {order_id} 자동 출력 성공")
                        # 출력 성공 시 is_printed 상태 업데이트
                        self.update_is_printed_status(order_id, True)
                    else:
                        logging.warning(f"주문 {order_id} 자동 출력 실패")
                
                # UI 새로고침
                self.refresh_orders()
            else:
                # 미출력 주문이 없으면 조용히 처리
                pass
                
        except Exception as e:
            logging.error(f"자동 출력 처리 오류: {e}")
            self.notice_label.setText("자동 출력 처리 중 오류가 발생했습니다.")

    def get_unprinteed_orders(self) -> List[Dict[str, Any]]:
        """출력되지 않은 주문들을 가져옵니다."""
        conn = sqlite3.connect(self.cache.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # is_printed가 0(False)인 주문들을 최신순으로 가져오기
        query = """
        SELECT o.order_id, o.company_id, o.is_dine_in, o.total_price, o.created_at,
               c.company_name
        FROM "order" o
        JOIN company c ON c.company_id = o.company_id
        WHERE o.is_printed = 0
        ORDER BY o.created_at DESC
        LIMIT 10
        """
        
        rows = cursor.execute(query).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_is_printed_status(self, order_id: int, is_printed: bool) -> None:
        """주문의 출력 상태를 업데이트합니다."""
        try:
            # 로컬 DB 업데이트
            with sqlite3.connect(self.cache.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE "order" SET is_printed = ? WHERE order_id = ?',
                    (1 if is_printed else 0, order_id)
                )
                conn.commit()
                logging.info(f"주문 {order_id}의 출력 상태를 {is_printed}로 업데이트")
            
            # Supabase에도 업데이트 시도
            if self.cache.base_url:
                try:
                    response = requests.patch(
                        f"{self.cache.base_url}/rest/v1/order",
                        headers=self.cache.headers,
                        json={"is_printed": is_printed},
                        params={"order_id": f"eq.{order_id}"}
                    )
                    response.raise_for_status()
                    logging.info(f"Supabase에 주문 {order_id} 출력 상태 업데이트 성공")
                except Exception as e:
                    logging.error(f"Supabase 출력 상태 업데이트 실패: {e}")
                        
        except Exception as e:
            logging.error(f"출력 상태 업데이트 오류: {e}")

    def process_auto_print(self, order_data: dict) -> bool:
        """자동 출력을 처리합니다."""
        order_id = order_data.get("order_id")
        
        try:
            # 이미 출력된 주문인지 확인
            if order_data.get("is_printed", False):
                logging.info(f"주문 {order_id}: 이미 출력됨")
                return True
                
            # 출력 상태를 "출력중"으로 변경 (print_status는 별도 관리)
            self.update_order_status(order_id, OrderStatus.PRINTING)
            
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
                # 출력 성공
                self.update_order_status(order_id, OrderStatus.PRINTED)
                logging.info(f"주문 {order_id} 자동 출력 성공")
                self.notice_label.setText(f"주문 {order_id}이(가) 자동으로 출력되었습니다.")
                return True
            else:
                # 출력 실패
                self.update_order_status(order_id, OrderStatus.PRINT_FAILED)
                logging.error(f"주문 {order_id} 자동 출력 실패")
                return False
                
        except Exception as e:
            logging.error(f"자동 출력 처리 오류: {e}")
            self.update_order_status(order_id, OrderStatus.PRINT_FAILED)
            return False

    def should_retry_print(self, order_data: dict) -> bool:
        """재시도가 필요한지 확인합니다."""
        if order_data.get("print_status") != OrderStatus.NEW:
            return False
            
        last_attempt = order_data.get("last_print_attempt")
        if not last_attempt:
            return True
            
        try:
            last_attempt_time = datetime.fromisoformat(last_attempt)
            retry_interval = self.printer_manager.auto_print_config.get("retry_interval", 30)
            return datetime.now() >= last_attempt_time + timedelta(seconds=retry_interval)
        except Exception:
            return True
    
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
                    # 상태 업데이트
                    self.update_order_status(order_data["order_id"], OrderStatus.PRINTED)
                    # is_printed 상태도 업데이트
                    self.update_is_printed_status(order_data["order_id"], True)
                    
                    # UI 업데이트
                    self.order_table.setItem(current_row, 5, QTableWidgetItem("출력완료"))
                    self.order_table.setItem(current_row, 6, QTableWidgetItem(OrderStatus.PRINTED))
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
            
            # 상태 (기존 is_printed 기반)
            status = "출력완료" if order_data.get("is_printed", False) else "신규"
            self.order_table.setItem(row_position, 5, QTableWidgetItem(status))
            
            # 출력상태 (새로운 print_status 기반)
            print_status = order_data.get("print_status", OrderStatus.NEW)
            self.order_table.setItem(row_position, 6, QTableWidgetItem(print_status))
            
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
            self.order_table.setItem(row_position, 7, QTableWidgetItem(created_at))
            
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
