import os
import shutil
from typing import Dict
from fastapi import (
    Cookie,
    FastAPI,
    Form,
    Request,
    Response,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from uuid import uuid4
import time
from pathlib import Path

from pydantic import BaseModel


def now_ts():
    return int(time.time() * 1000)


class UserModel(BaseModel):
    name: str
    password: str


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: Dict[WebSocket, UserModel] = {}

    @property
    def users(self):
        return list({user.name for user in self.connections.values()})

    async def connect(self, ws: WebSocket, user: UserModel):
        await ws.accept()
        self.connections[ws] = user

    def disconnect(self, ws: WebSocket):
        self.connections.pop(ws)

    async def broadcast(self, msg: Dict[str, any]):
        msg["ts"] = now_ts()
        msg["mid"] = str(uuid4())
        for ws in self.connections:
            await ws.send_json(msg)


MEDIA_DIR = Path("media")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")
templates = Jinja2Templates("templates")
cm = ConnectionManager()

users: Dict[str, UserModel] = {}

CHAT_BOT = "ChatBot"


@app.websocket("/ws")
async def ws_endpoint(
    ws: WebSocket,
    username: str | None = Cookie(default=None),
):
    print(f"WS username={username}")
    user = users.get(username)
    if user is None:
        return

    await cm.connect(ws, user)
    try:
        await cm.broadcast(
            {
                "from": CHAT_BOT,
                "type": "users_list",
                "users": cm.users,
                "text": f"Client connected {username}",
            }
        )
        while True:
            txt = await ws.receive_text()
            if len(txt) > 512:
                continue
            print(f"{username}> ", txt)
            await cm.broadcast({
                "from": username,
                "text": txt,
            })
    except WebSocketDisconnect:
        cm.disconnect(ws)
        print(f"Client disconnected {username}")
        await cm.broadcast(
            {
                "from": CHAT_BOT,
                "type": "users_list",
                "users": cm.users,
                "text": f"Client disconnected {username}",
            }
        )


@app.get("/")
def index(
    request: Request,
    username: str | None = Cookie(default=None),
):
    print(f"GET / username={username}")
    user = users.get(username)
    if user is None:
        return templates.TemplateResponse(
            "login.html",
            {"request": request},
        )
    return templates.TemplateResponse(
        "index.html",
        {"request": request},
    )


@app.post("/login")
def login(
    request: Request,
    username: str = Form(),
    password: str = Form(),
):
    username = username.strip()
    password = password.strip()
    if len(username) == 0 or len(password) == 0:
        return templates.TemplateResponse("login.html", {"request": request})
    user = users.get(username)
    if user is not None and user.password != password:
        # TODO: пароль или имя неправильные
        return templates.TemplateResponse("login.html", {"request": request})

    # либо он новый либо старый и корректный юзер
    if user is None:
        user = UserModel(
            name=username,
            password=password,
        )
        users[username] = user

    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie("username", username)
    return response


@app.post("/upload")
async def create_upload_files(
    file: UploadFile,
    username: str | None = Cookie(default=None),
):
    user = users.get(username)
    if user is None:
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    fid = str(uuid4())
    if file.filename is not None:
        parts = file.filename.split(os.extsep)
        if len(parts) > 1:
            ext = parts[-1]
            fid += f".{ext}"
    print(f"username={username} fid={fid}")

    new_file = MEDIA_DIR / fid
    with new_file.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    content_type = file.content_type.split('/')[0]

    await cm.broadcast({
        "from": username,
        "content_type": content_type,
        "file": f"/media/{fid}",
    })
    return {"file": f"/media/{fid}", "content_type": content_type}
