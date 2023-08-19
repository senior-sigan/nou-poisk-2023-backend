import curses
from curses import wrapper
from typing import Optional
import textwrap
import time
import socket
import queue
import threading

ENTER_HEIGHT = 4
USER_LIST_WIDTH = 12
HOST = '192.168.1.103'
PORT = 9000


class EditWindow:
    def __init__(
        self, stdscr: curses.window, 
        y: int, x: int, h:int, w: int,
    ):
        self.y = y
        self.x = x
        self.h = h
        self.w = w
        self.win = stdscr.derwin(self.h, self.w, self.y, self.x)
        self.win.nodelay(True)
        self.text = ''

    def get_text(self) -> Optional[str]:
        while True:
            (y, x) = self.win.getyx()
            try:
                ch = self.win.get_wch()
            except curses.error:
                return None
            if ch == '\n':
                break
            elif ch == '\x7f' or ch == '\x08':
                if len(self.text) > 0:
                    self.win.move(y, x - 1)
                    self.win.delch()
                    self.text = self.text[:-1]
            elif isinstance(ch, str) and len(self.text) < self.w * self.h - 1:
                # -1 потому что курсор сместит за экран когда напечатается последний символ
                # и приложение упадёт.
                # TODO: сделать скролл поля ввода
                self.text += ch
                self.win.addch(ch)
        self.win.clear()
        self.win.refresh()
        self.win.move(0, 0)
        text = self.text
        self.text = ''
        return text

def print_wrapped(win: curses.window, text: str, y=0, x=0):
    h, w = win.getmaxyx()
    if x >= w or x < 0:
        print(f'[WARN] x={x} is out of the window w={w}')
        return
    if y >= h or y < 0:
        print(f'[WARN] y={y} is out of the window h={h}')
        return
    text_w = w - x
    lines = textwrap.wrap(text, text_w)
    n_lines = len(lines)
    text_h = 0
    for i, line in enumerate(lines):
        ly = y - n_lines + i + 1
        if ly >= 0:
            text_h += 1
            win.addstr(ly, x, line)
    return text_h


class MessagesWindow:
    def __init__(
        self, stdscr: curses.window, 
        y: int, x: int, h:int, w: int,
    ):
        self.y = y
        self.x = x
        self.h = h
        self.w = w
        self.win = stdscr.derwin(h, w, y, x)
        self.messages = []

    def append(self, msg):
        self.messages.append(msg)

        self.win.clear()
        lines = 0
        for msg in self.messages[::-1]:
            l = print_wrapped(self.win, msg, self.h - lines - 1, 0)
            lines += l + 1
            if lines >= self.h:
                break
        self.win.refresh()


def handle_messages(
    sock: socket.socket,
    msg_queue: queue.Queue,
):
    disconect_counter = 0
    while True:
        res = sock.recv(1024)
        if len(res) == 0:
            disconect_counter += 1
            if disconect_counter > 10:
                # TODO: log error
                break
            time.sleep(0.1)
            continue
        # TODO: разбить сырое сообщение с сервера на части
        msg_queue.put(res.decode())
        disconect_counter = 0
    # TODO: если сеть пропала, то выходим из приложения


def main(stdscr: curses.window):
    msg_queue = queue.Queue()
    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )
    sock.connect((HOST, PORT))

    mt = threading.Thread(target=handle_messages, args=(sock, msg_queue))
    mt.daemon = True
    mt.start()

    stdscr.clear()
    h, w = stdscr.getmaxyx()

    stdscr.vline(0, USER_LIST_WIDTH, curses.ACS_VLINE, h)
    stdscr.hline(h - ENTER_HEIGHT - 1, USER_LIST_WIDTH + 1, curses.ACS_HLINE, w)

    stdscr.refresh()

    edit_win = EditWindow(
        stdscr=stdscr,
        y=h - ENTER_HEIGHT,
        x=USER_LIST_WIDTH + 1,
        h=ENTER_HEIGHT,
        w=w - (USER_LIST_WIDTH + 1),
    )

    msg_win = MessagesWindow(
        stdscr=stdscr,
        y=1,
        x=USER_LIST_WIDTH + 1,
        h=h - ENTER_HEIGHT - 2,
        w=w - (USER_LIST_WIDTH + 1),
    )

    while True:        
        text = edit_win.get_text()

        if text is not None and len(text) > 0:
            msg_win.append(text)
            sock.sendall(text.encode())

        try:
            msg = msg_queue.get(block=False, timeout=0.1)
            msg_win.append(msg)
        except queue.Empty:
            pass

        time.sleep(0.1)

if __name__ == '__main__':
    wrapper(main)