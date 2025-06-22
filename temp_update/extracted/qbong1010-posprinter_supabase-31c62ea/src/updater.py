import os
import json
import requests
import zipfile
import shutil
import logging
from pathlib import Path
from typing import Optional, Dict, Any

class AutoUpdater:
    def __init__(self, github_repo: str, current_version: str):
        """
        GitHub 자동 업데이트 시스템
        
        Args:
            github_repo: GitHub 저장소 (예: "username/repository")
            current_version: 현재 프로그램 버전
        """
        self.github_repo = github_repo
        self.current_version = current_version
        self.api_url = f"https://api.github.com/repos/{github_repo}"
        
        # 업데이트 로거 설정
        self.logger = logging.getLogger("updater")
        handler = logging.FileHandler("update.log", encoding="utf-8")
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def check_for_updates(self) -> Optional[Dict[str, Any]]:
        """
        GitHub에서 최신 릴리즈 확인
        
        Returns:
            최신 릴리즈 정보 또는 None (업데이트가 없는 경우)
        """
        try:
            self.logger.info("업데이트 확인 중...")
            response = requests.get(f"{self.api_url}/releases/latest", timeout=10)
            response.raise_for_status()
            
            latest_release = response.json()
            latest_version = latest_release["tag_name"].lstrip("v")
            
            self.logger.info(f"현재 버전: {self.current_version}")
            self.logger.info(f"최신 버전: {latest_version}")
            
            if self._is_newer_version(latest_version, self.current_version):
                self.logger.info("새로운 업데이트가 있습니다.")
                return latest_release
            else:
                self.logger.info("최신 버전을 사용 중입니다.")
                return None
                
        except requests.RequestException as e:
            self.logger.error(f"업데이트 확인 실패: {e}")
            return None
        except Exception as e:
            self.logger.error(f"업데이트 확인 중 오류 발생: {e}")
            return None
    
    def _is_newer_version(self, latest: str, current: str) -> bool:
        """버전 비교"""
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            
            # 길이 맞추기
            max_len = max(len(latest_parts), len(current_parts))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            current_parts.extend([0] * (max_len - len(current_parts)))
            
            return latest_parts > current_parts
        except:
            return False
    
    def download_update(self, release_info: Dict[str, Any]) -> Optional[str]:
        """
        업데이트 파일 다운로드
        
        Args:
            release_info: GitHub 릴리즈 정보
            
        Returns:
            다운로드된 파일 경로 또는 None
        """
        try:
            # ZIP 파일 에셋 찾기
            zip_asset = None
            for asset in release_info.get("assets", []):
                if asset["name"].endswith(".zip"):
                    zip_asset = asset
                    break
            
            if not zip_asset:
                # 소스 코드 ZIP 사용
                download_url = release_info["zipball_url"]
                filename = f"update_{release_info['tag_name']}.zip"
            else:
                download_url = zip_asset["browser_download_url"]
                filename = zip_asset["name"]
            
            self.logger.info(f"업데이트 다운로드 중: {download_url}")
            
            # 임시 디렉토리에 다운로드
            temp_dir = Path("temp_update")
            temp_dir.mkdir(exist_ok=True)
            download_path = temp_dir / filename
            
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.logger.info(f"다운로드 완료: {download_path}")
            return str(download_path)
            
        except Exception as e:
            self.logger.error(f"다운로드 실패: {e}")
            return None
    
    def apply_update(self, zip_path: str, backup: bool = True) -> bool:
        """
        업데이트 적용
        
        Args:
            zip_path: 다운로드된 ZIP 파일 경로
            backup: 백업 생성 여부
            
        Returns:
            성공 여부
        """
        try:
            current_dir = Path.cwd()
            temp_dir = Path("temp_update")
            backup_dir = Path("backup")
            
            # 백업 생성
            if backup:
                self.logger.info("현재 버전 백업 중...")
                if backup_dir.exists():
                    shutil.rmtree(backup_dir)
                backup_dir.mkdir()
                
                # 중요 파일들 백업
                important_files = ["main.py", "src", "requirements.txt", "printer_config.json"]
                for file_name in important_files:
                    file_path = current_dir / file_name
                    if file_path.exists():
                        if file_path.is_dir():
                            shutil.copytree(file_path, backup_dir / file_name)
                        else:
                            shutil.copy2(file_path, backup_dir / file_name)
            
            # ZIP 파일 압축 해제
            self.logger.info("업데이트 파일 압축 해제 중...")
            extract_dir = temp_dir / "extracted"
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            extract_dir.mkdir()
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # 압축 해제된 폴더 찾기
            extracted_contents = list(extract_dir.iterdir())
            if len(extracted_contents) == 1 and extracted_contents[0].is_dir():
                source_dir = extracted_contents[0]
            else:
                source_dir = extract_dir
            
            # 파일 업데이트
            self.logger.info("파일 업데이트 중...")
            update_files = ["main.py", "src", "requirements.txt"]
            
            for file_name in update_files:
                source_path = source_dir / file_name
                dest_path = current_dir / file_name
                
                if source_path.exists():
                    if dest_path.exists():
                        if dest_path.is_dir():
                            shutil.rmtree(dest_path)
                        else:
                            dest_path.unlink()
                    
                    if source_path.is_dir():
                        shutil.copytree(source_path, dest_path)
                    else:
                        shutil.copy2(source_path, dest_path)
                    
                    self.logger.info(f"업데이트됨: {file_name}")
            
            # 버전 정보 업데이트
            self._update_version_info()
            
            # 정리
            shutil.rmtree(temp_dir)
            
            self.logger.info("업데이트가 성공적으로 완료되었습니다.")
            return True
            
        except Exception as e:
            self.logger.error(f"업데이트 적용 실패: {e}")
            
            # 백업에서 복원 시도
            if backup and backup_dir.exists():
                try:
                    self.logger.info("백업에서 복원 중...")
                    self._restore_from_backup(backup_dir)
                except Exception as restore_error:
                    self.logger.error(f"백업 복원 실패: {restore_error}")
            
            return False
    
    def _restore_from_backup(self, backup_dir: Path):
        """백업에서 복원"""
        current_dir = Path.cwd()
        
        for item in backup_dir.iterdir():
            dest_path = current_dir / item.name
            
            if dest_path.exists():
                if dest_path.is_dir():
                    shutil.rmtree(dest_path)
                else:
                    dest_path.unlink()
            
            if item.is_dir():
                shutil.copytree(item, dest_path)
            else:
                shutil.copy2(item, dest_path)
    
    def _update_version_info(self):
        """버전 정보 파일 업데이트"""
        try:
            version_file = Path("version.json")
            version_info = {
                "version": self.current_version,
                "updated_at": str(Path("app.log").stat().st_mtime if Path("app.log").exists() else 0)
            }
            
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(version_info, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.warning(f"버전 정보 업데이트 실패: {e}")

def get_current_version() -> str:
    """현재 프로그램 버전 가져오기"""
    try:
        version_file = Path("version.json")
        if version_file.exists():
            with open(version_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("version", "1.0.0")
    except:
        pass
    
    return "1.0.0"

def check_and_update(github_repo: str, auto_apply: bool = False) -> bool:
    """
    업데이트 확인 및 적용
    
    Args:
        github_repo: GitHub 저장소
        auto_apply: 자동 적용 여부
        
    Returns:
        업데이트 적용 여부
    """
    current_version = get_current_version()
    updater = AutoUpdater(github_repo, current_version)
    
    # 업데이트 확인
    release_info = updater.check_for_updates()
    if not release_info:
        return False
    
    if not auto_apply:
        # 사용자 확인 필요
        print(f"새로운 업데이트가 있습니다: {release_info['tag_name']}")
        print(f"릴리즈 노트: {release_info.get('body', '없음')}")
        
        response = input("업데이트를 설치하시겠습니까? (y/N): ")
        if response.lower() not in ['y', 'yes', '예', 'ㅇ']:
            return False
    
    # 업데이트 다운로드 및 적용
    zip_path = updater.download_update(release_info)
    if not zip_path:
        return False
    
    return updater.apply_update(zip_path) 