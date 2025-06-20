import sys
import os
import logging
import atexit
import signal
from pathlib import Path
import threading
import traceback

from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer

from src.gui.main_window import MainWindow
from src.updater import check_and_update
from src.supabase_client import SupabaseClient
from src.database.remote_log_handler import RemoteLogManager

# 전역 변수
remote_log_manager = None
supabase_client = None

def setup_logging():
    """로깅 설정"""
    log_path = Path(os.getenv("APP_LOG_PATH", "app.log"))
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path, encoding='utf-8')
        ]
    )

def setup_remote_logging():
    """원격 로깅 설정"""
    global remote_log_manager, supabase_client
    
    try:
        # Supabase 클라이언트 생성
        supabase_client = SupabaseClient()
        
        # 원격 로그 매니저 생성 및 설정
        remote_log_manager = RemoteLogManager(supabase_client)
        success = remote_log_manager.setup_remote_logging(log_level=logging.INFO)
        
        if success:
            logging.info("원격 로깅 시스템이 성공적으로 초기화되었습니다.")
        else:
            logging.warning("원격 로깅 시스템 초기화에 실패했습니다. 로컬 로깅만 사용합니다.")
            
    except Exception as e:
        logging.warning(f"원격 로깅 설정 실패: {e}. 로컬 로깅만 사용합니다.")

def cleanup_on_exit():
    """프로그램 종료 시 정리 작업"""
    global remote_log_manager
    
    try:
        logging.info("프로그램 종료 절차를 시작합니다.")
        
        if remote_log_manager:
            remote_log_manager.remove_remote_logging()
            
    except Exception as e:
        print(f"종료 시 정리 작업 실패: {e}")

def handle_exception(exc_type, exc_value, exc_traceback):
    """처리되지 않은 예외를 로깅"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Ctrl+C는 정상적인 종료로 처리
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # 예외 정보를 로그로 기록
    error_msg = f"처리되지 않은 예외 발생: {exc_type.__name__}: {exc_value}"
    import traceback
    error_details = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    logging.error(error_msg, exc_info=(exc_type, exc_value, exc_traceback))
    
    # 원격으로도 오류 전송
    if remote_log_manager and remote_log_manager.supabase_client:
        try:
            remote_log_manager.supabase_client.send_error_log(
                message=error_msg,
                error_details=error_details,
                module_name="main",
                function_name="handle_exception"
            )
        except:
            pass  # 로그 전송 실패는 무시

def signal_handler(signum, frame):
    """시그널 핸들러 (Windows에서는 SIGINT만 지원)"""
    logging.info(f"시그널 {signum} 수신. 프로그램을 안전하게 종료합니다.")
    cleanup_on_exit()
    sys.exit(0)

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

class POSApplication(QApplication):
    """POS 애플리케이션 클래스"""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.main_window = None
        
        # 애플리케이션 종료 시 정리 작업 연결
        self.aboutToQuit.connect(self.cleanup)
    
    def cleanup(self):
        """애플리케이션 종료 시 정리"""
        try:
            logging.info("애플리케이션이 종료됩니다.")
            cleanup_on_exit()
        except Exception as e:
            print(f"정리 작업 중 오류: {e}")

def main():
    # 예외 처리 핸들러 설정
    sys.excepthook = handle_exception
    
    # 시그널 핸들러 설정 (Windows에서는 SIGINT만)
    try:
        signal.signal(signal.SIGINT, signal_handler)
    except AttributeError:
        pass  # Windows에서 지원하지 않는 시그널은 무시
    
    # 종료 시 정리 함수 등록
    atexit.register(cleanup_on_exit)
    
    # 기본 로깅 설정
    setup_logging()
    
    # 환경 변수 로드
    load_dotenv()
    
    logging.info("POS 프린터 애플리케이션을 시작합니다.")
    
    # 원격 로깅 설정
    setup_remote_logging()
    
    try:
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
        
        # Qt 애플리케이션 생성
        app = POSApplication(sys.argv)
        
        # 메인 윈도우 생성
        window = MainWindow(supabase_config, db_config)
        app.main_window = window
        window.show()
        
        # 백그라운드에서 업데이트 확인
        update_thread = threading.Thread(target=check_for_updates_async, daemon=True)
        update_thread.start()
        
        logging.info("프로그램이 성공적으로 시작되었습니다.")
        
        # 애플리케이션 실행
        result = app.exec()
        
        logging.info("애플리케이션 이벤트 루프가 종료되었습니다.")
        return result
        
    except Exception as e:
        error_msg = f"메인 함수에서 치명적 오류 발생: {e}"
        logging.error(error_msg, exc_info=True)
        
        # 원격으로 오류 전송
        if remote_log_manager and remote_log_manager.supabase_client:
            try:
                remote_log_manager.supabase_client.send_error_log(
                    message=error_msg,
                    error_details=str(e),
                    module_name="main",
                    function_name="main"
                )
            except:
                pass
        
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 