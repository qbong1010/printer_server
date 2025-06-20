#!/usr/bin/env python3
"""
POS 프린터 로그 모니터링 시스템 테스트 스크립트

이 스크립트는 로그 모니터링 시스템이 제대로 작동하는지 테스트합니다.
실제 운영 환경에서 실행하기 전에 테스트 환경에서 먼저 실행해보세요.
"""

import os
import sys
import time
import logging
from dotenv import load_dotenv

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.supabase_client import SupabaseClient
from src.database.remote_log_handler import RemoteLogManager

def test_supabase_connection():
    """Supabase 연결 테스트"""
    print("🔗 Supabase 연결 테스트 중...")
    
    try:
        client = SupabaseClient()
        print(f"   클라이언트 ID: {client.client_info['client_id']}")
        print(f"   클라이언트 이름: {client.client_info['client_name']}")
        print(f"   OS 정보: {client.client_info['os_info']}")
        print(f"   앱 버전: {client.client_info['app_version']}")
        print("✅ Supabase 클라이언트 생성 성공")
        return client
        
    except Exception as e:
        print(f"❌ Supabase 연결 실패: {e}")
        return None

def test_log_sending(client):
    """로그 전송 테스트"""
    print("\n📤 로그 전송 테스트 중...")
    
    test_cases = [
        {
            "log_level": "INFO",
            "log_type": "startup",
            "message": "테스트 - 애플리케이션 시작",
            "module_name": "test_script"
        },
        {
            "log_level": "INFO", 
            "log_type": "info",
            "message": "테스트 - 일반 정보 로그",
            "module_name": "test_script",
            "function_name": "test_log_sending"
        },
        {
            "log_level": "WARNING",
            "log_type": "warning", 
            "message": "테스트 - 경고 로그",
            "module_name": "test_script"
        },
        {
            "log_level": "ERROR",
            "log_type": "error",
            "message": "테스트 - 오류 로그",
            "error_details": "이것은 테스트용 오류 상세 정보입니다.",
            "module_name": "test_script",
            "function_name": "test_error_case",
            "line_number": 100
        }
    ]
    
    success_count = 0
    for i, test_case in enumerate(test_cases, 1):
        try:
            result = client.send_log(**test_case)
            if result:
                print(f"   ✅ 테스트 {i}: {test_case['log_type']} 로그 전송 성공")
                success_count += 1
            else:
                print(f"   ❌ 테스트 {i}: {test_case['log_type']} 로그 전송 실패")
            
            # 너무 빠른 요청 방지
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   ❌ 테스트 {i} 오류: {e}")
    
    print(f"\n📊 로그 전송 테스트 결과: {success_count}/{len(test_cases)} 성공")
    return success_count == len(test_cases)

def test_remote_logging_handler():
    """원격 로깅 핸들러 테스트"""
    print("\n🔧 원격 로깅 핸들러 테스트 중...")
    
    try:
        # 임시 로거 생성
        test_logger = logging.getLogger("test_remote_logging")
        test_logger.setLevel(logging.DEBUG)
        
        # Supabase 클라이언트 생성
        client = SupabaseClient()
        
        # 원격 로그 매니저 생성
        remote_log_manager = RemoteLogManager(client)
        
        # 원격 로깅 설정
        success = remote_log_manager.setup_remote_logging(log_level=logging.INFO)
        
        if not success:
            print("   ❌ 원격 로깅 핸들러 설정 실패")
            return False
        
        print("   ✅ 원격 로깅 핸들러 설정 성공")
        
        # 테스트 로그 발생
        test_logger.info("테스트 - Python logging을 통한 INFO 로그")
        test_logger.warning("테스트 - Python logging을 통한 WARNING 로그") 
        
        try:
            # 의도적 오류 발생으로 ERROR 로그 테스트
            1 / 0
        except ZeroDivisionError:
            test_logger.error("테스트 - Python logging을 통한 ERROR 로그", exc_info=True)
        
        print("   ✅ 테스트 로그 발생 완료")
        
        # 정리
        time.sleep(2)  # 로그 전송 대기
        remote_log_manager.remove_remote_logging()
        print("   ✅ 원격 로깅 핸들러 정리 완료")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 원격 로깅 핸들러 테스트 실패: {e}")
        return False

def test_log_retrieval(client):
    """로그 조회 테스트"""
    print("\n📥 로그 조회 테스트 중...")
    
    try:
        logs = client.get_client_logs(limit=10)
        
        if logs:
            print(f"   ✅ 로그 조회 성공: {len(logs)}개 로그 조회됨")
            
            # 최근 3개 로그 출력
            print("   📋 최근 로그 샘플:")
            for i, log in enumerate(logs[:3], 1):
                created_at = log.get('created_at', 'N/A')
                log_level = log.get('log_level', 'N/A')
                message = log.get('message', 'N/A')
                print(f"      {i}. [{created_at}] {log_level}: {message}")
        else:
            print("   ⚠️ 조회된 로그가 없습니다 (정상일 수 있음)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 로그 조회 실패: {e}")
        return False

def test_startup_shutdown_logs(client):
    """시작/종료 로그 테스트"""
    print("\n🚀 시작/종료 로그 테스트 중...")
    
    try:
        # 시작 로그 전송
        startup_result = client.send_startup_log()
        if startup_result:
            print("   ✅ 시작 로그 전송 성공")
        else:
            print("   ❌ 시작 로그 전송 실패")
        
        time.sleep(1)
        
        # 종료 로그 전송
        shutdown_result = client.send_shutdown_log()
        if shutdown_result:
            print("   ✅ 종료 로그 전송 성공")
        else:
            print("   ❌ 종료 로그 전송 실패")
        
        return startup_result and shutdown_result
        
    except Exception as e:
        print(f"   ❌ 시작/종료 로그 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("=" * 60)
    print("🧪 POS 프린터 로그 모니터링 시스템 테스트")
    print("=" * 60)
    
    # 환경 변수 로드
    load_dotenv()
    
    # 필수 환경 변수 확인
    required_env_vars = ['SUPABASE_URL', 'SUPABASE_API_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 필수 환경 변수가 누락되었습니다: {', '.join(missing_vars)}")
        print("   .env 파일을 확인해주세요.")
        return False
    
    print("✅ 환경 변수 확인 완료")
    
    # 테스트 실행
    test_results = []
    
    # 1. Supabase 연결 테스트
    client = test_supabase_connection()
    if not client:
        print("\n❌ Supabase 연결 실패로 테스트를 중단합니다.")
        return False
    test_results.append(True)
    
    # 2. 로그 전송 테스트
    test_results.append(test_log_sending(client))
    
    # 3. 시작/종료 로그 테스트
    test_results.append(test_startup_shutdown_logs(client))
    
    # 4. 원격 로깅 핸들러 테스트
    test_results.append(test_remote_logging_handler())
    
    # 5. 로그 조회 테스트 (잠시 대기 후)
    print("\n⏳ 로그 전송 완료 대기 중... (3초)")
    time.sleep(3)
    test_results.append(test_log_retrieval(client))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    test_names = [
        "Supabase 연결",
        "로그 전송",
        "시작/종료 로그",
        "원격 로깅 핸들러",
        "로그 조회"
    ]
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    for i, (name, result) in enumerate(zip(test_names, test_results)):
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{i+1}. {name}: {status}")
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\n전체 테스트 결과: {passed_tests}/{total_tests} 통과 ({success_rate:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 모든 테스트가 성공했습니다! 시스템이 정상적으로 작동합니다.")
        print("\n다음 단계:")
        print("1. Supabase 대시보드에서 app_logs 테이블을 확인하세요")
        print("2. monitoring_queries.sql의 쿼리들을 사용해 로그를 모니터링하세요")
        print("3. 실제 애플리케이션을 실행하여 로그 수집을 시작하세요")
    else:
        print("⚠️ 일부 테스트가 실패했습니다. 설정을 다시 확인해주세요.")
        print("\n문제 해결 방법:")
        print("1. .env 파일의 Supabase 설정 확인")
        print("2. Supabase에서 app_logs 테이블 생성 여부 확인")
        print("3. API 키 권한 확인")
        print("4. 네트워크 연결 상태 확인")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자에 의해 테스트가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {e}")
        sys.exit(1) 