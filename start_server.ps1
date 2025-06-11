# ngrok 프로세스 시작
Write-Host "ngrok을 시작합니다..."
Start-Process ngrok -ArgumentList "http --url=calm-remotely-longhorn.ngrok-free.app 5001" -WindowStyle Normal

# ngrok이 시작될 때까지 잠시 대기
Start-Sleep -Seconds 3

# 고정된 ngrok URL 설정
$ngrokUrl = "ws://calm-remotely-longhorn.ngrok-free.app"
Write-Host "ngrok URL: $ngrokUrl"
# 환경 변수 설정
$env:WEBSOCKET_SERVER_URL = $ngrokUrl
Write-Host "환경 변수 WEBSOCKET_SERVER_URL이 설정되었습니다."

# WebSocket 서버 시작
Write-Host "`nWebSocket 서버를 시작합니다..."
python src/websocket/server.py 