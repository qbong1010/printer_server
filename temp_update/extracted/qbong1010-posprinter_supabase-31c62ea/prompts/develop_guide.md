# 🎯 목표
아래 명세에 따라 Python + PySide6로 실행되는 **Windows용 데스크탑 주문·프린터 통합 위젯**을 만들어줘.

---

## ✅ 핵심 목적
- 실시간 WebSocket 주문 수신
- GUI에 주문 내역 표시
- 자동으로 로컬 프린터에 영수증 출력 (ESC/POS 명령 또는 텍스트 출력)
- SQLite로 주문 로그 저장

---

## 💻 기술 스택
- Python 3.10 이상
- PySide6 (Qt GUI)
- websockets 또는 socketio-client (WebSocket 클라이언트)
- win32print (프린터 출력용 Windows API)
- sqlite3 (주문 로그 저장)
- pyinstaller (exe 생성 예정)

---

## 🧱 기능 사양

### 1. WebSocket 주문 수신
- 서버에서 실시간 주문 JSON을 수신.
- WebSocket 주소는 추후 `.env`에서 불러오는 형태로 작성해줘.
- 수신 메시지 예시:
```json
{"order_id":"21","customer_name":"미래새한감정평가법인","items":[{"name":"아토키토 포케","quantity":1,"price":10900,"options":["사우전 드레싱(기본)"]}],"payment_method":"현장결제"}