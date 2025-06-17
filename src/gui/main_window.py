from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QTextEdit, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from .order_widget import OrderWidget
from .printer_widget import PrinterWidget
from src.supabase_client import SupabaseClient
from src.printer.receipt_preview import read_receipt_file

class ReceiptPreviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # 미리보기 텍스트 영역
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Courier New", 10))  # 고정폭 폰트 사용
        
        # 새로고침 버튼
        refresh_btn = QPushButton("새로고침")
        refresh_btn.clicked.connect(self.refresh_preview)
        
        layout.addWidget(refresh_btn)
        layout.addWidget(self.preview_text)
        
        # 초기 미리보기 로드
        self.refresh_preview()
        
    def refresh_preview(self):
        preview_text = read_receipt_file()
        if preview_text:
            self.preview_text.setText(preview_text)
        else:
            self.preview_text.setText("영수증 미리보기를 불러올 수 없습니다.")

class MainWindow(QMainWindow):
    def __init__(self, supabase_config, db_config):
        super().__init__()
        self.setWindowTitle("주문 관리 시스템")
        self.setMinimumSize(800, 600)
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃 설정
        layout = QVBoxLayout(central_widget)
        
        # 탭 위젯 생성
        tab_widget = QTabWidget()
        
        # 주문 관리 탭
        self.order_widget = OrderWidget(supabase_config, db_config)
        tab_widget.addTab(self.order_widget, "주문 관리")
        
        # 프린터 설정 탭
        self.printer_widget = PrinterWidget()
        tab_widget.addTab(self.printer_widget, "프린터 설정")
        
        # 영수증 미리보기 탭
        self.receipt_preview = ReceiptPreviewWidget()
        tab_widget.addTab(self.receipt_preview, "영수증 미리보기")
        
        layout.addWidget(tab_widget)

        # SupabaseClient 연결
        self.supabase_client = SupabaseClient()
        
        # 윈도우 설정
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: white;
            }
            QTabBar::tab {
                background: #e1e1e1;
                border: 1px solid #cccccc;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
            }
            QTabBar::tab:hover {
                background: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:pressed {
                background-color: #2a5f96;
            }
        """) 