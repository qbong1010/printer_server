import os
import shutil
import subprocess
import sys
from pathlib import Path

def build_executable():
    """PyInstaller를 사용하여 실행 파일을 생성하고 배포 폴더를 구성합니다."""

    current_dir = Path(__file__).resolve().parent
    separator = ";" if os.name == "nt" else ":"
    
    icon_path = current_dir / "signature.png"
    main_path = current_dir / "main.py"

    # escpos 라이브러리 데이터 파일 경로 확인
    try:
        import escpos
        escpos_path = Path(escpos.__file__).parent
        escpos_data_files = [
            f"--add-data={escpos_path / 'capabilities.json'}{separator}escpos/.",
            f"--add-data={escpos_path / 'capabilities_win.json'}{separator}escpos/."
        ]
        # JSON 파일이 실제로 존재하는지 확인
        escpos_data_files = [f for f in escpos_data_files if Path(str(f).split(separator)[0].split('=')[1]).exists()]
    except:
        escpos_data_files = []

    # PyInstaller 명령 구성
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        f"--name=POSPrinter",
        f"--icon={icon_path}" if icon_path.exists() else "",
        f"--add-data=src{separator}src",
        f"--add-data=printer_config.json{separator}.",
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=websockets",
        "--hidden-import=requests",
        "--hidden-import=python_escpos",
        "--hidden-import=psutil",
        "--hidden-import=pyusb",
        "--hidden-import=serial",
        "--hidden-import=escpos",
        "--hidden-import=escpos.capabilities",
        str(main_path)
    ] + escpos_data_files
    # 빈 문자열 제거
    cmd = [c for c in cmd if c]

    print("⚙️ 실행 파일 생성 중...")
    print(f"명령어:\n  {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 실행 파일 생성 완료!")
    except subprocess.CalledProcessError as e:
        print("❌ 실행 파일 생성 실패")
        print(e.stderr)
        return False

    dist_exe_path = current_dir / "dist" / "POSPrinter.exe"
    if not dist_exe_path.exists():
        print("❌ 실행 파일이 생성되지 않았습니다.")
        return False

    # 배포 폴더 생성
    deploy_dir = current_dir / "deploy"
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()

    print("📁 배포 폴더 구성 중...")

    # 실행 파일 복사
    shutil.copy2(dist_exe_path, deploy_dir / "POSPrinter.exe")

    # 설정 파일 복사
    config_files = [
        "printer_config.json",
        # ".env",  # 보안 이슈로 기본 비포함. 필요시 주석 해제
    ]
    for file_name in config_files:
        src_path = current_dir / file_name
        if src_path.exists():
            shutil.copy2(src_path, deploy_dir / file_name)

    # README 생성
    create_deploy_readme(deploy_dir)

    print(f"📦 배포 완료: {deploy_dir}")
    try:
        os.startfile(deploy_dir)  # Windows 한정
    except Exception:
        pass

    return True

def create_deploy_readme(deploy_dir: Path):
    """배포 폴더에 README 파일을 생성합니다."""
    readme_content = """# POS Printer 배포 패키지

## 설치 및 실행 방법

1. **실행 파일**: `POSPrinter.exe`를 더블클릭하여 실행
2. **설정 파일**: `printer_config.json`에서 프린터 설정을 확인/수정

## 주의사항

- Windows 환경에서 실행됩니다
- 프린터 연결 상태를 확인하세요
- 방화벽 설정에서 프로그램 접근을 허용하세요

## 문제 해결

프로그램 실행에 문제가 있으면 다음을 확인하세요:
- 프린터 드라이버 설치 상태
- USB 연결 상태 (USB 프린터 사용 시)
- 네트워크 연결 상태 (네트워크 프린터 사용 시)

## 지원

문제가 지속되면 로그 파일을 확인하거나 개발자에게 문의하세요.
"""
    
    readme_path = deploy_dir / "README.txt"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"📝 README 파일 생성: {readme_path}")

if __name__ == "__main__":
    build_executable()
