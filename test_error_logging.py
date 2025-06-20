#!/usr/bin/env python3
"""
Supabase 에러 로깅 시스템 테스트 스크립트
"""

import os
import sys
import logging
import time
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 경로를 Python path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.error_logger import initialize_error_logger, get_error_logger, log_exception

def test_error_logging():
    """에러 로깅 시스템 테스트"""
    print("=== Supabase 에러 로깅 시스템 테스트 ===")
    
    # 환경 변수 로드
    load_dotenv()
    
    # 기본 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Supabase 설정 확인
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_api_key = os.getenv('SUPABASE_API_KEY')
    
    if not supabase_url or not supabase_api_key:
        print("❌ SUPABASE_URL 또는 SUPABASE_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("   .env 파일을 확인해주세요.")
        return False
    
    print(f"✅ Supabase URL: {supabase_url}")
    print(f"✅ API Key: {supabase_api_key[:10]}...")
    
    try:
        # 에러 로거 초기화
        print("\n1. 에러 로거 초기화 중...")
        error_logger = initialize_error_logger(
            supabase_url=supabase_url,
            supabase_api_key=supabase_api_key,
            client_name="TEST-CLIENT",
            app_version="1.0.0-test"
        )
        print("✅ 에러 로거 초기화 완료")
        
        # 시스템 정보 로깅
        print("\n2. 시스템 정보 로깅 중...")
        error_logger.log_system_info()
        print("✅ 시스템 정보 로깅 완료")
        
        # 다양한 타입의 테스트 로그 전송
        print("\n3. 테스트 로그 전송 중...")
        
        # 일반 WARNING 로그
        logger = logging.getLogger("test_module")
        logger.warning("테스트 경고 메시지입니다.")
        
        # 에러 로그 (예외 포함)
        try:
            1 / 0  # 의도적인 에러
        except Exception as e:
            logger.error("테스트 에러 발생", exc_info=True)
            error_logger.log_error(e, "테스트 에러", {"test_data": "sample"})
        
        # 프린터 에러 로그
        try:
            raise ConnectionError("프린터 연결 실패")
        except Exception as e:
            error_logger.log_printer_error("escpos", e, "TEST-001")
        
        # 데이터베이스 에러 로그
        try:
            raise sqlite3.Error("데이터베이스 연결 실패")
        except Exception as e:
            error_logger.log_database_error("connection", e, "orders")
        
        # 네트워크 에러 로그
        try:
            raise requests.exceptions.Timeout("네트워크 타임아웃")
        except Exception as e:
            error_logger.log_network_error("https://api.example.com", e, "POST")
        
        print("✅ 테스트 로그 전송 완료")
        
        # 로그 전송 대기
        print("\n4. 로그 전송 대기 중 (5초)...")
        time.sleep(5)
        
        print("\n✅ 모든 테스트 완료!")
        print("\n📊 Supabase 대시보드에서 app_logs 테이블을 확인해보세요:")
        print(f"   {supabase_url.replace('/rest/v1', '')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 필요한 모듈 import
    import sqlite3
    import requests.exceptions
    
    success = test_error_logging()
    sys.exit(0 if success else 1) 