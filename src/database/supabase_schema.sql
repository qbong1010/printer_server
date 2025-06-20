-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.company (
  company_id integer NOT NULL DEFAULT nextval('company_company_id_seq'::regclass),
  company_name character varying NOT NULL,
  required_signature boolean DEFAULT false,
  CONSTRAINT company_pkey PRIMARY KEY (company_id)
);
CREATE TABLE public.menu_category (
  menu_category_id integer NOT NULL DEFAULT nextval('menu_category_menu_category_id_seq'::regclass),
  category_name character varying NOT NULL,
  indv_select_yn boolean DEFAULT true,
  CONSTRAINT menu_category_pkey PRIMARY KEY (menu_category_id)
);
CREATE TABLE public.menu_item (
  menu_item_id integer NOT NULL DEFAULT nextval('menu_item_menu_item_id_seq'::regclass),
  menu_name character varying NOT NULL,
  menu_price integer NOT NULL,
  menu_description text,
  menu_category_id integer NOT NULL,
  is_available boolean,
  menu_image_url character varying,
  CONSTRAINT menu_item_pkey PRIMARY KEY (menu_item_id),
  CONSTRAINT menu_item_menu_category_id_fkey FOREIGN KEY (menu_category_id) REFERENCES public.menu_category(menu_category_id)
);
CREATE TABLE public.menu_item_option_group (
  menu_item_id integer NOT NULL,
  option_group_id integer NOT NULL,
  is_required boolean DEFAULT false,
  display_order integer,
  CONSTRAINT menu_item_option_group_pkey PRIMARY KEY (menu_item_id, option_group_id),
  CONSTRAINT menu_item_option_group_menu_item_id_fkey FOREIGN KEY (menu_item_id) REFERENCES public.menu_item(menu_item_id),
  CONSTRAINT menu_item_option_group_option_group_id_fkey FOREIGN KEY (option_group_id) REFERENCES public.option_group(option_group_id)
);
CREATE TABLE public.option_group (
  option_group_id integer NOT NULL DEFAULT nextval('option_group_option_group_id_seq'::regclass),
  option_group_name text NOT NULL,
  allow_multiple boolean DEFAULT false,
  memo text,
  CONSTRAINT option_group_pkey PRIMARY KEY (option_group_id)
);
CREATE TABLE public.option_group_item (
  option_group_id integer NOT NULL,
  option_item_id integer NOT NULL,
  CONSTRAINT option_group_item_option_item_id_fkey FOREIGN KEY (option_item_id) REFERENCES public.option_item(option_item_id),
  CONSTRAINT option_group_item_option_group_id_fkey FOREIGN KEY (option_group_id) REFERENCES public.option_group(option_group_id)
);
CREATE TABLE public.option_item (
  option_item_id integer NOT NULL DEFAULT nextval('option_item_option_item_id_seq'::regclass),
  option_item_name text NOT NULL,
  option_price integer DEFAULT 0,
  memo text,
  CONSTRAINT option_item_pkey PRIMARY KEY (option_item_id)
);
CREATE TABLE public.order (
  order_id integer NOT NULL DEFAULT nextval('order_order_id_seq'::regclass),
  company_id integer NOT NULL,
  is_dine_in boolean DEFAULT true,
  total_price integer DEFAULT 0,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  is_printed boolean DEFAULT false,
  signature_data text,
  CONSTRAINT order_pkey PRIMARY KEY (order_id),
  CONSTRAINT order_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.company(company_id)
);
CREATE TABLE public.order_item (
  order_item_id integer NOT NULL DEFAULT nextval('order_item_order_item_id_seq'::regclass),
  order_id integer NOT NULL,
  menu_item_id integer NOT NULL,
  quantity integer DEFAULT 1,
  item_price integer NOT NULL,
  CONSTRAINT order_item_pkey PRIMARY KEY (order_item_id),
  CONSTRAINT order_item_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.order(order_id),
  CONSTRAINT order_item_menu_item_id_fkey FOREIGN KEY (menu_item_id) REFERENCES public.menu_item(menu_item_id)
);
CREATE TABLE public.order_item_option (
  order_item_option_id integer NOT NULL DEFAULT nextval('order_item_option_order_item_option_id_seq'::regclass),
  order_item_id integer NOT NULL,
  option_item_id integer NOT NULL,
  CONSTRAINT order_item_option_pkey PRIMARY KEY (order_item_option_id),
  CONSTRAINT order_item_option_order_item_id_fkey FOREIGN KEY (order_item_id) REFERENCES public.order_item(order_item_id),
  CONSTRAINT order_item_option_option_item_id_fkey FOREIGN KEY (option_item_id) REFERENCES public.option_item(option_item_id)
);

CREATE TABLE IF NOT EXISTS cache_meta (
  key text PRIMARY KEY,
  value text
);

-- 애플리케이션 로그 테이블 추가
CREATE TABLE public.app_logs (
  log_id bigint NOT NULL DEFAULT nextval('app_logs_log_id_seq'::regclass),
  client_id character varying NOT NULL,
  client_name character varying,
  log_level character varying NOT NULL,
  log_type character varying NOT NULL, -- 'startup', 'shutdown', 'error', 'info', 'warning'
  message text NOT NULL,
  error_details text,
  module_name character varying,
  function_name character varying,
  line_number integer,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  app_version character varying,
  os_info character varying,
  CONSTRAINT app_logs_pkey PRIMARY KEY (log_id)
);

-- 인덱스 추가 (성능 최적화)
CREATE INDEX idx_app_logs_client_id ON public.app_logs(client_id);
CREATE INDEX idx_app_logs_created_at ON public.app_logs(created_at);
CREATE INDEX idx_app_logs_log_level ON public.app_logs(log_level);
CREATE INDEX idx_app_logs_log_type ON public.app_logs(log_type);
