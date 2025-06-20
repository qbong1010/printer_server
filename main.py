import sys
import os
import logging
from zoneinfo import ZoneInfo
import time
from pathlib import Path
import threading
import signal
import atexit
import json
from datetime import datetime, timedelta

from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication, QMessageBox
from src.gui.main_window import MainWindow
from src.updater import check_and_update
from src.error_logger import initialize_error_logger, get_error_logger, shutdown_error_logger

def setup_logging():
    # 로깅 설정
    log_path = Path(os.getenv("APP_LOG_PATH", "app.log"))
    os.environ["TZ"] = "Asia/Seoul"
    try:
        time.tzset()
    except AttributeError:
        pass

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    formatter.converter = lambda ts: datetime.fromtimestamp(ts, ZoneInfo("Asia/Seoul")).timetuple()

    handlers = [
        logging.StreamHandler(),
        logging.FileHandler(log_path, encoding='utf-8')
    ]
    for h in handlers:
        h.setFormatter(formatter)

    logging.basicConfig(level=logging.INFO, handlers=handlers)

def get_last_update_check():
    """마지막 업데이트 확인 시간을 가져옵니다."""
    try:
        update_check_file = Path("last_update_check.json")
        if update_check_file.exists():
            with open(update_check_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return datetime.fromisoformat(data.get('last_check', '2000-01-01T00:00:00'))
        return datetime(2000, 1, 1)  # 기본값: 오래 전 날짜
    except Exception:
        return datetime(2000, 1, 1)

def save_last_update_check():
    """마지막 업데이트 확인 시간을 저장합니다."""
    try:
        update_check_file = Path("last_update_check.json")
        data = {
            'last_check': datetime.now().isoformat(),
            'app_version': get_current_version()
        }
        with open(update_check_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.warning(f"업데이트 확인 시간 저장 실패: {e}")

def get_current_version():
    """현재 앱 버전을 가져옵니다."""
    try:
        version_file = Path("version.json")
        if version_file.exists():
            with open(version_file, 'r', encoding='utf-8') as f:
                version_info = json.load(f)
                return version_info.get('version', '1.0.0')
    except Exception:
        pass
    return '1.0.0'

def should_check_for_updates():
    """업데이트 확인이 필요한지 판단합니다."""
    last_check = get_last_update_check()
    now = datetime.now()
    
    # 환경변수에서 업데이트 확인 주기 설정 (기본값: 24시간)
    check_interval_hours = int(os.getenv('UPDATE_CHECK_INTERVAL', '24'))
    
    # 설정된 시간 이내에 확인했으면 건너뛰기
    if now - last_check < timedelta(hours=check_interval_hours):
        hours_since_check = (now - last_check).total_seconds() / 3600
        logging.info(f"최근 {hours_since_check:.1f}시간 전에 업데이트를 확인했습니다. ({check_interval_hours}시간마다 확인)")
        return False
    
    return True

def check_for_updates_async():
    """백그라운드에서 업데이트 확인 (최초 실행 시 또는 24시간마다)"""
    try:
        # 업데이트 확인 필요성 체크
        if not should_check_for_updates():
            return
        
        # GitHub 저장소 설정 - 실제 저장소로 변경하세요
        github_repo = "your-username/posprinter_supabase"  # 실제 저장소명으로 변경
        
        # 환경변수에서 저장소 설정 가능
        github_repo = os.getenv('GITHUB_REPO', github_repo)
        
        logging.info("업데이트 확인을 시작합니다...")
        
        if github_repo and github_repo != "your-username/posprinter_supabase":
            try:
                if check_and_update(github_repo, auto_apply=False):
                    logging.info("🎉 새로운 업데이트가 확인되었습니다!")
                    # TODO: 사용자에게 업데이트 알림 표시
                else:
                    logging.info("✅ 최신 버전을 사용 중입니다.")
                
                # 업데이트 확인 완료 시간 저장
                save_last_update_check()
                
            except Exception as e:
                logging.warning(f"업데이트 확인 중 오류 발생: {e}")
                # 오류가 발생해도 시간은 저장 (무한 재시도 방지)
                save_last_update_check()
        else:
            logging.info("GitHub 저장소가 설정되지 않아 자동 업데이트를 건너뜁니다.")
            logging.info("환경변수 GITHUB_REPO를 설정하거나 main.py에서 github_repo 변수를 수정하세요.")
            
    except Exception as e:
        logging.warning(f"업데이트 확인 실패: {e}")

def cleanup_on_exit():
    """프로그램 종료 시 정리 작업"""
    logging.info("프로그램 종료 중 - 정리 작업 수행 중...")
    shutdown_error_logger()
    logging.info("정리 작업 완료")

def signal_handler(signum, frame):
    """시그널 핸들러"""
    logging.info(f"시그널 {signum} 수신됨 - 프로그램 종료")
    cleanup_on_exit()
    sys.exit(0)

def main():
    setup_logging()
    load_dotenv()
    
    # 종료 시 정리 작업 등록
    atexit.register(cleanup_on_exit)
    
    # 윈도우에서 Ctrl+C 처리
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    except AttributeError:
        # 윈도우에서 지원하지 않는 시그널은 무시
        pass
    
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
    logging.info(f"현재 앱 버전: {get_current_version()}")
    
    # Supabase 에러 로깅 시스템 초기화
    try:
        if supabase_config['url'] and supabase_config['api_key']:
            # 버전 정보 읽기
            version_info = {"version": "1.0.0"}
            try:
                version_file = Path("version.json")
                if version_file.exists():
                    with open(version_file, 'r', encoding='utf-8') as f:
                        version_info = json.load(f)
            except Exception:
                pass  # 버전 파일 읽기 실패 시 기본값 사용
            
            error_logger = initialize_error_logger(
                supabase_url=supabase_config['url'],
                supabase_api_key=supabase_config['api_key'],
                app_version=version_info.get('version', '1.0.0')
            )
            error_logger.log_system_info()
            logging.info("Supabase 실시간 에러 로깅 시스템이 활성화되었습니다.")
        else:
            logging.warning("Supabase 설정이 없어 에러 로깅 시스템을 초기화할 수 없습니다.")
    except Exception as e:
        logging.error(f"에러 로깅 시스템 초기화 실패: {e}")
    
    app = QApplication(sys.argv)
    
    try:
        window = MainWindow(supabase_config, db_config)  # 설정을 전달
        window.show()
        
        # 백그라운드에서 업데이트 확인 (24시간마다 또는 최초 실행 시)
        try:
            update_thread = threading.Thread(target=check_for_updates_async, daemon=True)
            update_thread.start()
        except Exception as e:
            logging.warning(f"업데이트 확인 스레드 시작 실패: {e}")
        
        logging.info("프로그램이 성공적으로 시작되었습니다.")
        
        # 애플리케이션 실행
        exit_code = app.exec()
        
        # 정상 종료 시에도 정리 작업 수행
        cleanup_on_exit()
        
        sys.exit(exit_code)
        
    except Exception as e:
        logging.error(f"애플리케이션 시작 중 오류 발생: {e}", exc_info=True)
        # 심각한 오류 시 Supabase에도 로깅
        error_logger = get_error_logger()
        if error_logger:
            error_logger.log_error(e, "애플리케이션 시작 실패")
        # 정리 작업 후 종료
        cleanup_on_exit()
        raise

if __name__ == "__main__":
    main() 