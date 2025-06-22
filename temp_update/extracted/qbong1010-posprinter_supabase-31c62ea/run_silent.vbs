Set WshShell = CreateObject("WScript.Shell")
' 작업 디렉토리를 설정
WshShell.CurrentDirectory = "C:\Users\POS\Desktop\posprinter_supabase"
' Python 실행 (숨김 모드) - py 런처 사용
WshShell.Run "py main.py", 0, False 