from typing import Dict
from fastapi import Cookie, FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from uuid import uuid4, UUID
import time

from pydantic import BaseModel, Field

def now_ts():
    return int(time.time() * 1000)

class ConnectionManager:
    def __init__(self) -> None:
        self.connections: Dict[UUID, WebSocket] = {}

    @property
    def users(self):
        return [str(uid) for uid in self.connections.keys()]

    async def connect(self, ws: WebSocket):
        await ws.accept()
        uid = uuid4()
        self.connections[uid] = ws
        return uid
    
    def disconnect(self, uid: UUID):
        self.connections.pop(uid)

    async def broadcast(self, msg):
        msg['ts'] = now_ts()
        for uid, ws in self.connections.items():
            await ws.send_json(msg)


app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates('templates')
cm = ConnectionManager()

CHAT_BOT = 'ChatBot'

@app.websocket('/ws')
async def ws_endpoint(ws: WebSocket):
    uid = await cm.connect(ws)
    try:
        await cm.broadcast({
            'from': CHAT_BOT,
            'type': 'users_list',
            'users': cm.users,
            'text': f'Client connected {uid}',
        })
        while True:
            txt = await ws.receive_text()
            print('>', txt)
            message_id = uuid4()
            await cm.broadcast({
                'from': str(uid),
                'text': txt,
                'mid': str(message_id),
            })
    except WebSocketDisconnect:
        cm.disconnect(uid)
        print(f'Client disconnected {uid}')
        await cm.broadcast({
            'from': CHAT_BOT,
            'type': 'users_list',
            'users': cm.users,
            'text': f'Client disconnected {uid}',
        })

@app.get('/')
def index(request: Request):
    return templates.TemplateResponse(
        'index.html', {'request': request},
    )
