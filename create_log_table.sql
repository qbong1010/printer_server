-- POS 프린터 애플리케이션 로그 테이블 생성
-- Supabase 대시보드의 SQL Editor에서 실행하세요.

-- 로그 테이블 생성
CREATE TABLE IF NOT EXISTS public.app_logs (
    log_id bigserial PRIMARY KEY,
    client_id varchar(100) NOT NULL,
    client_name varchar(200),
    log_level varchar(20) NOT NULL,
    log_type varchar(50) NOT NULL,
    message text NOT NULL,
    error_details text,
    module_name varchar(100),
    function_name varchar(100),
    line_number integer,
    created_at timestamptz DEFAULT timezone('utc'::text, now()),
    app_version varchar(20),
    os_info varchar(200)
);

-- 성능 최적화를 위한 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_app_logs_client_id ON public.app_logs(client_id);
CREATE INDEX IF NOT EXISTS idx_app_logs_created_at ON public.app_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_app_logs_log_level ON public.app_logs(log_level);
CREATE INDEX IF NOT EXISTS idx_app_logs_log_type ON public.app_logs(log_type);
CREATE INDEX IF NOT EXISTS idx_app_logs_client_created ON public.app_logs(client_id, created_at DESC);

-- 테이블에 대한 코멘트 추가
COMMENT ON TABLE public.app_logs IS 'POS 프린터 클라이언트 애플리케이션 로그';
COMMENT ON COLUMN public.app_logs.client_id IS '클라이언트 고유 식별자 (MAC 주소 기반)';
COMMENT ON COLUMN public.app_logs.client_name IS '클라이언트 컴퓨터 이름';
COMMENT ON COLUMN public.app_logs.log_level IS '로그 레벨 (INFO, WARNING, ERROR 등)';
COMMENT ON COLUMN public.app_logs.log_type IS '로그 유형 (startup, shutdown, error, info, warning)';
COMMENT ON COLUMN public.app_logs.message IS '로그 메시지';
COMMENT ON COLUMN public.app_logs.error_details IS '오류 상세 정보 (스택 트레이스 등)';
COMMENT ON COLUMN public.app_logs.module_name IS '로그가 발생한 모듈명';
COMMENT ON COLUMN public.app_logs.function_name IS '로그가 발생한 함수명';
COMMENT ON COLUMN public.app_logs.line_number IS '로그가 발생한 라인 번호';
COMMENT ON COLUMN public.app_logs.app_version IS '애플리케이션 버전';
COMMENT ON COLUMN public.app_logs.os_info IS '운영체제 정보';

-- Row Level Security (RLS) 비활성화 (필요시 활성화)
-- ALTER TABLE public.app_logs ENABLE ROW LEVEL SECURITY;

-- 30일 이상 된 로그 자동 삭제를 위한 정책 (선택사항)
-- CREATE OR REPLACE FUNCTION delete_old_logs()
-- RETURNS void AS $$
-- BEGIN
--     DELETE FROM public.app_logs WHERE created_at < NOW() - INTERVAL '30 days';
-- END;
-- $$ LANGUAGE plpgsql;

-- 매일 자정에 오래된 로그 삭제 (pg_cron 확장이 필요)
-- SELECT cron.schedule('delete-old-logs', '0 0 * * *', 'SELECT delete_old_logs();');

-- 테이블 생성 확인
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE tablename = 'app_logs';

-- 생성된 인덱스 확인
SELECT 
    indexname,
    indexdef
FROM pg_indexes 
WHERE tablename = 'app_logs'; 