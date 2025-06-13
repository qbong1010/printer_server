# 주문·프린터 통합 위젯

Windows용 데스크탑 주문 관리 및 프린터 통합 위젯입니다.

## 주요 기능

- Supabase를 이용한 주문 수신
- GUI에 주문 내역 표시
- 자동 영수증 출력
- SQLite 주문 로그 저장

## 시스템 요구사항

- Windows 10 이상
- Python 3.10 이상
- 로컬 프린터 연결

## 설치 방법

1. 의존성 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 환경 변수 설정:
`.env` 파일을 생성하고 다음 내용을 추가합니다:
```
SUPABASE_PROJECT_ID=your-project-id
SUPABASE_API_KEY=your-api-key
SUPABASE_URL=https://your-project-id.supabase.co
DEFAULT_PRINTER_NAME=your-printer-name
DEBUG=True
```

## 실행 방법

```bash
python main.py
```

## 프로젝트 구조

```
printer_server_websocket/
├── requirements.txt        # 의존성 패키지 목록
├── .env                   # 환경 변수 설정
├── main.py               # 메인 실행 파일
├── src/
│   ├── gui/              # GUI 관련 코드
│   ├── websocket/        # WebSocket 클라이언트
│   ├── printer/          # 프린터 관련 코드
│   └── database/         # SQLite 데이터베이스 관련
└── README.md             # 프로젝트 설명
```

## 주문 데이터 형식

```json
{
    "order_id": "21",
    "customer_name": "고객명",
    "items": [
        {
            "name": "상품명",
            "quantity": 1,
            "price": 10900,
            "options": ["옵션1", "옵션2"]
        }
    ],
    "payment_method": "현장결제"
}
``` 