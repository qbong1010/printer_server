from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from .order_widget import OrderWidget
from .server_widget import ServerWidget
import asyncio
from ..websocket.client import WebSocketClient

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("주문 관리 시스템")
        self.setMinimumSize(800, 600)
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 레이아웃 설정
        layout = QVBoxLayout(central_widget)
        
        # 서버 상태 위젯 추가
        self.server_widget = ServerWidget()
        layout.addWidget(self.server_widget)
        
        # 주문 위젯 추가
        self.order_widget = OrderWidget()
        layout.addWidget(self.order_widget)

        # 💡 WebSocketClient 연결
        self.ws_client = WebSocketClient()
        self.ws_client.order_received.connect(self.order_widget.add_order)

        # 💡 WebSocket 실행 (비동기로 실행)
        import threading
        threading.Thread(target=lambda: asyncio.run(self.ws_client.connect()), daemon=True).start()
        
        # 윈도우 설정
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
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