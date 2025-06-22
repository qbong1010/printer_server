# POS 프린터 프로그램 설치 스크립트
# 관리자 권한으로 실행해야 합니다

param(
    [string]$InstallPath = "C:\Program Files\POS_Printer",
    [switch]$SkipPython = $false
)

Write-Host "=== POS 프린터 프로그램 설치를 시작합니다 ===" -ForegroundColor Green

# 관리자 권한 확인
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "이 스크립트는 관리자 권한으로 실행해야 합니다." -ForegroundColor Red
    Write-Host "PowerShell을 '관리자 권한으로 실행'하고 다시 시도해주세요." -ForegroundColor Yellow
    Read-Host "아무 키나 눌러서 종료..."
    exit 1
}

# 설치 디렉토리 생성
Write-Host "설치 디렉토리 생성 중..." -ForegroundColor Yellow
if (!(Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Force -Path $InstallPath | Out-Null
}

# Python 설치 확인 및 설치
if (!$SkipPython) {
    Write-Host "Python 설치 상태 확인 중..." -ForegroundColor Yellow
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python 3\.[8-9]|Python 3\.1[0-9]") {
            Write-Host "Python이 이미 설치되어 있습니다: $pythonVersion" -ForegroundColor Green
        } else {
            throw "Python 버전이 3.8 이상이어야 합니다."
        }
    } catch {
        Write-Host "Python 3.9 설치 중..." -ForegroundColor Yellow
        $pythonUrl = "https://www.python.org/ftp/python/3.9.18/python-3.9.18-amd64.exe"
        $pythonInstaller = "$env:TEMP\python-installer.exe"
        
        Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller
        Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
        Remove-Item $pythonInstaller
        
        # 환경변수 새로고침
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    }
}

# 프로그램 파일 복사
Write-Host "프로그램 파일 복사 중..." -ForegroundColor Yellow
$sourceFiles = @(
    "main.py", "requirements.txt", "printer_config.json", 
    "src", "setup_utility", "libusb-1.0.dll"
)

foreach ($file in $sourceFiles) {
    if (Test-Path $file) {
        Copy-Item -Path $file -Destination $InstallPath -Recurse -Force
        Write-Host "복사됨: $file" -ForegroundColor Gray
    }
}

# 가상환경 생성 및 패키지 설치
Write-Host "Python 가상환경 설정 중..." -ForegroundColor Yellow
Set-Location $InstallPath

python -m venv venv
& .\venv\Scripts\Activate.ps1

Write-Host "필요한 패키지 설치 중..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt

# 설정 파일 생성
Write-Host "기본 설정 파일 생성 중..." -ForegroundColor Yellow
$envContent = @"
# Supabase 설정 (사용자가 수정해야 함)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PROJECT_ID=your-project-id
SUPABASE_API_KEY=your-api-key

# 로그 파일 경로
APP_LOG_PATH=app.log
CACHE_DB_PATH=cache.db
"@

Set-Content -Path ".env" -Value $envContent -Encoding UTF8

# 실행 스크립트 생성
$runScript = @"
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python main.py
pause
"@

Set-Content -Path "run_pos_printer.bat" -Value $runScript

# 바탕화면 바로가기 생성
Write-Host "바탕화면 바로가기 생성 중..." -ForegroundColor Yellow
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$([Environment]::GetFolderPath('Desktop'))\POS 프린터.lnk")
$Shortcut.TargetPath = "$InstallPath\run_pos_printer.bat"
$Shortcut.WorkingDirectory = $InstallPath
$Shortcut.IconLocation = "shell32.dll,77"
$Shortcut.Save()

Write-Host ""
Write-Host "=== 설치가 완료되었습니다! ===" -ForegroundColor Green
Write-Host ""
Write-Host "다음 단계를 진행해주세요:" -ForegroundColor Yellow
Write-Host "1. $InstallPath\.env 파일을 열어서 Supabase 설정을 입력하세요"
Write-Host "2. $InstallPath\printer_config.json 파일에서 프린터 설정을 확인하세요"
Write-Host "3. 바탕화면의 'POS 프린터' 바로가기를 더블클릭하여 프로그램을 실행하세요"
Write-Host ""
Write-Host "설치 위치: $InstallPath" -ForegroundColor Cyan
Read-Host "아무 키나 눌러서 종료..." 