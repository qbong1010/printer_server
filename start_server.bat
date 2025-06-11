@echo off
echo WebSocket 서버와 ngrok을 시작합니다...

REM ngrok 프로세스 실행 (새 창에서)
start "ngrok" cmd /c "ngrok http --url=calm-remotely-longhorn.ngrok-free.app 5001"

REM 잠시 대기하여 ngrok이 시작될 때까지 기다림
timeout /t 3

REM WebSocket 서버 실행
python src/websocket/server.py

pause 