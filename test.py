import serial

# COM 포트와 Baudrate는 실제 환경에 맞게 설정
ser = serial.Serial(port='COM3', baudrate=9600)

# 포스 프린터로 텍스트 전송
ser.write(b'Kim sohyun.\n')

# 연결 종료
ser.close()
