from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget
from PySide6.QtCore import Qt
from .order_widget import OrderWidget
from .printer_widget import PrinterWidget
from src.supabase_client import SupabaseClient

class MainWindow(QMainWindow):
    def __init__(self):
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
        self.order_widget = OrderWidget()
        tab_widget.addTab(self.order_widget, "주문 관리")
        
        # 프린터 설정 탭
        self.printer_widget = PrinterWidget()
        tab_widget.addTab(self.printer_widget, "프린터 설정")
        
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