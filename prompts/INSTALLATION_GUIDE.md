# POS 프린터 프로그램 설치 및 사용 가이드

## 📋 개요
이 프로그램은 Supabase와 연동하여 주문 정보를 실시간으로 받아 프린터로 출력하는 POS 시스템입니다.

## 📋 시스템 요구사항
- Windows 10 이상
- 최소 2GB 이상의 여유 공간
- 인터넷 연결 (설치 및 업데이트 시 필요)

## 🚀 설치 방법

### 1단계: 설치 파일 다운로드
1. GitHub 페이지에서 최신 버전을 다운로드하세요
2. ZIP 파일을 압축 해제하세요

### 2단계: 관리자 권한으로 설치 실행
1. Windows 검색에서 "PowerShell"을 입력하세요
2. "Windows PowerShell"을 **마우스 오른쪽 버튼**으로 클릭하세요
3. "**관리자 권한으로 실행**"을 선택하세요
4. 압축 해제한 폴더로 이동하세요:
   ```powershell
   cd "C:\Users\사용자명\Downloads\posprinter_supabase"
   ```
5. 설치 스크립트를 실행하세요:
   ```powershell
   .\installer.ps1
   ```

### 3단계: 설치 완료 확인
- 설치가 완료되면 바탕화면에 "POS 프린터" 바로가기가 생성됩니다
- 설치 위치: `C:\Program Files\POS_Printer`

## ⚙️ 설정 방법

### Supabase 설정 (필수)
1. 설치 폴더의 `.env` 파일을 메모장으로 열기:
   ```
   C:\Program Files\POS_Printer\.env
   ```

2. 다음 정보를 입력하세요:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_PROJECT_ID=your-project-id
   SUPABASE_API_KEY=your-api-key
   ```

### 프린터 설정
1. `printer_config.json` 파일을 메모장으로 열기:
   ```
   C:\Program Files\POS_Printer\printer_config.json
   ```

2. 프린터 유형에 따라 설정을 수정하세요:

#### USB 프린터의 경우:
```json
{
  "printer_type": "usb",
  "printer_name": "영수증프린터",
  "usb_info": {
    "vendor_id": "0525",
    "product_id": "A700",
    "interface": "0"
  }
}
```

#### 네트워크 프린터의 경우:
```json
{
  "printer_type": "network",
  "printer_name": "네트워크프린터",
  "network_info": {
    "address": "192.168.0.100",
    "port": "9100"
  }
}
```

## 🖨️ 프린터 정보 확인 방법

### USB 프린터 정보 확인
1. 설치 폴더의 `setup_utility` 폴더로 이동
2. `escpos_usbprinter_setup.py` 실행:
   ```powershell
   cd "C:\Program Files\POS_Printer\setup_utility"
   ..\venv\Scripts\python.exe escpos_usbprinter_setup.py
   ```

### 프린터 테스트
1. `test_printer.py` 실행하여 프린터가 정상 작동하는지 확인:
   ```powershell
   ..\venv\Scripts\python.exe test_printer.py
   ```

## 🎯 프로그램 사용법

### 기본 실행
- 바탕화면의 "POS 프린터" 바로가기를 더블클릭
- 또는 시작 메뉴에서 "POS 프린터" 검색하여 실행

### 주문 처리
1. 프로그램이 실행되면 자동으로 Supabase에서 주문 데이터를 가져옵니다
2. 새로운 주문이 있으면 자동으로 프린터에서 영수증이 출력됩니다
3. 수동으로 영수증을 출력하려면 "인쇄" 버튼을 클릭하세요

## 🔄 **자동 업데이트 기능**

### 1. **프로그램 내 업데이트 확인**
- 프로그램 실행 후 상단의 **"업데이트 확인"** 버튼 클릭
- 자동으로 GitHub에서 최신 버전 확인
- 새 버전이 있으면 설치 여부 선택 가능
- 업데이트 시 자동으로 백업 생성

### 2. **자동 업데이트 (24시간마다)**
- 프로그램 시작 시 자동으로 업데이트 확인
- 24시간마다 백그라운드에서 확인
- 환경변수 `UPDATE_CHECK_INTERVAL`로 주기 조정 가능

### 3. **수동 업데이트 스크립트**
매장에서 프로그램 없이 업데이트하려면:
```powershell
# PowerShell에서 실행
.\update.ps1
```

## 🛠️ 설치 방법

### 1. 시스템 요구사항
- Windows 10 이상
- Python 3.8+ (또는 실행 파일 사용)
- 인터넷 연결 (Supabase 연결 및 업데이트용)

### 2. 설치 과정

#### 방법 1: 실행 파일 사용 (권장)
1. 최신 릴리즈에서 `POSPrinter.exe` 다운로드
2. 프로그램을 원하는 폴더에 저장
3. 환경 설정 파일 `.env` 생성
4. 프린터 설정 파일 `printer_config.json` 설정

#### 방법 2: 소스 코드 설치
```powershell
# 1. 저장소 클론
git clone https://github.com/qbong1010/posprinter_supabase.git
cd posprinter_supabase

# 2. 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 프로그램 실행
python main.py
```

## ⚙️ 환경 설정

### 1. Supabase 설정 (`.env` 파일)
```env
SUPABASE_URL=your_supabase_url
SUPABASE_API_KEY=your_supabase_api_key
SUPABASE_PROJECT_ID=your_project_id
GITHUB_REPO=qbong1010/posprinter_supabase
UPDATE_CHECK_INTERVAL=24
```

### 2. 프린터 설정 (`printer_config.json`)
```json
{
  "printer_type": "escpos",
  "connection_type": "usb",
  "vendor_id": "0x04b8",
  "product_id": "0x0202",
  "com_port": "COM3",
  "baud_rate": 9600,
  "output_file": "output/receipt.txt",
  "print_on_receive": true,
  "auto_cut": true
}
```

## 🖨️ 지원 프린터 유형

1. **ESC/POS 프린터 (USB)**
   - 대부분의 영수증 프린터
   - USB 연결
   
2. **시리얼 프린터 (COM 포트)**
   - 오래된 프린터
   - RS-232 연결

3. **파일 출력**
   - 테스트용
   - 텍스트 파일로 저장

## 📱 사용 방법

### 1. 프로그램 시작
```powershell
# 실행 파일 사용
POSPrinter.exe

# 또는 소스 코드 실행
python main.py
```

### 2. 주요 기능
- **주문 관리**: 실시간 주문 수신 및 상태 관리
- **프린터 설정**: 프린터 연결 및 설정
- **영수증 미리보기**: 출력 내용 확인
- **업데이트 확인**: 최신 버전 확인 및 자동 업데이트

### 3. 자동 인쇄 설정
- `printer_config.json`에서 `print_on_receive: true` 설정
- 새 주문 수신 시 자동으로 인쇄

## 🔧 문제 해결

### 1. 업데이트 문제
- 인터넷 연결 확인
- GitHub 접속 가능 여부 확인
- 수동 업데이트 스크립트 `update.ps1` 실행

### 2. 프린터 연결 문제
- 프린터 드라이버 설치 확인
- USB 케이블 연결 상태 확인
- 다른 프로그램에서 프린터 사용 중인지 확인

### 3. Supabase 연결 문제
- `.env` 파일의 URL과 API 키 확인
- 인터넷 연결 상태 확인
- 프로젝트 권한 설정 확인

## 📞 지원

문제가 발생하면:
1. 로그 파일 `app.log` 확인
2. 오류 메시지 캡처
3. GitHub Issues에 문의

---

**자동 업데이트 기능으로 항상 최신 버전을 유지하세요!** 🚀