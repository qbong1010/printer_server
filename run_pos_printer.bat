@echo off
chcp 65001 >nul
title POS 프린터 프로그램

echo ========================================
echo         POS 프린터 프로그램
echo ========================================
echo.

:: 현재 스크립트 위치 확인
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: 실행 파일 존재 확인
if not exist "POSPrinter.exe" (
    echo ❌ POSPrinter.exe 파일을 찾을 수 없습니다.
    echo 현재 폴더에 POSPrinter.exe가 있는지 확인하세요.
    echo.
    pause
    exit /b 1
)

:: 환경 변수 파일 확인
if not exist ".env" (
    echo ⚠️  .env 파일이 없습니다.
    echo Supabase 설정이 필요합니다.
    echo.
    set /p "CREATE_ENV=환경 설정 파일을 생성하시겠습니까? (y/n): "
    if /i "%CREATE_ENV%"=="y" (
        echo.
        echo === Supabase 설정 입력 ===
        set /p "SUPABASE_PROJECT_ID=프로젝트 ID: "
        set /p "SUPABASE_API_KEY=API 키: "
        set /p "SUPABASE_URL=Supabase URL: "
        set /p "DEFAULT_PRINTER_NAME=기본 프린터 이름: "
        
        (
            echo SUPABASE_PROJECT_ID=%SUPABASE_PROJECT_ID%
            echo SUPABASE_API_KEY=%SUPABASE_API_KEY%
            echo SUPABASE_URL=%SUPABASE_URL%
            echo DEFAULT_PRINTER_NAME=%DEFAULT_PRINTER_NAME%
            echo DEBUG=False
            echo CACHE_DB_PATH=cache.db
            echo APP_LOG_PATH=app.log
        ) > .env
        
        echo ✅ .env 파일이 생성되었습니다.
        echo.
    ) else (
        echo 프로그램을 종료합니다.
        pause
        exit /b 1
    )
)

:: 프린터 설정 파일 확인
if not exist "printer_config.json" (
    echo ⚠️  printer_config.json 파일이 없습니다.
    echo 기본 프린터 설정을 생성합니다.
    (
        echo {
        echo     "printer_type": "usb",
        echo     "printer_name": "POS-58",
        echo     "paper_width": 58,
        echo     "encoding": "cp949"
        echo }
    ) > printer_config.json
    echo ✅ printer_config.json 파일이 생성되었습니다.
    echo.
)

:: 로그 폴더 생성
if not exist "logs" mkdir logs

:: 프로그램 실행
echo 🚀 POS 프린터 프로그램을 시작합니다...
echo.
echo 프로그램을 종료하려면 창을 닫거나 Ctrl+C를 누르세요.
echo.

:: 프로그램 실행 및 오류 처리
POSPrinter.exe
if errorlevel 1 (
    echo.
    echo ❌ 프로그램 실행 중 오류가 발생했습니다.
    echo.
    echo 문제 해결 방법:
    echo 1. 관리자 권한으로 실행해보세요
    echo 2. 프린터가 연결되어 있는지 확인하세요
    echo 3. 인터넷 연결을 확인하세요
    echo 4. app.log 파일을 확인하세요
    echo.
    pause
    exit /b 1
)

echo.
echo 프로그램이 정상적으로 종료되었습니다.
pause 