# CLIENT
import sys
import socket
import threading

HOST = '192.168.1.103'
PORT = 9000

def handle_messages(sock: socket.socket):
    # TODO: если сеть пропала, то выходим из приложения
    while True:
        res = sock.recv(1024)
        if len(res) == 0:
            print('[WARN] Empty res')
            break
        # TODO: разбить сырое сообщение с сервера на части
        print(res.decode())


def handle_input(sock: socket.socket):
    while True:
        msg = input()
        if msg == 'exit':
            print('Exiting')
            break
        sock.sendall(msg.encode())


def main():
    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )
    # TODO: сервер долженотправлять PING каждые 5 секунд
    #  чтобы клиент знал, что сервер жив
    # sock.settimeout(10)
    sock.connect((HOST, PORT))

    mt = threading.Thread(target=handle_messages, args=(sock,))
    it = threading.Thread(target=handle_input, args=(sock,))
    mt.daemon = True

    mt.start()
    it.start()

    it.join()
    sock.close()


if __name__ == '__main__':
    main()
