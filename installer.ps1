# POS 프린터 프로그램 자동 설치 스크립트
# 관리자 권한으로 실행해야 합니다.

param(
    [string]$InstallPath = "C:\POSPrinter",
    [switch]$CreateDesktopShortcut = $true
)

Write-Host "=== POS 프린터 프로그램 설치 스크립트 ===" -ForegroundColor Green
Write-Host ""

# 관리자 권한 확인
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ 이 스크립트는 관리자 권한으로 실행해야 합니다." -ForegroundColor Red
    Write-Host "PowerShell을 관리자 권한으로 실행한 후 다시 시도하세요." -ForegroundColor Yellow
    exit 1
}

# 설치 경로 생성
Write-Host "📁 설치 경로 생성 중: $InstallPath" -ForegroundColor Cyan
if (!(Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
}

# 현재 스크립트 위치에서 파일 복사
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$DeployPath = Join-Path $ScriptPath "deploy"

if (!(Test-Path $DeployPath)) {
    Write-Host "❌ 배포 폴더를 찾을 수 없습니다: $DeployPath" -ForegroundColor Red
    Write-Host "먼저 build_exe.py를 실행하여 배포 파일을 생성하세요." -ForegroundColor Yellow
    exit 1
}

# 파일 복사
Write-Host "📋 파일 복사 중..." -ForegroundColor Cyan
Copy-Item -Path "$DeployPath\*" -Destination $InstallPath -Recurse -Force

# 바탕화면 바로가기 생성
if ($CreateDesktopShortcut) {
    Write-Host "🖥️ 바탕화면 바로가기 생성 중..." -ForegroundColor Cyan
    $DesktopPath = [Environment]::GetFolderPath("Desktop")
    $ShortcutPath = Join-Path $DesktopPath "POS 프린터.lnk"
    $TargetPath = Join-Path $InstallPath "POSPrinter.exe"
    
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = $TargetPath
    $Shortcut.WorkingDirectory = $InstallPath
    $Shortcut.Description = "POS 프린터 프로그램"
    $Shortcut.Save()
}

# 시작 메뉴 바로가기 생성
Write-Host "📋 시작 메뉴 바로가기 생성 중..." -ForegroundColor Cyan
$StartMenuPath = [Environment]::GetFolderPath("StartMenu")
$ProgramsPath = Join-Path $StartMenuPath "Programs"
$POSFolder = Join-Path $ProgramsPath "POS 프린터"

if (!(Test-Path $POSFolder)) {
    New-Item -ItemType Directory -Path $POSFolder -Force | Out-Null
}

$StartMenuShortcut = Join-Path $POSFolder "POS 프린터.lnk"
$TargetPath = Join-Path $InstallPath "POSPrinter.exe"

$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($StartMenuShortcut)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = $InstallPath
$Shortcut.Description = "POS 프린터 프로그램"
$Shortcut.Save()

# 환경 변수 설정 (선택사항)
Write-Host "🔧 환경 변수 설정 중..." -ForegroundColor Cyan
$EnvPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
if ($EnvPath -notlike "*$InstallPath*") {
    $NewPath = "$EnvPath;$InstallPath"
    [Environment]::SetEnvironmentVariable("PATH", $NewPath, "Machine")
    Write-Host "✅ PATH 환경 변수에 설치 경로가 추가되었습니다." -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ 설치가 완료되었습니다!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 다음 단계:" -ForegroundColor Yellow
Write-Host "1. $InstallPath\.env 파일을 편집하여 Supabase 설정을 입력하세요."
Write-Host "2. 프린터가 연결되어 있는지 확인하세요."
Write-Host "3. 바탕화면의 'POS 프린터' 바로가기를 클릭하여 프로그램을 실행하세요."
Write-Host ""
Write-Host "📁 설치 위치: $InstallPath" -ForegroundColor Cyan
Write-Host "🖥️ 바탕화면 바로가기: $DesktopPath\POS 프린터.lnk" -ForegroundColor Cyan
Write-Host "📋 시작 메뉴: 시작 > 프로그램 > POS 프린터" -ForegroundColor Cyan

# 설치 완료 후 바로가기 실행 여부 확인
$RunNow = Read-Host "프로그램을 지금 실행하시겠습니까? (y/n)"
if ($RunNow -eq "y" -or $RunNow -eq "Y") {
    Write-Host "🚀 프로그램 실행 중..." -ForegroundColor Green
    Start-Process -FilePath (Join-Path $InstallPath "POSPrinter.exe")
} 