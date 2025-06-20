# 🚨 Supabase 실시간 에러 로깅 시스템 가이드

## 📋 목차
1. [시스템 개요](#시스템-개요)
2. [현재 에러 핸들링 현황](#현재-에러-핸들링-현황)
3. [Supabase 실시간 로깅 구현](#supabase-실시간-로깅-구현)
4. [사용법](#사용법)
5. [테스트 방법](#테스트-방법)
6. [모니터링 및 관리](#모니터링-및-관리)

## 🎯 시스템 개요

이 프로젝트에는 **실시간 에러 모니터링 시스템**이 구현되어 있습니다. 모든 중요한 에러와 경고가 자동으로 Supabase 데이터베이스로 전송되어 실시간 모니터링이 가능합니다.

### 🔑 주요 기능
- **실시간 에러 전송**: 백그라운드 스레드로 비동기 전송
- **클라이언트별 추적**: 각 PC마다 고유 ID로 구분
- **에러 분류**: 프린터, 데이터베이스, 네트워크, GUI 등 카테고리별 분류
- **상세 정보**: 에러 발생 위치, 시간, 시스템 정보 등 포함
- **장애 복구**: Supabase 연결 실패 시에도 로컬 로그는 정상 동작

## 📊 현재 에러 핸들링 현황

### ✅ 에러 핸들링이 구현된 영역

| 모듈 | 파일 위치 | 에러 처리 내용 | Supabase 로깅 |
|------|-----------|---------------|---------------|
| **메인 애플리케이션** | `main.py` | 앱 시작/종료 에러 | ✅ |
| **Supabase 통신** | `src/supabase_client.py` | API 호출 실패 | ✅ |
| **데이터베이스** | `src/database/cache.py` | SQLite 연결/쿼리 에러 | ✅ |
| **프린터 관리** | `src/printer/manager.py` | 프린터 설정/출력 에러 | ✅ |
| **USB 프린터** | `src/printer/escpos_printer.py` | USB 통신 에러 | ⚠️ |
| **네트워크 프린터** | `src/printer/network_printer.py` | 네트워크 연결 에러 | ⚠️ |
| **COM 프린터** | `src/printer/com_printer.py` | 시리얼 통신 에러 | ⚠️ |
| **GUI 주문** | `src/gui/order_widget.py` | 주문 처리 에러 | ✅ |
| **GUI 프린터** | `src/gui/printer_widget.py` | 프린터 설정 에러 | ⚠️ |
| **자동 업데이터** | `src/updater.py` | 업데이트 에러 | ⚠️ |

**범례:**
- ✅ = Supabase 에러 로깅 구현 완료
- ⚠️ = 기본 로깅만 구현 (Supabase 로깅 추가 권장)

### 📝 로깅 파일 현황

| 로그 파일 | 용도 | 형식 |
|-----------|------|------|
| `app.log` | 메인 애플리케이션 로그 | 콘솔 + 파일 |
| `update.log` | 자동 업데이트 로그 | 파일 |
| `printer_debug.log` | 프린터 디버그 로그 | 파일 |

## 🚀 Supabase 실시간 로깅 구현

### 📁 새로 추가된 파일

#### `src/error_logger.py`
실시간 에러 로깅의 핵심 모듈:

```python
# 사용 예시
from src.error_logger import initialize_error_logger, get_error_logger

# 초기화 (main.py에서)
error_logger = initialize_error_logger(
    supabase_url=supabase_url,
    supabase_api_key=supabase_api_key,
    app_version="1.0.0"
)

# 에러 로깅 (어디서든)
error_logger = get_error_logger()
if error_logger:
    error_logger.log_printer_error("escpos", exception, "ORDER-123")
```

### 🗄️ Supabase 테이블 구조

```sql
TABLE public.app_logs (
  log_id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  client_id text NOT NULL,              -- 클라이언트 고유 ID
  client_name text,                     -- 클라이언트 이름 (예: POS-STORE01)
  log_level text NOT NULL,              -- INFO, WARNING, ERROR, CRITICAL
  log_type text NOT NULL,               -- PRINTER, DATABASE, NETWORK, GUI, ERROR
  message text NOT NULL,                -- 에러 메시지
  error_details text,                   -- 상세 스택 트레이스
  module_name text,                     -- 에러 발생 모듈
  function_name text,                   -- 에러 발생 함수
  line_number integer,                  -- 에러 발생 라인
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  app_version text,                     -- 앱 버전
  os_info text,                         -- 운영체제 정보
  CONSTRAINT app_logs_pkey PRIMARY KEY (log_id)
);
```

### 🔧 클라이언트 ID 생성 방식

```python
# 고유 클라이언트 ID 자동 생성
client_id = f"{hostname}-{username}-{mac_address[:8]}"
# 예: STORE01-admin-1a2b3c4d
```

## 📚 사용법

### 1. 기본 설정

`.env` 파일에 Supabase 정보 설정:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_API_KEY=your-api-key
```

### 2. 자동 에러 로깅

시스템이 자동으로 다음 에러들을 Supabase에 전송합니다:

- **프린터 에러**: 출력 실패, 연결 오류 등
- **데이터베이스 에러**: SQLite 연결/쿼리 실패
- **네트워크 에러**: Supabase API 호출 실패
- **GUI 에러**: 주문 처리 중 예외
- **시스템 에러**: 앱 시작/종료 시 치명적 오류

### 3. 수동 에러 로깅

코드에서 직접 에러를 로깅하려면:

```python
from src.error_logger import get_error_logger

# 일반 에러
error_logger = get_error_logger()
if error_logger:
    error_logger.log_error(exception, "상황 설명", {"추가": "데이터"})

# 프린터 에러
error_logger.log_printer_error("escpos", exception, "ORDER-123")

# 데이터베이스 에러
error_logger.log_database_error("insert", exception, "orders")

# 네트워크 에러
error_logger.log_network_error("https://api.example.com", exception, "POST")
```

### 4. 로그 레벨 설정

```python
# WARNING 이상만 Supabase로 전송 (기본값)
supabase_handler.setLevel(logging.WARNING)

# ERROR 이상만 전송하려면
supabase_handler.setLevel(logging.ERROR)
```

## 🧪 테스트 방법

### 1. 테스트 스크립트 실행

```bash
python test_error_logging.py
```

이 스크립트는 다음을 테스트합니다:
- Supabase 연결
- 다양한 타입의 에러 로그 전송
- 시스템 정보 로깅

### 2. 수동 테스트

1. **프린터 에러 테스트**: 잘못된 프린터 설정으로 출력 시도
2. **네트워크 에러 테스트**: 인터넷 연결 끊고 주문 동기화
3. **데이터베이스 에러 테스트**: 데이터베이스 파일 권한 변경

### 3. Supabase 대시보드 확인

1. Supabase 프로젝트 대시보드 접속
2. `app_logs` 테이블 확인
3. 실시간으로 들어오는 로그 모니터링

## 📈 모니터링 및 관리

### 🔍 Supabase에서 에러 조회

```sql
-- 최근 에러 조회
SELECT * FROM app_logs 
WHERE log_level IN ('ERROR', 'CRITICAL')
ORDER BY created_at DESC
LIMIT 50;

-- 클라이언트별 에러 통계
SELECT client_name, log_type, COUNT(*) as error_count
FROM app_logs 
WHERE log_level = 'ERROR'
AND created_at >= NOW() - INTERVAL '24 hours'
GROUP BY client_name, log_type
ORDER BY error_count DESC;

-- 특정 프린터 에러 조회
SELECT * FROM app_logs 
WHERE log_type = 'PRINTER'
AND message LIKE '%USB%'
ORDER BY created_at DESC;
```

### 📊 대시보드 구성 예시

1. **실시간 에러 알림**: ERROR 레벨 로그 발생 시 즉시 알림
2. **에러 통계**: 일일/주간 에러 발생 추이
3. **클라이언트 상태**: 각 매장별 에러 발생 현황
4. **프린터 상태**: 프린터별 에러 빈도

### 🔧 유지보수 가이드

#### 로그 정리 (월 1회 권장)
```sql
-- 30일 이상 된 INFO 로그 삭제
DELETE FROM app_logs 
WHERE log_level = 'INFO' 
AND created_at < NOW() - INTERVAL '30 days';

-- 90일 이상 된 WARNING 로그 삭제
DELETE FROM app_logs 
WHERE log_level = 'WARNING' 
AND created_at < NOW() - INTERVAL '90 days';
```

#### 성능 최적화
```sql
-- 인덱스 생성 (필요시)
CREATE INDEX idx_app_logs_client_created ON app_logs(client_id, created_at);
CREATE INDEX idx_app_logs_level_type ON app_logs(log_level, log_type);
```

## 🚨 장애 대응

### Supabase 연결 실패 시
- 로컬 로그 파일은 정상 동작 계속
- 백그라운드에서 자동 재연결 시도
- 네트워크 복구 시 자동으로 로깅 재개

### 대용량 로그 발생 시
- 큐 시스템으로 메모리 사용량 제한
- 전송 실패 시 자동 재시도 (최대 3회)
- 타임아웃 설정으로 블로킹 방지

## 📞 문제 해결

### 자주 발생하는 문제

1. **"Supabase 로그 전송 실패"**
   - `.env` 파일의 SUPABASE_URL, SUPABASE_API_KEY 확인
   - 네트워크 연결 상태 확인
   - Supabase 프로젝트 활성화 상태 확인

2. **"클라이언트 ID 생성 실패"**
   - Windows 사용자 권한 확인
   - MAC 주소 읽기 권한 확인

3. **"로그가 Supabase에 나타나지 않음"**
   - 로그 레벨 설정 확인 (WARNING 이상만 전송)
   - 백그라운드 스레드 동작 확인
   - 5초 정도 대기 후 확인

---

## 📝 업데이트 내역

- **v1.0.0**: 기본 에러 로깅 시스템 구현
- **v1.1.0**: Supabase 실시간 로깅 추가
- **v1.2.0**: 클라이언트별 추적 기능 추가
- **v1.3.0**: 에러 분류 및 상세 정보 개선

> 💡 **팁**: 정기적으로 Supabase 대시보드를 확인하여 반복되는 에러 패턴을 파악하고 사전 대응하세요! 