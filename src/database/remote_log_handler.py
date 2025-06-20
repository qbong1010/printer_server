import logging
import queue
import threading
import time
import traceback
from typing import Optional

from src.supabase_client import SupabaseClient


class SupabaseLogHandler(logging.Handler):
    """Supabase로 로그를 전송하는 커스텀 핸들러"""
    
    def __init__(self, supabase_client: SupabaseClient, max_queue_size: int = 1000):
        super().__init__()
        self.supabase_client = supabase_client
        self.log_queue = queue.Queue(maxsize=max_queue_size)
        self.worker_thread = None
        self.shutdown_event = threading.Event()
        self.start_worker()
    
    def start_worker(self):
        """백그라운드 워커 스레드 시작"""
        if self.worker_thread is None or not self.worker_thread.is_alive():
            self.worker_thread = threading.Thread(
                target=self._worker_loop,
                daemon=True,
                name="SupabaseLogWorker"
            )
            self.worker_thread.start()
    
    def _worker_loop(self):
        """백그라운드에서 로그를 처리하는 워커 루프"""
        while not self.shutdown_event.is_set():
            try:
                # 큐에서 로그 레코드 가져오기 (타임아웃 1초)
                try:
                    record = self.log_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # 로그 전송 시도
                self._send_log_record(record)
                self.log_queue.task_done()
                
            except Exception as e:
                # 워커 스레드 내부 오류는 조용히 처리
                print(f"로그 워커 스레드 오류: {e}")
                time.sleep(1)
    
    def _send_log_record(self, record: logging.LogRecord):
        """로그 레코드를 Supabase로 전송"""
        try:
            # 오류 상세 정보 추출
            error_details = None
            if record.exc_info:
                error_details = self.format(record)
            elif hasattr(record, 'exc_text') and record.exc_text:
                error_details = record.exc_text
            
            # 로그 타입 결정
            log_type = self._determine_log_type(record)
            
            # Supabase에 로그 전송
            self.supabase_client.send_log(
                log_level=record.levelname,
                log_type=log_type,
                message=record.getMessage(),
                error_details=error_details,
                module_name=record.module if hasattr(record, 'module') else record.name,
                function_name=record.funcName if record.funcName != '<module>' else None,
                line_number=record.lineno if record.lineno else None
            )
            
        except Exception as e:
            # 로그 전송 실패는 조용히 처리 (무한 루프 방지)
            print(f"로그 전송 실패: {e}")
    
    def _determine_log_type(self, record: logging.LogRecord) -> str:
        """로그 레코드에서 로그 타입을 결정"""
        message = record.getMessage().lower()
        
        # 특정 키워드로 로그 타입 판단
        if any(keyword in message for keyword in ['시작', 'startup', 'started', '시작되었습니다']):
            return 'startup'
        elif any(keyword in message for keyword in ['종료', 'shutdown', 'stopped', '종료되었습니다']):
            return 'shutdown'
        elif record.levelno >= logging.ERROR:
            return 'error'
        elif record.levelno >= logging.WARNING:
            return 'warning'
        else:
            return 'info'
    
    def emit(self, record: logging.LogRecord):
        """로그 레코드를 큐에 추가"""
        try:
            # 큐가 가득 찬 경우 오래된 로그를 버림
            if self.log_queue.full():
                try:
                    self.log_queue.get_nowait()
                except queue.Empty:
                    pass
            
            self.log_queue.put_nowait(record)
            
        except Exception:
            # 핸들러 내부 오류 시 조용히 처리
            pass
    
    def close(self):
        """핸들러 종료"""
        self.shutdown_event.set()
        
        # 남은 로그 처리 대기 (최대 5초)
        try:
            if self.worker_thread and self.worker_thread.is_alive():
                self.worker_thread.join(timeout=5.0)
        except:
            pass
        
        super().close()


class RemoteLogManager:
    """원격 로깅 관리자"""
    
    def __init__(self, supabase_client: SupabaseClient):
        self.supabase_client = supabase_client
        self.handler: Optional[SupabaseLogHandler] = None
    
    def setup_remote_logging(self, log_level: int = logging.INFO):
        """원격 로깅 설정"""
        try:
            # 기존 핸들러 제거
            if self.handler:
                self.remove_remote_logging()
            
            # Supabase 로그 핸들러 생성
            self.handler = SupabaseLogHandler(self.supabase_client)
            self.handler.setLevel(log_level)
            
            # 포맷터 설정
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            self.handler.setFormatter(formatter)
            
            # 루트 로거에 핸들러 추가
            root_logger = logging.getLogger()
            root_logger.addHandler(self.handler)
            
            # 시작 로그 전송
            self.supabase_client.send_startup_log()
            
            return True
            
        except Exception as e:
            print(f"원격 로깅 설정 실패: {e}")
            return False
    
    def remove_remote_logging(self):
        """원격 로깅 제거"""
        try:
            if self.handler:
                # 종료 로그 전송
                self.supabase_client.send_shutdown_log()
                
                # 핸들러 제거 및 정리
                root_logger = logging.getLogger()
                root_logger.removeHandler(self.handler)
                self.handler.close()
                self.handler = None
                
        except Exception as e:
            print(f"원격 로깅 제거 실패: {e}")
    
    def send_custom_log(self, level: str, log_type: str, message: str, **kwargs):
        """사용자 정의 로그 전송"""
        try:
            self.supabase_client.send_log(
                log_level=level,
                log_type=log_type,
                message=message,
                **kwargs
            )
        except Exception as e:
            print(f"사용자 정의 로그 전송 실패: {e}") 