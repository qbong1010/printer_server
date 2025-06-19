# POS 프린터 프로그램을 숨김 모드로 실행
Set-Location "C:\Users\POS\Desktop\posprinter_supabase"
Start-Process -FilePath "py" -ArgumentList "main.py" -WindowStyle Hidden 