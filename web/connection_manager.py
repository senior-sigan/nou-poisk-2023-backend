from typing import Dict
from uuid import uuid4

from fastapi import WebSocket

from models import User
from utils import now_ts


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: Dict[WebSocket, User] = {}

    @property
    def users(self):
        return list({user.name for user in self.connections.values()})

    async def connect(self, ws: WebSocket, user: User):
        await ws.accept()
        self.connections[ws] = user

    def disconnect(self, ws: WebSocket):
        self.connections.pop(ws)

    async def broadcast(self, msg: Dict[str, any]):
        if msg.get('ts') is None:
            msg["ts"] = now_ts()
        msg["mid"] = str(uuid4())
        
        to = msg.get('to')
        from_ = msg.get('from')
        for ws, user in self.connections.items():
            if to is None or user.name == to or user.name == from_:
                await ws.send_json(msg)


cm = ConnectionManager()
