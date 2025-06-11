import sys
import os
from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication
from src.gui.main_window import MainWindow

def main():
    # 환경 변수 로드
    load_dotenv()
    
    # QApplication 인스턴스 생성
    app = QApplication(sys.argv)
    
    # 메인 윈도우 생성 및 표시
    window = MainWindow()
    window.show()
    
    # 애플리케이션 실행
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 