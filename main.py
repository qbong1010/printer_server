import sys
import os
import logging
from pathlib import Path

from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication
from src.gui.main_window import MainWindow

def setup_logging():
    # 로깅 설정
    log_path = Path(os.getenv("APP_LOG_PATH", "app.log"))
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path, encoding='utf-8')
        ]
    )

def main():
    setup_logging()
    load_dotenv()
    
    # Supabase 설정을 중앙에서 관리
    supabase_config = {
        'url': os.getenv('SUPABASE_URL'),
        'project_id': os.getenv('SUPABASE_PROJECT_ID'),
        'api_key': os.getenv('SUPABASE_API_KEY')
    }
    
    # 데이터베이스 설정을 중앙에서 관리
    db_path = Path(os.getenv("CACHE_DB_PATH", "cache.db")).resolve()
    db_config = {
        'path': str(db_path)
    }
    
    logging.info(f"Supabase URL: {supabase_config['url']}")
    logging.info(f"데이터베이스 파일 위치: {db_config['path']}")
    
    app = QApplication(sys.argv)
    window = MainWindow(supabase_config, db_config)  # 설정을 전달
    window.show()
    
    logging.info("프로그램이 성공적으로 시작되었습니다.")
    
    # 애플리케이션 실행
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 