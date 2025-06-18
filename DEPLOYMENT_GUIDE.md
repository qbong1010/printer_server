# POS 프린터 프로그램 배포 가이드

## 개요
이 가이드는 POS 프린터 프로그램을 포스PC에 설치하고 매장근무자가 쉽게 사용할 수 있도록 하는 방법을 설명합니다.

## 배포 방법

### 방법 1: 실행 파일 배포 (추천)

#### 1단계: 실행 파일 생성
개발 환경에서 다음 명령어를 실행합니다:

```powershell
# 가상환경 활성화 (있는 경우)
.\venv\Scripts\Activate.ps1

# 실행 파일 생성
python build_exe.py
```

#### 2단계: 배포 패키지 준비
생성된 `deploy` 폴더에는 다음 파일들이 포함됩니다:
- `POSPrinter.exe` - 메인 실행 파일
- `printer_config.json` - 프린터 설정 파일
- `.env` - 환경 변수 설정 파일 (편집 필요)
- `README_설치방법.txt` - 설치 가이드

#### 3단계: 포스PC 설치
포스PC에서 다음 중 하나의 방법을 선택합니다:

**자동 설치 (권장):**
```powershell
# PowerShell을 관리자 권한으로 실행
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\installer.ps1
```

**수동 설치:**
1. `deploy` 폴더의 모든 파일을 `C:\POSPrinter`에 복사
2. `.env` 파일을 편집하여 Supabase 설정 입력
3. `POSPrinter.exe`를 더블클릭하여 실행

### 방법 2: MSI 설치 패키지 (고급)

WiX Toolset을 사용하여 MSI 설치 패키지를 생성할 수 있습니다:

```powershell
# WiX Toolset 설치 후
candle POSPrinter.wxs
light POSPrinter.wixobj
```

## 포스PC 요구사항

### 최소 시스템 요구사항
- **OS**: Windows 10 (버전 1903 이상)
- **CPU**: Intel Core i3 또는 AMD 동급
- **RAM**: 4GB 이상
- **저장공간**: 500MB 이상
- **네트워크**: 인터넷 연결 (Supabase 연결용)

### 권장 시스템 요구사항
- **OS**: Windows 11
- **CPU**: Intel Core i5 또는 AMD 동급
- **RAM**: 8GB 이상
- **저장공간**: 1GB 이상
- **디스플레이**: 1920x1080 이상

## 설치 전 준비사항

### 1. 프린터 설정
- ESC/POS 호환 프린터가 연결되어 있어야 함
- 프린터 드라이버가 설치되어 있어야 함
- USB 또는 네트워크 연결 확인

### 2. 네트워크 설정
- Supabase 서버에 접근 가능한지 확인
- 방화벽에서 필요한 포트 허용 (443, 80)

### 3. 권한 설정
- 프로그램 실행을 위한 관리자 권한
- 프린터 접근 권한
- 파일 시스템 쓰기 권한

## 설치 후 설정

### 1. 환경 변수 설정
`.env` 파일을 편집하여 다음 정보를 입력:

```env
SUPABASE_PROJECT_ID=your-project-id
SUPABASE_API_KEY=your-api-key
SUPABASE_URL=https://your-project-id.supabase.co
DEFAULT_PRINTER_NAME=your-printer-name
DEBUG=False
CACHE_DB_PATH=cache.db
APP_LOG_PATH=app.log
```

### 2. 프린터 설정
`printer_config.json` 파일을 확인하고 필요시 수정:

```json
{
    "printer_type": "usb",
    "printer_name": "POS-58",
    "paper_width": 58,
    "encoding": "cp949"
}
```

### 3. 자동 시작 설정 (선택사항)
Windows 시작 프로그램에 등록:

```powershell
# 레지스트리에 등록
$StartupPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
Set-ItemProperty -Path $StartupPath -Name "POSPrinter" -Value "C:\POSPrinter\POSPrinter.exe"
```

## 사용자 교육

### 매장근무자를 위한 간단한 사용법

1. **프로그램 시작**
   - 바탕화면의 "POS 프린터" 아이콘 더블클릭
   - 또는 시작 메뉴 > 프로그램 > POS 프린터

2. **주문 확인**
   - 새 주문이 들어오면 자동으로 화면에 표시
   - 주문 목록에서 주문 상태 확인

3. **영수증 출력**
   - 주문이 들어오면 자동으로 영수증 출력
   - 수동 출력이 필요한 경우 "출력" 버튼 클릭

4. **프로그램 종료**
   - 창의 X 버튼 클릭
   - 또는 Alt+F4

### 문제 해결

#### 프로그램이 실행되지 않는 경우
1. 관리자 권한으로 실행
2. Windows Defender 예외 설정
3. .NET Framework 설치 확인

#### 프린터가 인식되지 않는 경우
1. 프린터 연결 상태 확인
2. 프린터 드라이버 재설치
3. `printer_config.json` 파일 확인

#### 주문이 수신되지 않는 경우
1. 인터넷 연결 확인
2. Supabase 설정 확인
3. 로그 파일 확인 (`app.log`)

## 유지보수

### 로그 파일 관리
- `app.log`: 애플리케이션 로그
- `printer_debug.log`: 프린터 디버그 로그
- `server.log`: 서버 연결 로그

### 정기 점검 항목
1. 로그 파일 크기 확인 (100MB 이상 시 정리)
2. 데이터베이스 파일 백업
3. 프린터 연결 상태 확인
4. 네트워크 연결 상태 확인

### 업데이트 방법
1. 새 버전의 `POSPrinter.exe` 다운로드
2. 기존 파일 백업
3. 새 파일로 교체
4. 프로그램 재시작

## 보안 고려사항

### 파일 권한
- 프로그램 폴더에 대한 읽기/쓰기 권한 제한
- 로그 파일 접근 권한 관리

### 네트워크 보안
- Supabase API 키 보안 유지
- 방화벽 설정으로 불필요한 포트 차단

### 데이터 보안
- 주문 데이터 암호화 저장
- 정기적인 데이터 백업

## 지원 및 문의

### 기술 지원
- 로그 파일 수집: `app.log`, `printer_debug.log`
- 시스템 정보: Windows 버전, 프린터 모델
- 오류 메시지 스크린샷

### 연락처
- 개발팀: [연락처 정보]
- 긴급 지원: [긴급 연락처]

---

**참고**: 이 가이드는 Windows 환경을 기준으로 작성되었습니다. 다른 운영체제에서는 다른 설치 방법이 필요할 수 있습니다. 