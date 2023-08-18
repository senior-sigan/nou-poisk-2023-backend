import socket

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM,
)
sock.settimeout(10)

sock.connect(('192.168.1.103', 3000))

sock.sendall(
    b'GET /hello.html HTTP/1.1\r\n'
    b'Connection: close\r\n\r\n'
)

res = b''
while True:
    data = sock.recv(1024)
    if len(data) == 0:
        break
    res += data

print(res.decode())