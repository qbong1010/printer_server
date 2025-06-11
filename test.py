# 예시 Flask 서버 실행 코드
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Server OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
