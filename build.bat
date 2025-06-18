@echo off
chcp 65001 >nul
title POS 프린터 프로그램 빌드

echo ========================================
echo     POS 프린터 프로그램 빌드 도구
echo ========================================
echo.

:: 현재 디렉토리 확인
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo Python 3.10 이상을 설치한 후 다시 시도하세요.
    echo.
    pause
    exit /b 1
)

echo ✅ Python 설치 확인 완료
python --version

:: 가상환경 확인 및 활성화
if exist "venv\Scripts\activate.bat" (
    echo.
    echo 🔄 가상환경을 활성화합니다...
    call venv\Scripts\activate.bat
    echo ✅ 가상환경 활성화 완료
) else (
    echo.
    echo ⚠️  가상환경이 없습니다. 새로 생성하시겠습니까? (y/n)
    set /p "CREATE_VENV=선택: "
    if /i "%CREATE_VENV%"=="y" (
        echo.
        echo 🔄 가상환경을 생성합니다...
        python -m venv venv
        call venv\Scripts\activate.bat
        echo ✅ 가상환경 생성 및 활성화 완료
        
        echo.
        echo 📦 필요한 패키지를 설치합니다...
        pip install -r requirements.txt
        echo ✅ 패키지 설치 완료
    ) else (
        echo 전역 Python 환경을 사용합니다.
    )
)

:: 필요한 패키지 설치 확인
echo.
echo 📦 PyInstaller 설치 확인 중...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller가 설치되어 있지 않습니다. 설치합니다...
    pip install pyinstaller
)

:: 빌드 실행
echo.
echo 🏗️  실행 파일을 생성합니다...
echo 이 과정은 몇 분 정도 소요될 수 있습니다.
echo.

python build_exe.py

if errorlevel 1 (
    echo.
    echo ❌ 빌드 중 오류가 발생했습니다.
    echo 오류 내용을 확인하고 다시 시도하세요.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo           빌드 완료!
echo ========================================
echo.
echo 📁 생성된 파일들:
echo   - dist\POSPrinter.exe (실행 파일)
echo   - deploy\ (배포 폴더)
echo.
echo 📋 다음 단계:
echo   1. deploy 폴더의 내용을 포스PC로 복사
echo   2. .env 파일을 편집하여 Supabase 설정 입력
echo   3. POSPrinter.exe 실행
echo.
echo 🚀 배포를 위해 deploy 폴더를 확인하세요!
echo.

pause 