# POS 프린터 프로그램 설치 및 사용 가이드

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

## 🔄 자동 업데이트

### 업데이트 확인
프로그램은 자동으로 GitHub에서 업데이트를 확인합니다.
업데이트가 있으면 알림이 표시됩니다.

### 수동 업데이트
1. 업데이트 파일을 다운로드합니다
2. 현재 프로그램을 종료합니다
3. 새로운 파일을 설치 폴더에 덮어씁니다:
   ```
   C:\Program Files\POS_Printer
   ```

## 🆘 문제 해결

### 일반적인 문제들

#### 1. 프로그램이 실행되지 않는 경우
- `.env` 파일의 Supabase 설정이 올바른지 확인하세요
- 로그 파일 확인: `C:\Program Files\POS_Printer\app.log`

#### 2. 프린터가 작동하지 않는 경우
- 프린터 전원 및 연결 상태 확인
- `printer_config.json` 설정 확인
- 프린터 테스트 스크립트 실행

#### 3. Supabase 연결 오류
- 인터넷 연결 상태 확인
- Supabase URL과 API 키가 올바른지 확인
- 방화벽 설정 확인

### 로그 파일 위치
- 애플리케이션 로그: `C:\Program Files\POS_Printer\app.log`
- 프린터 디버그 로그: `C:\Program Files\POS_Printer\printer_debug.log`

## 📞 지원 및 문의

문제가 발생하거나 도움이 필요한 경우:
1. 로그 파일을 확인하세요
2. GitHub Issues에 문제를 보고하세요
3. 관리자에게 문의하세요

---

**주의사항**: 이 프로그램은 상업용 목적으로 사용됩니다. 설정 변경 시 주의하시고, 정기적으로 백업을 유지하세요. $$