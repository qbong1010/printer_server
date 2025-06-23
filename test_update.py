#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.updater import check_and_update, get_current_version

def test_update():
    """업데이트 기능 테스트"""
    print("=== 업데이트 기능 테스트 ===")
    print(f"현재 버전: {get_current_version()}")
    
    # 캐시 파일 삭제
    cache_file = Path("last_update_check.json")
    if cache_file.exists():
        cache_file.unlink()
        print("캐시 파일이 삭제되었습니다.")
    
    # 업데이트 확인
    print("\n업데이트 확인 중...")
    try:
        result = check_and_update('qbong1010/posprinter_supabase', auto_apply=False)
        print(f"업데이트 확인 결과: {result}")
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_update() 