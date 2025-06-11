import json
import asyncio
import websockets
import os
from PySide6.QtCore import QObject, Signal

class WebSocketClient(QObject):
    order_received = Signal(dict)  # 주문 수신 시그널
    
    def __init__(self):
        super().__init__()
        # ngrok URL을 환경 변수로 설정하거나 기본 로컬 WebSocket 서버 사용
        self.ws_url = os.getenv('WEBSOCKET_SERVER_URL', 'ws://localhost:5001')
        self.running = False
    
    async def connect(self):
        """WebSocket 서버에 연결"""
        try:
            async with websockets.connect(self.ws_url) as websocket:
                self.running = True
                while self.running:
                    try:
                        message = await websocket.recv()
                        # JSON 메시지 파싱
                        order_data = json.loads(message)
                        # 주문 수신 시그널 발생
                        self.order_received.emit(order_data)
                    except websockets.ConnectionClosed:
                        print("WebSocket 연결이 종료되었습니다.")
                        break
                    except json.JSONDecodeError:
                        print("잘못된 JSON 형식입니다.")
                    except Exception as e:
                        print(f"오류 발생: {e}")
        except Exception as e:
            print(f"WebSocket 연결 실패: {e}")
    
    def stop(self):
        """클라이언트 중지"""
        self.running = False 