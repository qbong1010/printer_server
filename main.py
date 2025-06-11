import sys
import os
from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
import logging

def setup_logging():
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log', encoding='utf-8')
        ]
    )

def main():
    # 로깅 설정
    setup_logging()
    
    # 환경 변수 로드
    load_dotenv()
    
    # WebSocket 서버 포트 정보 출력
    ws_url = os.getenv('WEBSOCKET_SERVER_URL', 'ws://localhost:5001')
    logging.info(f"WebSocket 서버 URL: {ws_url}")
    
    # 데이터베이스 파일 위치 출력
    db_path = os.path.abspath("orders.db")
    logging.info(f"데이터베이스 파일 위치: {db_path}")
    
    # QApplication 인스턴스 생성
    app = QApplication(sys.argv)
    
    # 메인 윈도우 생성 및 표시
    window = MainWindow()
    window.show()
    
    logging.info("프로그램이 성공적으로 시작되었습니다.")
    
    # 애플리케이션 실행
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 