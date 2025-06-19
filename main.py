import sys
import os
import logging
from pathlib import Path
import threading

from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication, QMessageBox
from src.gui.main_window import MainWindow
from src.updater import check_and_update

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

def check_for_updates_async():
    """백그라운드에서 업데이트 확인"""
    try:
        # GitHub 저장소 이름을 실제 저장소로 변경하세요
        github_repo = "your-username/posprinter_supabase"
        
        if check_and_update(github_repo, auto_apply=False):
            logging.info("업데이트가 확인되었습니다.")
        else:
            logging.info("최신 버전을 사용 중입니다.")
    except Exception as e:
        logging.warning(f"업데이트 확인 실패: {e}")

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
    
    # 백그라운드에서 업데이트 확인
    update_thread = threading.Thread(target=check_for_updates_async, daemon=True)
    update_thread.start()
    
    logging.info("프로그램이 성공적으로 시작되었습니다.")
    
    # 애플리케이션 실행
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 