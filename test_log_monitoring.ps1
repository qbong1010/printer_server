# POS 프린터 로그 모니터링 시스템 테스트 스크립트 (PowerShell)
# Windows 환경에서 테스트를 실행합니다.

Write-Host "============================================" -ForegroundColor Green
Write-Host "🧪 POS 프린터 로그 모니터링 시스템 테스트" -ForegroundColor Green  
Write-Host "============================================" -ForegroundColor Green

# 현재 위치 확인
$currentPath = Get-Location
Write-Host "📁 현재 위치: $currentPath" -ForegroundColor Yellow

# Python이 설치되어 있는지 확인
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python 확인: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Python이 설치되어 있지 않습니다." -ForegroundColor Red
    Write-Host "   Python을 설치하고 다시 시도해주세요." -ForegroundColor Yellow
    Read-Host "아무 키나 눌러 종료하세요"
    exit 1
}

# 가상환경 확인 및 활성화
if (Test-Path "venv") {
    Write-Host "🔧 가상환경을 활성화합니다..." -ForegroundColor Yellow
    try {
        & "venv\Scripts\Activate.ps1"
        Write-Host "✅ 가상환경 활성화 성공" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️ 가상환경 활성화 실패, 시스템 Python을 사용합니다." -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ 가상환경이 없습니다. 시스템 Python을 사용합니다." -ForegroundColor Yellow
}

# .env 파일 확인
if (Test-Path ".env") {
    Write-Host "✅ .env 파일 확인됨" -ForegroundColor Green
} else {
    Write-Host "❌ .env 파일이 없습니다." -ForegroundColor Red
    Write-Host "   Supabase 설정을 위한 .env 파일을 생성해주세요." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   .env 파일 예시:" -ForegroundColor Cyan
    Write-Host "   SUPABASE_URL=https://your-project.supabase.co" -ForegroundColor Gray
    Write-Host "   SUPABASE_PROJECT_ID=your-project-id" -ForegroundColor Gray  
    Write-Host "   SUPABASE_API_KEY=your-api-key" -ForegroundColor Gray
    Write-Host ""
    Read-Host "아무 키나 눌러 종료하세요"
    exit 1
}

# 필요한 패키지 설치 확인
Write-Host "📦 필요한 패키지를 확인합니다..." -ForegroundColor Yellow

$requiredPackages = @("requests", "python-dotenv", "PySide6")
$missingPackages = @()

foreach ($package in $requiredPackages) {
    try {
        python -c "import $($package.Replace('-', '_'))" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $package 설치됨" -ForegroundColor Green
        } else {
            Write-Host "   ❌ $package 누락" -ForegroundColor Red
            $missingPackages += $package
        }
    }
    catch {
        Write-Host "   ❌ $package 누락" -ForegroundColor Red
        $missingPackages += $package
    }
}

# 누락된 패키지 설치
if ($missingPackages.Count -gt 0) {
    Write-Host "📥 누락된 패키지를 설치합니다..." -ForegroundColor Yellow
    
    if (Test-Path "requirements.txt") {
        try {
            python -m pip install -r requirements.txt
            Write-Host "✅ 패키지 설치 완료" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ 패키지 설치 실패" -ForegroundColor Red
            Write-Host "   수동으로 설치해주세요: python -m pip install -r requirements.txt" -ForegroundColor Yellow
            Read-Host "아무 키나 눌러 종료하세요"
            exit 1
        }
    } else {
        Write-Host "❌ requirements.txt 파일이 없습니다." -ForegroundColor Red
        Write-Host "   수동으로 패키지를 설치해주세요:" -ForegroundColor Yellow
        foreach ($package in $missingPackages) {
            Write-Host "   python -m pip install $package" -ForegroundColor Cyan
        }
        Read-Host "아무 키나 눌러 종료하세요"
        exit 1
    }
}

# 테스트 스크립트 실행
Write-Host ""
Write-Host "🚀 테스트를 시작합니다..." -ForegroundColor Green
Write-Host ""

try {
    python test_log_monitoring.py
    $exitCode = $LASTEXITCODE
    
    Write-Host ""
    if ($exitCode -eq 0) {
        Write-Host "🎉 테스트가 성공적으로 완료되었습니다!" -ForegroundColor Green
        Write-Host ""
        Write-Host "다음 단계:" -ForegroundColor Cyan
        Write-Host "1. Supabase 대시보드에서 app_logs 테이블을 확인하세요" -ForegroundColor White
        Write-Host "2. monitoring_queries.sql의 쿼리들을 사용해 로그를 모니터링하세요" -ForegroundColor White
        Write-Host "3. python main.py로 실제 애플리케이션을 실행하세요" -ForegroundColor White
    } else {
        Write-Host "⚠️ 테스트 중 일부 문제가 발생했습니다." -ForegroundColor Yellow
        Write-Host "위의 오류 메시지를 확인하고 문제를 해결해주세요." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "❌ 테스트 실행 중 오류가 발생했습니다." -ForegroundColor Red
    Write-Host "오류 내용: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🔍 추가 정보:" -ForegroundColor Cyan
Write-Host "- 로그 모니터링 가이드: LOG_MONITORING_GUIDE.md" -ForegroundColor White
Write-Host "- Supabase 테이블 생성: create_log_table.sql" -ForegroundColor White
Write-Host "- 모니터링 쿼리: monitoring_queries.sql" -ForegroundColor White

Write-Host ""
Read-Host "아무 키나 눌러 종료하세요" 