# SERVER
import socket
import threading
from typing import Dict, Tuple

HOST = '0.0.0.0'
PORT = 9000

clients: Dict[Tuple, socket.socket] = {} # ключ - это ip:port а значение - client (потом имя)


def send_all_clients(text: str):
    msg = f'FROM: SERVER\r\n{text}'
    for client_addr in clients:
        clients[client_addr].sendall(msg.encode())

def client_loop(client: socket.socket, addr):
    print(f'Connected: {addr}')
    try:
        while True:
            # TODO: обрабоатывать исключения sendall и recv
            data = client.recv(1024)
            if len(data) == 0:
                print(f'[WARN] Empty data addr={addr}')
                break
            txt = data.decode().strip()
            if len(txt) == 0:
                print(f'[WARN] Empty string addr={addr}')
                continue

            print(f'{addr[0]}:{addr[1]}> {txt}')
            # client.sendall(b'OK')
            
            msg = f'FROM: {addr[0]}:{addr[1]}\r\n{txt}'
            for client_addr in clients:
                if client_addr != addr:
                    clients[client_addr].sendall(msg.encode())
    except Exception as err:
        print(f'[ERROR] {addr}', err)

    print(f'Client disconnected {addr}')
    clients.pop(addr)
    client.close()
    send_all_clients(f'Client {addr[0]}:{addr[1]} Disconnected ')


def main():
    with socket.create_server(
        (HOST, PORT), 
        reuse_port=True,
    ) as sock:
        print(f'Listening {HOST}:{PORT}')

        while True:
            try:
                print('wait for connection')
                client, addr = sock.accept()
                clients[addr] = client
                ct = threading.Thread(
                    target=client_loop,
                    args=(client, addr),
                )
                ct.start()
            except Exception as err:
                print('[ERROR] ', err)
                break

if __name__ == '__main__':
    main()
