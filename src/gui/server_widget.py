from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QGroupBox)
from PySide6.QtCore import Qt, Signal
import subprocess
import psutil
import requests
import os

class ServerWidget(QWidget):
    server_status_changed = Signal(bool)
    ngrok_status_changed = Signal(bool)
    
    def __init__(self):
        super().__init__()
        self.ws_port = int(os.getenv('WEBSOCKET_SERVER_PORT', '5001'))
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 서버 상태 그룹
        server_group = QGroupBox("서버 상태")
        server_layout = QVBoxLayout()
        
        # 웹소켓 서버 상태
        ws_status_layout = QHBoxLayout()
        self.ws_status_label = QLabel("웹소켓 서버: 비활성")
        self.ws_restart_btn = QPushButton("서버 재시작")
        self.ws_restart_btn.clicked.connect(self.restart_websocket_server)
        ws_status_layout.addWidget(self.ws_status_label)
        ws_status_layout.addWidget(self.ws_restart_btn)
        
        # ngrok 상태
        ngrok_status_layout = QHBoxLayout()
        self.ngrok_status_label = QLabel("ngrok 터널: 비활성")
        self.ngrok_url_label = QLabel("URL: -")
        self.ngrok_restart_btn = QPushButton("ngrok 재시작")
        self.ngrok_restart_btn.clicked.connect(self.restart_ngrok)
        ngrok_status_layout.addWidget(self.ngrok_status_label)
        ngrok_status_layout.addWidget(self.ngrok_url_label)
        ngrok_status_layout.addWidget(self.ngrok_restart_btn)
        
        server_layout.addLayout(ws_status_layout)
        server_layout.addLayout(ngrok_status_layout)
        server_group.setLayout(server_layout)
        layout.addWidget(server_group)
        
        # 초기 상태 체크
        self.check_server_status()
        
    def check_server_status(self):
        """서버 상태를 주기적으로 체크"""
        # 웹소켓 서버 상태 체크
        ws_active = self.is_websocket_server_running()
        self.ws_status_label.setText(f"웹소켓 서버: {'활성' if ws_active else '비활성'}")
        self.server_status_changed.emit(ws_active)
        
        # ngrok 상태 체크
        ngrok_active, ngrok_url = self.check_ngrok_status()
        self.ngrok_status_label.setText(f"ngrok 터널: {'활성' if ngrok_active else '비활성'}")
        self.ngrok_url_label.setText(f"URL: {ngrok_url if ngrok_active else '-'}")
        self.ngrok_status_changed.emit(ngrok_active)
    
    def is_websocket_server_running(self):
        """웹소켓 서버가 실행 중인지 확인"""
        try:
            # 환경변수에서 설정된 포트 체크
            return any(conn.laddr.port == self.ws_port for conn in psutil.net_connections())
        except:
            return False
            
    def check_ngrok_status(self):
        """ngrok 상태와 URL 확인"""
        try:
            response = requests.get("http://localhost:4040/api/tunnels")
            if response.status_code == 200:
                tunnels = response.json()["tunnels"]
                if tunnels:
                    return True, tunnels[0]["public_url"]
            return False, None
        except:
            return False, None
            
    def restart_websocket_server(self):
        """웹소켓 서버 재시작"""
        try:
            # 기존 프로세스 종료
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and 'python' in proc.info['cmdline'][0].lower():
                        cmdline = ' '.join(proc.info['cmdline'])
                        if 'websocket_server.py' in cmdline:
                            proc.terminate()
                            proc.wait(timeout=5)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    pass

            # 새로운 서버 프로세스 시작 - 환경변수 전달
            subprocess.Popen(
                ['powershell', '-Command', 'python src/websocket/server.py'],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
        except Exception as e:
            print(f"서버 재시작 중 오류 발생: {e}")
        finally:
            self.check_server_status()
        
    def restart_ngrok(self):
        """ngrok 재시작"""
        try:
            # 기존 ngrok 프로세스 종료
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'ngrok' in proc.info['name'].lower():
                        proc.terminate()
                        proc.wait(timeout=5)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    pass

            # 새로운 ngrok 프로세스 시작 - 환경변수의 포트 사용
            subprocess.Popen(
                ['powershell', '-Command', f'ngrok http {self.ws_port}'],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
        except Exception as e:
            print(f"ngrok 재시작 중 오류 발생: {e}")
        finally:
            self.check_server_status() 