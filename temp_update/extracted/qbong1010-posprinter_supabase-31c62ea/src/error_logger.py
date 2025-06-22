import os
import sys
import logging
import platform
import uuid
import traceback
import json
from datetime import datetime
from typing import Optional, Dict, Any
import requests
import threading
from queue import Queue, Empty
import time

class SupabaseLogHandler(logging.Handler):
    """Supabase에 로그를 실시간으로 전송하는 로깅 핸들러"""
    
    def __init__(self, supabase_url: str, supabase_api_key: str, client_id: str = None, 
                 client_name: str = None, app_version: str = "1.0.0"):
        super().__init__()
        self.supabase_url = supabase_url.rstrip('/')
        self.supabase_api_key = supabase_api_key
        self.client_id = client_id or self._generate_client_id()
        self.client_name = client_name or f"POS-{platform.node()}"
        self.app_version = app_version
        self.os_info = f"{platform.system()} {platform.release()} {platform.version()}"
        
        # 로그 전송용 큐와 워커 스레드
        self.log_queue = Queue()
        self.shutdown_event = threading.Event()  # 종료 이벤트 추가
        self.worker_thread = threading.Thread(target=self._log_worker, daemon=True)
        self.worker_thread.start()
        
        # 헤더 설정
        self.headers = {
            "apikey": self.supabase_api_key,
            "Authorization": f"Bearer {self.supabase_api_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        logging.getLogger(__name__).info(f"Supabase 로그 핸들러 초기화 완료 - 클라이언트 ID: {self.client_id}")
    
    def shutdown(self):
        """로그 핸들러 안전 종료"""
        self.shutdown_event.set()
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)  # 최대 2초 대기
    
    def _generate_client_id(self) -> str:
        """고유한 클라이언트 ID 생성"""
        # 컴퓨터 이름과 MAC 주소를 조합하여 고유 ID 생성
        import getpass
        try:
            import uuid
            mac = hex(uuid.getnode())[2:]  # MAC 주소 (16진수)
            username = getpass.getuser()
            hostname = platform.node()
            client_id = f"{hostname}-{username}-{mac[:8]}"
            return client_id
        except Exception:
            # 실패 시 랜덤 UUID 사용
            return str(uuid.uuid4())[:8]
    
    def emit(self, record: logging.LogRecord):
        """로그 레코드를 큐에 추가"""
        try:
            # 종료 이벤트가 설정되었으면 로그를 큐에 추가하지 않음
            if self.shutdown_event.is_set():
                return
                
            log_data = self._format_log_record(record)
            # 큐가 너무 크면 오래된 로그 제거
            if self.log_queue.qsize() > 100:
                try:
                    self.log_queue.get_nowait()
                except Empty:
                    pass
            self.log_queue.put(log_data, block=False)
        except Exception:
            # 로깅 핸들러에서 예외가 발생하면 조용히 무시
            pass
    
    def _format_log_record(self, record: logging.LogRecord) -> Dict[str, Any]:
        """로그 레코드를 Supabase 형식으로 변환"""
        # 에러 세부 정보 추출
        error_details = None
        if record.exc_info:
            error_details = self.format(record)
        
        # 로그 타입 결정
        log_type = self._determine_log_type(record)
        
        return {
            "client_id": self.client_id,
            "client_name": self.client_name,
            "log_level": record.levelname,
            "log_type": log_type,
            "message": record.getMessage(),
            "error_details": error_details,
            "module_name": record.module if hasattr(record, 'module') else record.name,
            "function_name": record.funcName if record.funcName != '<module>' else None,
            "line_number": record.lineno,
            "app_version": self.app_version,
            "os_info": self.os_info,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
    
    def _determine_log_type(self, record: logging.LogRecord) -> str:
        """로그 레코드에서 로그 타입을 결정"""
        message = record.getMessage().lower()
        module_name = record.name.lower()
        
        if 'printer' in module_name or 'print' in message:
            return 'PRINTER'
        elif 'supabase' in module_name or 'database' in module_name or 'db' in message:
            return 'DATABASE'
        elif 'gui' in module_name or 'widget' in module_name:
            return 'GUI'
        elif 'network' in message or 'connection' in message:
            return 'NETWORK'
        elif record.levelname in ['ERROR', 'CRITICAL']:
            return 'ERROR'
        elif record.levelname == 'WARNING':
            return 'WARNING'
        else:
            return 'INFO'
    
    def _log_worker(self):
        """백그라운드에서 로그를 Supabase에 전송하는 워커"""
        consecutive_failures = 0
        max_consecutive_failures = 10  # 연속 실패 허용 횟수
        
        while not self.shutdown_event.is_set():
            try:
                # 큐에서 로그 데이터 가져오기 (최대 1초 대기)
                log_data = self.log_queue.get(timeout=1.0)
                
                # Supabase 전송 시도
                success = self._send_to_supabase(log_data)
                
                if success:
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                
                self.log_queue.task_done()
                
                # 연속 실패가 많으면 잠시 대기
                if consecutive_failures >= max_consecutive_failures:
                    time.sleep(5.0)  # 5초 대기
                    consecutive_failures = 0  # 카운터 리셋
                    
            except Empty:
                # 큐가 비어있는 경우 - 정상 상황
                continue
            except Exception as e:
                # 예외 발생 시 짧은 대기 후 계속
                consecutive_failures += 1
                time.sleep(0.5)
                
                # 너무 많은 연속 실패가 발생하면 더 오래 대기
                if consecutive_failures >= max_consecutive_failures:
                    time.sleep(10.0)
                    consecutive_failures = 0
    
    def _send_to_supabase(self, log_data: Dict[str, Any], max_retries: int = 3):
        """실제로 Supabase에 로그 데이터 전송"""
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.supabase_url}/rest/v1/app_logs",
                    headers=self.headers,
                    json=log_data,
                    timeout=5.0
                )
                
                if response.status_code in [200, 201]:
                    return True
                else:
                    if attempt == max_retries - 1:
                        # 최종 실패 시에만 로컬 로그에 기록
                        logging.getLogger(__name__).error(
                            f"Supabase 로그 전송 실패 (HTTP {response.status_code}): {log_data['message'][:100]}"
                        )
                    
            except requests.exceptions.Timeout:
                if attempt == max_retries - 1:
                    logging.getLogger(__name__).warning("Supabase 로그 전송 타임아웃")
            except requests.exceptions.ConnectionError:
                if attempt == max_retries - 1:
                    logging.getLogger(__name__).warning("Supabase 연결 실패")
            except Exception as e:
                if attempt == max_retries - 1:
                    logging.getLogger(__name__).error(f"Supabase 로그 전송 중 예외: {e}")
            
            # 재시도 전 대기
            time.sleep(0.5 * (attempt + 1))
        
        return False

class ErrorLogger:
    """프로젝트 전체의 에러 로깅을 관리하는 클래스"""
    
    def __init__(self, supabase_url: str, supabase_api_key: str, client_id: str = None, 
                 client_name: str = None, app_version: str = "1.0.0"):
        self.supabase_handler = SupabaseLogHandler(
            supabase_url, supabase_api_key, client_id, client_name, app_version
        )
        self._setup_logging()
    
    def _setup_logging(self):
        """전체 로깅 시스템에 Supabase 핸들러 추가"""
        # 루트 로거에 Supabase 핸들러 추가
        root_logger = logging.getLogger()
        
        # 기존 Supabase 핸들러가 있는지 확인하고 제거
        for handler in root_logger.handlers[:]:
            if isinstance(handler, SupabaseLogHandler):
                root_logger.removeHandler(handler)
        
        # 새 Supabase 핸들러 추가
        self.supabase_handler.setLevel(logging.WARNING)  # WARNING 이상만 Supabase로 전송
        root_logger.addHandler(self.supabase_handler)
        
        # 포맷터 설정
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.supabase_handler.setFormatter(formatter)
    
    def log_system_info(self):
        """시스템 시작 시 기본 정보 로깅"""
        logger = logging.getLogger("system")
        logger.info(f"애플리케이션 시작 - 클라이언트: {self.supabase_handler.client_name}")
        logger.info(f"운영체제: {self.supabase_handler.os_info}")
        logger.info(f"Python 버전: {sys.version}")
        logger.info(f"애플리케이션 버전: {self.supabase_handler.app_version}")
    
    def log_error(self, error: Exception, context: str = "", extra_data: Dict[str, Any] = None):
        """예외를 포함한 상세 에러 로깅"""
        logger = logging.getLogger("error_logger")
        
        error_message = f"{context}: {str(error)}" if context else str(error)
        
        # 추가 데이터가 있으면 메시지에 포함
        if extra_data:
            error_message += f" | 추가정보: {json.dumps(extra_data, ensure_ascii=False)}"
        
        logger.error(error_message, exc_info=True)
    
    def log_printer_error(self, printer_type: str, error: Exception, order_id: str = None):
        """프린터 관련 에러 전용 로깅"""
        logger = logging.getLogger("printer_error")
        context = f"프린터({printer_type}) 오류"
        if order_id:
            context += f" - 주문 ID: {order_id}"
        
        self.log_error(error, context, {"printer_type": printer_type, "order_id": order_id})
    
    def log_database_error(self, operation: str, error: Exception, table_name: str = None):
        """데이터베이스 관련 에러 전용 로깅"""
        logger = logging.getLogger("database_error")
        context = f"데이터베이스 오류({operation})"
        if table_name:
            context += f" - 테이블: {table_name}"
        
        self.log_error(error, context, {"operation": operation, "table_name": table_name})
    
    def log_network_error(self, url: str, error: Exception, method: str = "GET"):
        """네트워크 관련 에러 전용 로깅"""
        logger = logging.getLogger("network_error")
        context = f"네트워크 오류({method} {url})"
        
        self.log_error(error, context, {"url": url, "method": method})
    
    def shutdown(self):
        """에러 로거 안전 종료"""
        if self.supabase_handler:
            self.supabase_handler.shutdown()

# 글로벌 에러 로거 인스턴스
_global_error_logger: Optional[ErrorLogger] = None

def initialize_error_logger(supabase_url: str, supabase_api_key: str, 
                          client_id: str = None, client_name: str = None, 
                          app_version: str = "1.0.0") -> ErrorLogger:
    """글로벌 에러 로거 초기화"""
    global _global_error_logger
    _global_error_logger = ErrorLogger(
        supabase_url, supabase_api_key, client_id, client_name, app_version
    )
    return _global_error_logger

def get_error_logger() -> Optional[ErrorLogger]:
    """글로벌 에러 로거 인스턴스 반환"""
    return _global_error_logger

def shutdown_error_logger():
    """글로벌 에러 로거 안전 종료"""
    global _global_error_logger
    if _global_error_logger:
        _global_error_logger.shutdown()
        _global_error_logger = None

def log_exception(error: Exception, context: str = "", **kwargs):
    """간편한 예외 로깅 함수"""
    if _global_error_logger:
        _global_error_logger.log_error(error, context, kwargs)
    else:
        # 백업용 로깅
        logging.getLogger("error").error(f"{context}: {error}", exc_info=True) 