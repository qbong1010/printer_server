# POS 프린터 프로그램 배포 스크립트
# 이 스크립트는 GitHub에서 자동으로 배포 패키지를 생성합니다

param(
    [string]$Version = "1.0.0",
    [string]$OutputPath = ".\release",
    [switch]$CreateInstaller = $true
)

Write-Host "=== POS 프린터 프로그램 배포 패키지 생성 ===" -ForegroundColor Green

# 출력 디렉토리 생성
if (Test-Path $OutputPath) {
    Remove-Item $OutputPath -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $OutputPath | Out-Null

# 배포할 파일 목록
$filesToInclude = @(
    "main.py",
    "requirements.txt", 
    "printer_config.json",
    "src",
    "setup_utility",
    "libusb-1.0.dll",
    "installer.ps1",
    "INSTALLATION_GUIDE.md",
    "version.json"
)

# 파일 복사
Write-Host "배포 파일 복사 중..." -ForegroundColor Yellow
foreach ($file in $filesToInclude) {
    if (Test-Path $file) {
        Copy-Item -Path $file -Destination $OutputPath -Recurse -Force
        Write-Host "복사됨: $file" -ForegroundColor Gray
    } else {
        Write-Host "경고: $file 파일을 찾을 수 없습니다" -ForegroundColor Yellow
    }
}

# 버전 정보 업데이트
$versionFile = Join-Path $OutputPath "version.json"
if (Test-Path $versionFile) {
    $versionInfo = Get-Content $versionFile | ConvertFrom-Json
    $versionInfo.version = $Version
    $versionInfo.updated_at = Get-Date -Format "yyyy-MM-dd"
    $versionInfo | ConvertTo-Json -Depth 10 | Set-Content $versionFile -Encoding UTF8
}

# ZIP 파일 생성
if ($CreateInstaller) {
    Write-Host "ZIP 패키지 생성 중..." -ForegroundColor Yellow
    $zipPath = "POS_Printer_v$Version.zip"
    
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }
    
    Compress-Archive -Path "$OutputPath\*" -DestinationPath $zipPath -Force
    Write-Host "배포 패키지 생성 완료: $zipPath" -ForegroundColor Green
}

# README 생성
$readmeContent = @"
# POS 프린터 프로그램 v$Version

## 설치 방법
1. ZIP 파일을 압축 해제하세요
2. PowerShell을 관리자 권한으로 실행하세요
3. 압축 해제한 폴더로 이동하세요
4. .\installer.ps1 명령을 실행하세요

## 설정 방법
자세한 설정 방법은 INSTALLATION_GUIDE.md 파일을 참조하세요.

## 업데이트
프로그램에서 자동으로 업데이트를 확인합니다.

---
배포일: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
버전: $Version
"@

Set-Content -Path (Join-Path $OutputPath "README.txt") -Value $readmeContent -Encoding UTF8

Write-Host ""
Write-Host "=== 배포 패키지 생성 완료! ===" -ForegroundColor Green
Write-Host "출력 경로: $OutputPath" -ForegroundColor Cyan
if ($CreateInstaller) {
    Write-Host "ZIP 파일: $zipPath" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "GitHub 릴리즈에 업로드할 파일:" -ForegroundColor Yellow
if (Test-Path $zipPath) {
    Write-Host "- $zipPath" -ForegroundColor Gray
}
Write-Host "- INSTALLATION_GUIDE.md" -ForegroundColor Gray 