import asyncio
import websockets
import json
from datetime import datetime
import logging

class WebSocketServer:
    def __init__(self, host="localhost", port=5001):
        self.host = host
        self.port = port
        self.clients = set()
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('server.log', encoding='utf-8')
            ]
        )

    async def register(self, websocket):
        """클라이언트 등록"""
        self.clients.add(websocket)
        logging.info(f"새로운 클라이언트 연결됨. 현재 연결 수: {len(self.clients)}")

    async def unregister(self, websocket):
        """클라이언트 등록 해제"""
        self.clients.remove(websocket)
        logging.info(f"클라이언트 연결 해제. 현재 연결 수: {len(self.clients)}")

    async def broadcast_order(self, order_data):
        """모든 클라이언트에게 주문 데이터 전송"""
        if not self.clients:
            logging.warning("연결된 클라이언트가 없습니다.")
            return

        # 타임스탬프 추가
        order_data['timestamp'] = datetime.now().isoformat()
        message = json.dumps(order_data)

        # 연결된 모든 클라이언트에게 전송
        disconnected = set()
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.ConnectionClosed:
                disconnected.add(client)
            except Exception as e:
                logging.error(f"메시지 전송 중 오류 발생: {e}")
                disconnected.add(client)
        
        # 연결이 끊긴 클라이언트 제거
        for client in disconnected:
            await self.unregister(client)

    async def handler(self, websocket):
        """클라이언트 연결 처리"""
        await self.register(websocket)
        try:
            async for message in websocket:
                try:
                    # JSON 형식 검증
                    order_data = json.loads(message)
                    logging.info(f"주문 수신: {order_data}")
                    # 모든 클라이언트에게 브로드캐스트
                    await self.broadcast_order(order_data)
                except json.JSONDecodeError:
                    logging.error("잘못된 JSON 형식")
                except Exception as e:
                    logging.error(f"메시지 처리 중 오류 발생: {e}")
        finally:
            await self.unregister(websocket)

    async def start(self):
        """서버 시작"""
        async with websockets.serve(self.handler, self.host, self.port):
            logging.info(f"WebSocket 서버가 시작되었습니다. ws://{self.host}:{self.port}")
            await asyncio.Future()  # 무기한 실행

def main():
    server = WebSocketServer()
    asyncio.run(server.start())

if __name__ == "__main__":
    main() 