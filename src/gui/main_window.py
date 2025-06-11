from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from .order_widget import OrderWidget
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
        """) 