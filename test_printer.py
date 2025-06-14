from src.printer.escpos_printer import _get_printer

def test_printer():
    try:
        printer = _get_printer()
        print("프린터 연결 성공!")
        
        # 테스트 출력
        printer.text("프린터 연결 테스트\n")
        printer.text("이 메시지가 출력되면 연결이 정상입니다.\n")
        printer.cut()
        
    except Exception as e:
        print(f"프린터 연결 실패: {e}")

if __name__ == "__main__":
    test_printer() 