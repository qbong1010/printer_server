-- POS 프린터 애플리케이션 로그 모니터링 쿼리 모음
-- Supabase 대시보드의 SQL Editor에서 사용하세요.

-- ===========================================
-- 1. 기본 로그 조회 쿼리들
-- ===========================================

-- 최근 100개 로그 조회 (모든 클라이언트)
SELECT 
    created_at,
    client_name,
    log_level,
    log_type,
    message,
    module_name,
    app_version
FROM public.app_logs 
ORDER BY created_at DESC 
LIMIT 100;

-- 특정 클라이언트의 최근 로그 조회
SELECT 
    created_at,
    log_level,
    log_type,
    message,
    error_details,
    module_name,
    function_name
FROM public.app_logs 
WHERE client_id = 'YOUR_CLIENT_ID_HERE'  -- 실제 클라이언트 ID로 변경
ORDER BY created_at DESC 
LIMIT 50;

-- 오늘 발생한 모든 로그
SELECT 
    created_at,
    client_name,
    log_level,
    log_type,
    message,
    module_name
FROM public.app_logs 
WHERE DATE(created_at) = CURRENT_DATE
ORDER BY created_at DESC;

-- ===========================================
-- 2. 오류 모니터링 쿼리들
-- ===========================================

-- 최근 24시간 내 모든 오류
SELECT 
    created_at,
    client_name,
    client_id,
    message,
    error_details,
    module_name,
    function_name,
    line_number
FROM public.app_logs 
WHERE log_level = 'ERROR' 
    AND created_at >= NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;

-- 오류 발생 빈도 (모듈별)
SELECT 
    module_name,
    COUNT(*) as error_count,
    MAX(created_at) as last_error_time
FROM public.app_logs 
WHERE log_level = 'ERROR'
    AND created_at >= NOW() - INTERVAL '7 days'
GROUP BY module_name
ORDER BY error_count DESC;

-- 클라이언트별 오류 현황
SELECT 
    client_name,
    client_id,
    COUNT(*) as error_count,
    MAX(created_at) as last_error_time
FROM public.app_logs 
WHERE log_level = 'ERROR'
    AND created_at >= NOW() - INTERVAL '24 hours'
GROUP BY client_name, client_id
ORDER BY error_count DESC;

-- ===========================================
-- 3. 애플리케이션 활동 모니터링
-- ===========================================

-- 클라이언트별 시작/종료 로그
SELECT 
    client_name,
    client_id,
    log_type,
    created_at,
    app_version,
    os_info
FROM public.app_logs 
WHERE log_type IN ('startup', 'shutdown')
    AND created_at >= NOW() - INTERVAL '24 hours'
ORDER BY client_name, created_at DESC;

-- 활성 클라이언트 현황 (최근 1시간 내 활동)
SELECT 
    client_name,
    client_id,
    app_version,
    os_info,
    MAX(created_at) as last_activity,
    COUNT(*) as log_count
FROM public.app_logs 
WHERE created_at >= NOW() - INTERVAL '1 hour'
GROUP BY client_name, client_id, app_version, os_info
ORDER BY last_activity DESC;

-- 클라이언트별 마지막 시작 시간
WITH last_startup AS (
    SELECT 
        client_id,
        client_name,
        MAX(created_at) as last_startup_time
    FROM public.app_logs 
    WHERE log_type = 'startup'
    GROUP BY client_id, client_name
)
SELECT 
    client_name,
    client_id,
    last_startup_time,
    CASE 
        WHEN last_startup_time >= NOW() - INTERVAL '1 hour' THEN '온라인'
        WHEN last_startup_time >= NOW() - INTERVAL '24 hours' THEN '최근 활동'
        ELSE '오프라인'
    END as status
FROM last_startup
ORDER BY last_startup_time DESC;

-- ===========================================
-- 4. 통계 및 요약 쿼리들
-- ===========================================

-- 일별 로그 통계 (최근 7일)
SELECT 
    DATE(created_at) as log_date,
    COUNT(*) as total_logs,
    COUNT(CASE WHEN log_level = 'ERROR' THEN 1 END) as errors,
    COUNT(CASE WHEN log_level = 'WARNING' THEN 1 END) as warnings,
    COUNT(CASE WHEN log_type = 'startup' THEN 1 END) as startups,
    COUNT(CASE WHEN log_type = 'shutdown' THEN 1 END) as shutdowns
FROM public.app_logs 
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY log_date DESC;

-- 시간대별 활동 패턴 (최근 24시간)
SELECT 
    EXTRACT(hour FROM created_at) as hour_of_day,
    COUNT(*) as log_count,
    COUNT(DISTINCT client_id) as active_clients
FROM public.app_logs 
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY EXTRACT(hour FROM created_at)
ORDER BY hour_of_day;

-- 로그 레벨별 분포
SELECT 
    log_level,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM public.app_logs 
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY log_level
ORDER BY count DESC;

-- ===========================================
-- 5. 성능 및 시스템 모니터링
-- ===========================================

-- 버전별 클라이언트 분포
SELECT 
    app_version,
    COUNT(DISTINCT client_id) as client_count,
    MAX(created_at) as last_seen
FROM public.app_logs 
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY app_version
ORDER BY client_count DESC;

-- OS별 클라이언트 분포
SELECT 
    os_info,
    COUNT(DISTINCT client_id) as client_count,
    MAX(created_at) as last_seen
FROM public.app_logs 
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY os_info
ORDER BY client_count DESC;

-- 가장 활발한 클라이언트 (로그 발생량 기준)
SELECT 
    client_name,
    client_id,
    COUNT(*) as log_count,
    MIN(created_at) as first_log,
    MAX(created_at) as last_log
FROM public.app_logs 
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY client_name, client_id
ORDER BY log_count DESC
LIMIT 10;

-- ===========================================
-- 6. 실시간 모니터링 (새로고침용)
-- ===========================================

-- 실시간 대시보드 (최근 5분)
SELECT 
    '최근 5분간 로그' as category,
    COUNT(*) as count
FROM public.app_logs 
WHERE created_at >= NOW() - INTERVAL '5 minutes'

UNION ALL

SELECT 
    '활성 클라이언트' as category,
    COUNT(DISTINCT client_id) as count
FROM public.app_logs 
WHERE created_at >= NOW() - INTERVAL '5 minutes'

UNION ALL

SELECT 
    '최근 5분간 오류' as category,
    COUNT(*) as count
FROM public.app_logs 
WHERE created_at >= NOW() - INTERVAL '5 minutes'
    AND log_level = 'ERROR';

-- 최근 발생한 중요 로그 (오류 + 시작/종료)
SELECT 
    created_at,
    client_name,
    log_level,
    log_type,
    message,
    CASE 
        WHEN log_level = 'ERROR' THEN '🚨'
        WHEN log_type = 'startup' THEN '🟢'
        WHEN log_type = 'shutdown' THEN '🔴'
        ELSE '📝'
    END as icon
FROM public.app_logs 
WHERE (log_level = 'ERROR' OR log_type IN ('startup', 'shutdown'))
    AND created_at >= NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC
LIMIT 20;

-- ===========================================
-- 7. 데이터 정리 쿼리들
-- ===========================================

-- 30일 이상 된 로그 개수 확인
SELECT COUNT(*) as old_logs_count
FROM public.app_logs 
WHERE created_at < NOW() - INTERVAL '30 days';

-- 30일 이상 된 로그 삭제 (주의: 실행 전 백업 권장)
-- DELETE FROM public.app_logs WHERE created_at < NOW() - INTERVAL '30 days';

-- 테이블 크기 및 로그 통계
SELECT 
    COUNT(*) as total_logs,
    COUNT(DISTINCT client_id) as unique_clients,
    MIN(created_at) as oldest_log,
    MAX(created_at) as newest_log,
    pg_size_pretty(pg_total_relation_size('public.app_logs')) as table_size
FROM public.app_logs; 