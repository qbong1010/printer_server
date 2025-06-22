#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POS 프린터 설정 도구
비개발자도 쉽게 사용할 수 있는 GUI 설정 프로그램
"""

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import subprocess
import sys

class ConfigTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("POS 프린터 설정 도구")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # 설정 파일 경로
        self.config_file = Path("printer_config.json")
        self.env_file = Path(".env")
        
        # 현재 설정 로드
        self.current_config = self.load_config()
        self.current_env = self.load_env()
        
        self.create_widgets()
        
    def load_config(self):
        """프린터 설정 로드"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # 기본 설정
        return {
            "printer_type": "default",
            "printer_name": "기본 프린터",
            "usb_info": {
                "vendor_id": "0525",
                "product_id": "A700",
                "interface": "0"
            },
            "network_info": {
                "address": "192.168.0.100",
                "port": "9100"
            },
            "auto_print": {
                "enabled": True,
                "retry_count": 3,
                "retry_interval": 30,
                "check_printer_status": True
            }
        }
    
    def load_env(self):
        """환경 변수 설정 로드"""
        env_config = {
            "SUPABASE_URL": "",
            "SUPABASE_PROJECT_ID": "",
            "SUPABASE_API_KEY": "",
            "APP_LOG_PATH": "app.log",
            "CACHE_DB_PATH": "cache.db"
        }
        
        if self.env_file.exists():
            try:
                with open(self.env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            if key in env_config:
                                env_config[key] = value
            except:
                pass
        
        return env_config
    
    def create_widgets(self):
        """GUI 위젯 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 노트북 (탭) 위젯
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Supabase 설정 탭
        self.create_supabase_tab(notebook)
        
        # 프린터 설정 탭
        self.create_printer_tab(notebook)
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # 버튼들
        ttk.Button(button_frame, text="설정 저장", command=self.save_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="프린터 테스트", command=self.test_printer).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="프로그램 실행", command=self.run_program).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="종료", command=self.root.quit).pack(side=tk.RIGHT)
        
        # 상태 표시줄
        self.status_var = tk.StringVar()
        self.status_var.set("설정을 입력하고 저장 버튼을 클릭하세요.")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_label.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
    
    def create_supabase_tab(self, parent):
        """Supabase 설정 탭 생성"""
        frame = ttk.Frame(parent, padding="10")
        parent.add(frame, text="Supabase 설정")
        
        # Supabase URL
        ttk.Label(frame, text="Supabase URL:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.supabase_url_var = tk.StringVar(value=self.current_env["SUPABASE_URL"])
        ttk.Entry(frame, textvariable=self.supabase_url_var, width=60).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 프로젝트 ID
        ttk.Label(frame, text="프로젝트 ID:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.project_id_var = tk.StringVar(value=self.current_env["SUPABASE_PROJECT_ID"])
        ttk.Entry(frame, textvariable=self.project_id_var, width=60).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # API 키
        ttk.Label(frame, text="API 키:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.api_key_var = tk.StringVar(value=self.current_env["SUPABASE_API_KEY"])
        ttk.Entry(frame, textvariable=self.api_key_var, width=60, show="*").grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 도움말
        help_text = """
Supabase 설정 정보:
1. Supabase URL: https://your-project.supabase.co 형식
2. 프로젝트 ID: Supabase 대시보드에서 확인 가능  
3. API 키: Supabase 설정에서 anon/public 키 사용

※ 모든 필드를 올바르게 입력해야 프로그램이 정상 작동합니다.
        """
        
        text_widget = tk.Text(frame, height=8, width=70, wrap=tk.WORD)
        text_widget.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        text_widget.insert(tk.END, help_text.strip())
        text_widget.config(state=tk.DISABLED)
    
    def create_printer_tab(self, parent):
        """프린터 설정 탭 생성"""
        frame = ttk.Frame(parent, padding="10")
        parent.add(frame, text="프린터 설정")
        
        # 프린터 유형
        ttk.Label(frame, text="프린터 유형:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.printer_type_var = tk.StringVar(value=self.current_config["printer_type"])
        printer_type_combo = ttk.Combobox(frame, textvariable=self.printer_type_var, 
                                         values=["default", "usb", "network", "file"], state="readonly")
        printer_type_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 프린터 이름
        ttk.Label(frame, text="프린터 이름:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.printer_name_var = tk.StringVar(value=self.current_config["printer_name"])
        ttk.Entry(frame, textvariable=self.printer_name_var, width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 자동 인쇄 설정
        auto_frame = ttk.LabelFrame(frame, text="자동 인쇄 설정", padding="5")
        auto_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.auto_print_var = tk.BooleanVar(value=self.current_config["auto_print"]["enabled"])
        ttk.Checkbutton(auto_frame, text="자동 인쇄 활성화", variable=self.auto_print_var).grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        ttk.Label(auto_frame, text="재시도 횟수:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.retry_count_var = tk.IntVar(value=self.current_config["auto_print"]["retry_count"])
        ttk.Spinbox(auto_frame, from_=1, to=10, textvariable=self.retry_count_var, width=5).grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
    
    def save_config(self):
        """설정 저장"""
        try:
            # 프린터 설정 저장
            config = {
                "printer_type": self.printer_type_var.get(),
                "printer_name": self.printer_name_var.get(),
                "usb_info": {
                    "vendor_id": "0525",
                    "product_id": "A700",
                    "interface": "0"
                },
                "network_info": {
                    "address": "192.168.0.100",
                    "port": "9100"
                },
                "auto_print": {
                    "enabled": self.auto_print_var.get(),
                    "retry_count": self.retry_count_var.get(),
                    "retry_interval": 30,
                    "check_printer_status": True
                }
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # 환경 변수 저장
            env_content = f"""# Supabase 설정
SUPABASE_URL={self.supabase_url_var.get()}
SUPABASE_PROJECT_ID={self.project_id_var.get()}
SUPABASE_API_KEY={self.api_key_var.get()}

# 로그 파일 경로
APP_LOG_PATH=app.log
CACHE_DB_PATH=cache.db
"""
            
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            self.status_var.set("설정이 성공적으로 저장되었습니다.")
            messagebox.showinfo("성공", "설정이 저장되었습니다.")
            
        except Exception as e:
            self.status_var.set(f"설정 저장 실패: {e}")
            messagebox.showerror("오류", f"설정 저장 실패: {e}")
    
    def test_printer(self):
        """프린터 테스트"""
        try:
            script_path = Path("setup_utility/test_printer.py")
            if script_path.exists():
                subprocess.run([sys.executable, str(script_path)], check=True)
                messagebox.showinfo("성공", "프린터 테스트가 완료되었습니다.")
            else:
                messagebox.showwarning("경고", "프린터 테스트 스크립트를 찾을 수 없습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"프린터 테스트 실패: {e}")
    
    def run_program(self):
        """메인 프로그램 실행"""
        try:
            subprocess.Popen([sys.executable, "main.py"])
            self.status_var.set("프로그램을 실행했습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"프로그램 실행 실패: {e}")
    
    def run(self):
        """GUI 실행"""
        self.root.mainloop()

def main():
    """메인 함수"""
    app = ConfigTool()
    app.run()

if __name__ == "__main__":
    main()

class ConfigTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("POS 프린터 설정 도구")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # 설정 파일 경로
        self.config_file = Path("printer_config.json")
        self.env_file = Path(".env")
        
        # 현재 설정 로드
        self.current_config = self.load_config()
        self.current_env = self.load_env()
        
        self.create_widgets()
        
    def load_config(self):
        """프린터 설정 로드"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # 기본 설정
        return {
            "printer_type": "default",
            "printer_name": "기본 프린터",
            "usb_info": {
                "vendor_id": "0525",
                "product_id": "A700",
                "interface": "0"
            },
            "network_info": {
                "address": "192.168.0.100",
                "port": "9100"
            },
            "auto_print": {
                "enabled": True,
                "retry_count": 3,
                "retry_interval": 30,
                "check_printer_status": True
            }
        }
    
    def load_env(self):
        """환경 변수 설정 로드"""
        env_config = {
            "SUPABASE_URL": "",
            "SUPABASE_PROJECT_ID": "",
            "SUPABASE_API_KEY": "",
            "APP_LOG_PATH": "app.log",
            "CACHE_DB_PATH": "cache.db"
        }
        
        if self.env_file.exists():
            try:
                with open(self.env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            if key in env_config:
                                env_config[key] = value
            except:
                pass
        
        return env_config
    
    def create_widgets(self):
        """GUI 생성"""
        label = tk.Label(self.root, text="POS 프린터 설정 도구", font=("Arial", 16))
        label.pack(pady=20)
        
        ttk.Button(self.root, text="설정 저장", command=self.save_config).pack(pady=10)
        ttk.Button(self.root, text="종료", command=self.root.quit).pack(pady=10)
    
    def save_config(self):
        """설정 저장"""
        try:
            # 프린터 설정 저장
            config = {
                "printer_type": "default",
                "printer_name": "기본 프린터",
                "auto_print": {
                    "enabled": True,
                    "retry_count": 3,
                    "retry_interval": 30,
                    "check_printer_status": True
                }
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # 환경 변수 저장
            env_content = """# Supabase 설정
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PROJECT_ID=your-project-id
SUPABASE_API_KEY=your-api-key

# 로그 파일 경로
APP_LOG_PATH=app.log
CACHE_DB_PATH=cache.db
"""
            
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            messagebox.showinfo("성공", "설정이 저장되었습니다.")
            
        except Exception as e:
            messagebox.showerror("오류", f"설정 저장 실패: {e}")

    def run(self):
        """GUI 실행"""
        self.root.mainloop()

def main():
    """메인 함수"""
    app = ConfigTool()
    app.run()

if __name__ == "__main__":
    main() 