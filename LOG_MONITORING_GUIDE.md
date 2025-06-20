# POS 프린터 실시간 로그 모니터링 시스템

클라이언트 PC에서 발생하는 로그를 실시간으로 Supabase에 전송하여 원격으로 모니터링할 수 있는 시스템입니다.

## 🚀 주요 기능

- **실시간 로그 전송**: 애플리케이션 시작/종료, 오류, 일반 로그를 실시간으로 Supabase에 전송
- **클라이언트 식별**: MAC 주소 기반으로 각 클라이언트를 고유하게 식별
- **오류 추적**: 스택 트레이스를 포함한 상세한 오류 정보 수집
- **성능 최적화**: 백그라운드 큐를 사용하여 애플리케이션 성능에 영향 없이 로그 전송
- **자동 복구**: 네트워크 문제 시 로컬 로깅으로 자동 전환

## 📋 설정 방법

### 1. Supabase에서 테이블 생성

Supabase 대시보드의 SQL Editor에서 다음 파일을 실행하세요:

```sql
-- create_log_table.sql 파일의 내용을 복사하여 실행
```

### 2. 환경 변수 설정

`.env` 파일에 Supabase 연결 정보가 설정되어 있는지 확인하세요:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PROJECT_ID=your-project-id
SUPABASE_API_KEY=your-api-key
```

### 3. 애플리케이션 실행

기존 애플리케이션을 실행하면 자동으로 로그 모니터링이 시작됩니다.

```bash
python main.py
```

## 📊 로그 모니터링

### Supabase에서 로그 확인

1. Supabase 대시보드 → Table Editor → `app_logs` 테이블 확인
2. SQL Editor에서 `monitoring_queries.sql`의 쿼리들을 사용

### 주요 로그 유형

| 로그 유형 | 설명 | 예시 |
|---------|------|------|
| `startup` | 애플리케이션 시작 | 프로그램 시작 시 |
| `shutdown` | 애플리케이션 종료 | 프로그램 종료 시 |
| `error` | 오류 발생 | 예외 발생 시 |
| `warning` | 경고 | 네트워크 연결 실패 등 |
| `info` | 일반 정보 | 주문 처리, 프린터 연결 등 |

### 실시간 모니터링 쿼리

```sql
-- 최근 5분간 활동 현황
SELECT 
    created_at,
    client_name,
    log_level,
    log_type,
    message
FROM public.app_logs 
WHERE created_at >= NOW() - INTERVAL '5 minutes'
ORDER BY created_at DESC;
```

## 🔧 고급 설정

### 로그 레벨 조정

더 많은 로그를 수집하려면 `main.py`에서 로그 레벨을 변경할 수 있습니다:

```python
# INFO 레벨 (기본값) - 일반적인 로그만
remote_log_manager.setup_remote_logging(log_level=logging.INFO)

# DEBUG 레벨 - 모든 디버그 로그 포함 (주의: 로그량이 많아짐)
remote_log_manager.setup_remote_logging(log_level=logging.DEBUG)
```

### 커스텀 로그 전송

특정 이벤트에 대해 수동으로 로그를 전송할 수 있습니다:

```python
# 예시: 프린터 연결 상태 로그
if remote_log_manager:
    remote_log_manager.send_custom_log(
        level="INFO",
        log_type="printer_status",
        message="프린터 연결 성공",
        module_name="printer_manager"
    )
```

## 📈 모니터링 대시보드

### 기본 모니터링 쿼리들

#### 1. 클라이언트 상태 확인
```sql
-- 활성 클라이언트 목록 (최근 1시간)
SELECT 
    client_name,
    client_id,
    app_version,
    MAX(created_at) as last_activity
FROM public.app_logs 
WHERE created_at >= NOW() - INTERVAL '1 hour'
GROUP BY client_name, client_id, app_version
ORDER BY last_activity DESC;
```

#### 2. 오류 현황 확인
```sql
-- 최근 24시간 오류 현황
SELECT 
    client_name,
    COUNT(*) as error_count,
    MAX(created_at) as last_error
FROM public.app_logs 
WHERE log_level = 'ERROR' 
    AND created_at >= NOW() - INTERVAL '24 hours'
GROUP BY client_name
ORDER BY error_count DESC;
```

#### 3. 애플리케이션 가동 현황
```sql
-- 시작/종료 로그 확인
SELECT 
    client_name,
    log_type,
    created_at,
    app_version
FROM public.app_logs 
WHERE log_type IN ('startup', 'shutdown')
    AND created_at >= NOW() - INTERVAL '24 hours'
ORDER BY client_name, created_at DESC;
```

## 🔍 트러블슈팅

### 로그가 전송되지 않는 경우

1. **네트워크 연결 확인**
   - 인터넷 연결 상태 확인
   - Supabase URL 접근 가능 여부 확인

2. **환경 변수 확인**
   ```bash
   # .env 파일 확인
   cat .env
   ```

3. **Supabase API 키 권한 확인**
   - 테이블 읽기/쓰기 권한이 있는지 확인
   - RLS(Row Level Security) 설정 확인

4. **로컬 로그 확인**
   ```bash
   # 애플리케이션 로그 확인
   tail -f app.log
   ```

### 성능 이슈

- 로그 전송은 백그라운드에서 처리되므로 애플리케이션 성능에 영향 없음
- 네트워크 문제 시 자동으로 로컬 로깅으로 전환
- 큐가 가득 찬 경우 오래된 로그를 자동으로 제거

### 데이터 용량 관리

```sql
-- 30일 이상 된 로그 자동 삭제 (선택사항)
DELETE FROM public.app_logs 
WHERE created_at < NOW() - INTERVAL '30 days';
```

## 📱 알림 설정 (선택사항)

Supabase의 Edge Functions를 사용하여 오류 발생 시 알림을 받을 수 있습니다:

1. **Discord/Slack 웹훅 설정**
2. **이메일 알림 설정**
3. **SMS 알림 설정**

## 🔒 보안 고려사항

- 로그에는 개인정보가 포함되지 않도록 주의
- API 키는 환경 변수로 관리
- 필요시 RLS(Row Level Security) 활성화
- 정기적인 로그 데이터 정리

## 📊 로그 데이터 구조

| 필드명 | 타입 | 설명 |
|--------|------|------|
| `log_id` | bigint | 로그 고유 ID |
| `client_id` | varchar | 클라이언트 고유 식별자 |
| `client_name` | varchar | 클라이언트 컴퓨터 이름 |
| `log_level` | varchar | 로그 레벨 (INFO, WARNING, ERROR) |
| `log_type` | varchar | 로그 유형 (startup, shutdown, error, etc.) |
| `message` | text | 로그 메시지 |
| `error_details` | text | 오류 상세 정보 (스택 트레이스) |
| `module_name` | varchar | 모듈명 |
| `function_name` | varchar | 함수명 |
| `line_number` | integer | 라인 번호 |
| `created_at` | timestamptz | 로그 생성 시간 |
| `app_version` | varchar | 애플리케이션 버전 |
| `os_info` | varchar | 운영체제 정보 |

## 🚀 향후 개선 사항

- [ ] 웹 기반 실시간 대시보드 구축
- [ ] 오류 발생 시 자동 알림 기능
- [ ] 로그 검색 및 필터링 기능 강화
- [ ] 성능 메트릭 수집 추가
- [ ] 로그 분석 및 리포트 기능

---

## 지원

문제가 발생하거나 추가 기능이 필요한 경우 개발팀에 문의해주세요. 