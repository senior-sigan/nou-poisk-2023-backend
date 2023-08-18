# SERVER
import socket

HOST = '0.0.0.0'
PORT = 9000


def client_loop(client: socket.socket, addr):
    print(f'Connected: {addr}')
    while True:
        data = client.recv(1024)
        print(f'{addr[0]}> {data.decode()}')
        msg = input('>')
        if msg == 'exit':
            break
        client.sendall(msg.encode())
    client.close()


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f'Listening {HOST}:{PORT}')
    sock.bind((HOST, PORT))
    sock.listen(5)

    while True:
        try:
            print('wait for connection')
            client, addr = sock.accept()
            client_loop(client, addr)
        except Exception as err:
            print('[ERROR] ', err)

if __name__ == '__main__':
    main()
