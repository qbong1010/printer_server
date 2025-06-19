$$# 배포 노트 및 가이드

## 📦 배포 과정

### 1. 배포 전 검증
```powershell
# 모든 검증 실행
.\test_deployment.ps1

# 테스트 스킵하고 파일만 검증
.\test_deployment.ps1 -SkipTests

# 상세 정보 포함
.\test_deployment.ps1 -Verbose
```

### 2. 수동 배포 (로컬)
```powershell
# 배포 패키지 생성
.\deployment_guide.ps1 -Version "1.0.0"

# ZIP 파일까지 생성
.\deployment_guide.ps1 -Version "1.0.0" -CreateInstaller
```

### 3. GitHub 자동 배포
1. 코드를 main 브랜치에 푸시
2. GitHub에서 새로운 릴리즈 생성
3. 태그 형식: `v1.0.0` (v 접두사 필수)
4. 릴리즈 제목: `POS 프린터 v1.0.0`
5. 릴리즈 설명에 변경사항 기록

### 4. 자동 빌드 프로세스
- GitHub Actions가 자동으로 실행됩니다
- Windows 환경에서 빌드됩니다
- 다음 파일들이 릴리즈에 첨부됩니다:
  - `POS_Printer_v1.0.0.zip` (전체 프로그램)
  - `INSTALLATION_GUIDE.md` (설치 가이드)

## 🔧 배포 설정

### GitHub 저장소 설정
1. **Settings > Actions > General**에서 Actions 허용
2. **Settings > Secrets**에서 `GITHUB_TOKEN` 확인 (자동 생성됨)

### 업데이트 설정
`main.py`의 GitHub 저장소 이름을 실제 저장소로 변경:
```python
github_repo = "your-username/posprinter_supabase"  # 실제 저장소 이름으로 변경
```

`config_tool.py`에서도 동일하게 변경:
```python
from src.updater import check_and_update
if check_and_update("your-username/posprinter_supabase"):  # 실제 저장소 이름으로 변경
```

## 📋 배포 체크리스트

### 배포 전 확인사항
- [ ] 모든 기능이 정상 작동하는지 테스트
- [ ] 프린터 연결 및 출력 테스트
- [ ] Supabase 연동 테스트
- [ ] 설정 도구 정상 작동 확인
- [ ] 에러 로그 확인
- [ ] 버전 정보 업데이트 (`version.json`)
- [ ] CHANGELOG 또는 릴리즈 노트 작성

### 필수 파일 확인
- [ ] `main.py` - 메인 프로그램
- [ ] `config_tool.py` - 설정 도구
- [ ] `installer.ps1` - 설치 스크립트
- [ ] `requirements.txt` - Python 의존성
- [ ] `INSTALLATION_GUIDE.md` - 사용자 가이드
- [ ] `version.json` - 버전 정보
- [ ] `src/updater.py` - 자동 업데이트 시스템
- [ ] `.github/workflows/release.yml` - GitHub Actions

### 배포 후 확인사항
- [ ] GitHub 릴리즈 페이지에서 파일 다운로드 가능한지 확인
- [ ] 설치 과정이 정상적으로 진행되는지 테스트
- [ ] 자동 업데이트 기능 테스트
- [ ] 사용자 피드백 모니터링

## ⚠️ 주의사항

### 버전 관리
- **태그 형식**: `v1.0.0` (v 접두사 필수)
- **Semantic Versioning** 사용 권장:
  - `1.0.0`: 주요 버전 (breaking changes)
  - `1.1.0`: 기능 추가 (backward compatible)
  - `1.0.1`: 버그 수정

### 보안 고려사항
- `.env` 파일에 실제 API 키를 포함하지 않습니다
- GitHub에 민감한 정보가 업로드되지 않도록 주의합니다
- 릴리즈에 포함되는 파일들을 신중히 선택합니다

### 사용자 경험
- 설치 과정이 복잡하지 않도록 합니다
- 오류 메시지는 사용자가 이해하기 쉽게 작성합니다
- 업데이트 과정에서 설정이 유지되도록 합니다

## 🔄 업데이트 프로세스

### 일반적인 업데이트
1. 코드 수정 및 테스트
2. 버전 번호 증가 (`version.json`)
3. 변경사항 기록
4. GitHub에 푸시
5. 새로운 릴리즈 생성

### 긴급 업데이트 (핫픽스)
1. 버그 수정
2. 패치 버전 증가 (예: 1.0.0 → 1.0.1)
3. 즉시 릴리즈

### 주요 기능 업데이트
1. 기능 개발 및 광범위한 테스트
2. 사용자 가이드 업데이트
3. 마이너 또는 메이저 버전 증가
4. 릴리즈 노트에 자세한 변경사항 기록

## 📊 배포 후 모니터링

### 로그 수집
- 사용자 설치 과정의 문제점 파악
- 실행 중 발생하는 오류 모니터링
- 업데이트 성공/실패율 추적

### 사용자 피드백
- GitHub Issues를 통한 버그 리포트 수집
- 기능 요청 관리
- FAQ 업데이트

### 성능 모니터링
- 프로그램 시작 시간
- 메모리 사용량
- 프린터 응답 시간

---

**배포 관련 문제가 발생하면 이 문서를 참조하여 해결하시고, 필요시 내용을 업데이트해주세요.** 