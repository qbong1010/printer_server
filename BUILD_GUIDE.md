# 🛠️ 초간단 빌드 가이드

이 문서는 Windows에서 프로그램 실행 파일(`.exe`)을 만드는 가장 쉬운 방법을 설명합니다. 컴퓨터 사용 경험이 많지 않아도 따라 할 수 있도록 단계별로 정리했습니다.

## 1. 필요한 준비물

- **Windows 10 이상 PC**
- **Python 3.9 이상** (미리 설치되어 있지 않다면 설치 스크립트가 자동으로 설치합니다)
- 인터넷 연결

## 2. 소스 코드 내려받기

1. GitHub 페이지에서 `Code` 버튼을 눌러 `Download ZIP`을 선택합니다.
2. 다운로드한 ZIP 파일의 압축을 풉니다. 예시 폴더: `C:\posprinter_supabase`

## 3. 필수 패키지 설치

1. 시작 메뉴에서 **PowerShell**을 찾아 **관리자 권한으로 실행**합니다.
2. 다음 명령을 입력하여 프로젝트 폴더로 이동합니다.
   ```powershell
   cd C:\posprinter_supabase
   ```
3. 필요한 파이썬 패키지를 설치합니다.
   ```powershell
   pip install -r requirements.txt
   ```

## 4. 실행 파일 만들기

1. 계속해서 PowerShell 창에 다음 명령을 입력합니다.
   ```powershell
   python build_exe.py
   ```
2. 명령이 끝나면 `deploy` 폴더가 생기고 그 안에 `POSPrinter.exe` 파일이 만들어집니다.
3. `deploy\POSPrinter.exe`를 더블클릭하면 프로그램이 실행됩니다.

## 5. 자주 묻는 질문

- **빌드 중 오류가 나요!**
  - Python이 3.9 이상인지 확인하세요.
  - `pip install -r requirements.txt` 명령이 제대로 실행되었는지 확인하세요.
- **exe 파일이 어디 있나요?**
  - 빌드가 성공하면 프로젝트 폴더 안에 `deploy`라는 새 폴더가 생깁니다. 그 안에서 `POSPrinter.exe`를 찾을 수 있습니다.

## 6. 더 알아보기

- 고급 배포 방법이나 GitHub Actions 자동 빌드에 대해서는 `DEPLOYMENT_NOTES.md` 파일을 참고하세요.

이상으로 간단한 빌드 과정을 마쳤습니다. 실수해도 걱정하지 말고 천천히 다시 시도해 보세요!
