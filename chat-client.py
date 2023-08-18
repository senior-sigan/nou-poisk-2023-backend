# CLIENT
import socket

HOST = '192.168.1.103'
PORT = 9000

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM,
)
sock.settimeout(10)

sock.connect((HOST, PORT))

while True:
    msg = input('> ')
    if msg == 'exit':
        break
    sock.sendall(msg.encode())
    res = sock.recv(1024)
    if len(res) == 0:
        break
    print(f'server> {res.decode()}')

sock.close()