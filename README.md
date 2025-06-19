# POS 프린터 프로그램

Supabase와 연동하여 주문 데이터를 자동으로 프린터에서 출력하는 Windows용 프로그램입니다.

## 🚀 빠른 설치 (비개발자용)

### 1. 설치 파일 다운로드
- [최신 릴리즈](../../releases/latest)에서 `POS_Printer_vX.X.X.zip` 파일을 다운로드하세요
- ZIP 파일을 압축 해제하세요

### 2. 자동 설치
1. **PowerShell을 관리자 권한으로 실행**하세요
2. 압축 해제한 폴더로 이동하세요
3. 다음 명령을 실행하세요:
   ```powershell
   .\installer.ps1
   ```

### 3. 설정
설치 완료 후 바탕화면의 "POS 프린터" 바로가기를 실행하여 설정을 완료하세요.

자세한 설정 방법은 [설치 가이드](INSTALLATION_GUIDE.md)를 참조하세요.

## 📋 시스템 요구사항

- Windows 10 이상
- Python 3.8+ (자동 설치됨)
- 최소 2GB 여유 공간
- 인터넷 연결 (설치 및 업데이트 시)

## 🛠️ 개발자용 설정

### 개발 환경 설정
```powershell
# 저장소 클론
git clone https://github.com/your-username/posprinter_supabase.git
cd posprinter_supabase

# 가상환경 생성
python -m venv venv
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
copy .env.example .env
# .env 파일에서 Supabase 설정 입력

# 프로그램 실행
python main.py
```

### 설정 도구 실행
```powershell
python config_tool.py
```

## 🔄 자동 업데이트

이 프로그램은 GitHub를 통한 자동 업데이트를 지원합니다:

- 프로그램 실행 시 자동으로 업데이트 확인
- 새 버전이 있으면 알림 표시
- 한 번의 클릭으로 업데이트 적용

## 📁 주요 파일 구조

```
posprinter_supabase/
├── main.py                 # 메인 프로그램
├── config_tool.py          # 설정 도구
├── installer.ps1           # 설치 스크립트
├── INSTALLATION_GUIDE.md   # 설치 가이드
├── src/
│   ├── updater.py          # 자동 업데이트 시스템
│   ├── gui/                # GUI 관련 파일
│   ├── printer/            # 프린터 관련 파일
│   └── database/           # 데이터베이스 관련 파일
└── setup_utility/          # 설정 유틸리티
```

## 🖨️ 지원하는 프린터

- **기본 Windows 프린터**: 시스템에 설치된 모든 프린터
- **USB 프린터**: ESC/POS 호환 영수증 프린터
- **네트워크 프린터**: IP 주소를 통한 네트워크 프린터
- **파일 출력**: 테스트용 파일 출력

## 📞 지원 및 문의

### 문제 해결
1. [설치 가이드](INSTALLATION_GUIDE.md) 확인
2. 로그 파일 확인 (`app.log`, `printer_debug.log`)
3. [Issues](../../issues)에서 기존 문제 검색
4. 새로운 이슈 생성

### 기능 요청
- [Issues](../../issues)에서 기능 요청을 등록해주세요
- 가능한 한 자세한 설명과 사용 사례를 포함해주세요

## 📈 업데이트 로그

### v1.0.0 (2024-12-28)
- 초기 배포 버전
- Supabase 연동 기능
- 자동 프린터 출력
- GUI 설정 도구
- 자동 업데이트 시스템

## 🔐 라이선스

이 프로젝트는 상업적 사용을 위해 개발되었습니다. 
라이선스 관련 문의는 개발자에게 직접 연락해주세요.

## 👥 개발팀

- **메인 개발자**: [개발자명]
- **프로젝트 관리**: [관리자명]

---

**⚠️ 중요 알림**: 이 프로그램은 Windows 환경에서만 동작합니다. 설정 변경 시 주의하시고, 정기적으로 백업을 유지하세요. 