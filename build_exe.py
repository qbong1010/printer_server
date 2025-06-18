import os
import subprocess
import sys
from pathlib import Path

def build_executable():
    """PyInstaller를 사용하여 실행 파일을 생성합니다."""
    
    # 현재 디렉토리
    current_dir = Path.cwd()
    
    # PyInstaller 명령어 구성
    cmd = [
        "pyinstaller",
        "--onefile",  # 단일 실행 파일로 생성
        "--windowed",  # 콘솔 창 숨김
        "--name=POSPrinter",  # 실행 파일 이름
        "--icon=signature.png",  # 아이콘 설정 (있는 경우)
        "--add-data=src;src",  # src 폴더 포함
        "--add-data=printer_config.json;.",  # 설정 파일 포함
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=websockets",
        "--hidden-import=requests",
        "--hidden-import=python_escpos",
        "--hidden-import=psutil",
        "--hidden-import=pyusb",
        "--hidden-import=serial",
        "main.py"
    ]
    
    print("실행 파일 생성 중...")
    print(f"명령어: {' '.join(cmd)}")
    
    try:
        # PyInstaller 실행
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 실행 파일 생성 완료!")
        print(f"생성된 파일: {current_dir / 'dist' / 'POSPrinter.exe'}")
        
        # 배포 폴더 생성
        deploy_dir = current_dir / "deploy"
        deploy_dir.mkdir(exist_ok=True)
        
        # 필요한 파일들을 배포 폴더로 복사
        import shutil
        
        # 실행 파일 복사
        exe_path = current_dir / "dist" / "POSPrinter.exe"
        if exe_path.exists():
            shutil.copy2(exe_path, deploy_dir / "POSPrinter.exe")
        
        # 설정 파일 복사
        config_files = ["printer_config.json", ".env"]
        for config_file in config_files:
            if Path(config_file).exists():
                shutil.copy2(config_file, deploy_dir)
        
        # README 파일 생성
        create_deploy_readme(deploy_dir)
        
        print(f"✅ 배포 폴더 생성 완료: {deploy_dir}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 실행 파일 생성 실패: {e}")
        print(f"오류 출력: {e.stderr}")
        return False
    
    return True

def create_deploy_readme(deploy_dir):
    """배포용 README 파일을 생성합니다."""
    readme_content = """# POS 프린터 프로그램 배포 패키지

## 설치 방법

1. 이 폴더의 모든 파일을 포스PC의 원하는 위치에 복사합니다.
2. `.env` 파일을 편집하여 Supabase 설정을 입력합니다:
   ```
   SUPABASE_PROJECT_ID=your-project-id
   SUPABASE_API_KEY=your-api-key
   SUPABASE_URL=https://your-project-id.supabase.co
   DEFAULT_PRINTER_NAME=your-printer-name
   DEBUG=False
   ```
3. `POSPrinter.exe`를 더블클릭하여 프로그램을 실행합니다.

## 주의사항

- Windows 10 이상에서 실행됩니다.
- 프린터가 연결되어 있어야 합니다.
- 인터넷 연결이 필요합니다 (Supabase 연결용).

## 문제 해결

- 프로그램이 실행되지 않으면 관리자 권한으로 실행해보세요.
- 프린터 인식 문제가 있으면 `printer_config.json` 파일을 확인하세요.
- 로그 파일은 프로그램과 같은 폴더에 생성됩니다.
"""
    
    with open(deploy_dir / "README_설치방법.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)

if __name__ == "__main__":
    build_executable() 