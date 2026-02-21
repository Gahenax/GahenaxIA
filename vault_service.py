import os, socket, threading
KEY = os.environ.get('GEMINI_API_KEY', '')
def handle(c):
    try:
        data = c.recv(1024)
        if data == b'GET_KEY': c.sendall(KEY.encode())
    finally: c.close()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', 55555))
s.listen(1)
while True:
    conn, _ = s.accept()
    threading.Thread(target=handle, args=(conn,)).start()
