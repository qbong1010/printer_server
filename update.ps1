# POS 프린터 프로그램 업데이트 스크립트
# 매장에서 쉽게 업데이트할 수 있도록 제작

Write-Host "=== POS 프린터 프로그램 업데이트 ==="
Write-Host "현재 디렉토리: $PWD"
Write-Host ""

# Python 가상환경 확인
if (Test-Path "venv\Scripts\activate.ps1") {
    Write-Host "가상환경 활성화 중..."
    & "venv\Scripts\activate.ps1"
} else {
    Write-Host "경고: 가상환경을 찾을 수 없습니다."
}

# 업데이트 확인 및 적용
Write-Host "업데이트 확인 중..."
try {
    python -c "
from src.updater import check_and_update
import os
os.environ['GITHUB_REPO'] = 'qbong1010/posprinter_supabase'
result = check_and_update('qbong1010/posprinter_supabase', auto_apply=False)
if result:
    print('업데이트가 성공적으로 완료되었습니다!')
    print('프로그램을 다시 시작해주세요.')
else:
    print('현재 최신 버전을 사용 중이거나 업데이트가 취소되었습니다.')
"
} catch {
    Write-Host "오류 발생: $_"
    Write-Host "수동으로 프로그램을 확인해주세요."
}

Write-Host ""
Write-Host "업데이트 확인 완료!"
Write-Host "아무 키나 누르면 창이 닫힙니다..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 