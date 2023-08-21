from json import JSONDecodeError
import json
import os
import shutil
from typing import Dict
from fastapi import (
    Cookie,
    Depends,
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
from crud import create_message, create_user, get_last_messages, get_user_by_name
from models import Base, User
from database import SessionLocal, engine
from utils import verify_pwd
from sqlalchemy.orm import Session


def now_ts():
    return int(time.time() * 1000)


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
        msg["ts"] = now_ts()
        msg["mid"] = str(uuid4())
        for ws in self.connections:
            await ws.send_json(msg)


MEDIA_DIR = Path("media")

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")
templates = Jinja2Templates("templates")
cm = ConnectionManager()

CHAT_BOT = "ChatBot"


async def handle_chat_message(db: Session, data: Dict, user: User):
    if data["type"] == "message":
        txt = data["text"]
        if len(txt) > 512:
            print(f"Mesage from {user.name} too long. Ignoring...")
            return
        print(f"{user.name}> ", txt)
        create_message(db, user, text=txt)
        await cm.broadcast(
            {
                "type": "message",
                "from": user.name,
                "text": txt,
            }
        )
    else:
        print(f"[WARN] unknown message type from user {user.name}", data)


async def send_last_messages(db: Session, ws: WebSocket):
    last_mesages = get_last_messages(db)
    for msg in last_mesages:
        data = {
            "from": msg.user.name,
            "type": "message",
            "text": msg.text,
        }
        if msg.file is not None:
            data["file"] = {
                "content_type": msg.mtype,
                "path": msg.file,
            }
        await ws.send_json(data)


@app.websocket("/ws")
async def ws_endpoint(
    ws: WebSocket,
    username: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    print(f"WS username={username}")
    user = get_user_by_name(db, username)
    if user is None:
        return

    await cm.connect(ws, user)
    try:
        await ws.send_json(
            {
                "from": CHAT_BOT,
                "type": "me",
                "me": username,
            }
        )
        await cm.broadcast(
            {
                "from": CHAT_BOT,
                "type": "users_list",
                "users": cm.users,
                "text": f"Client connected {username}",
            }
        )
        await send_last_messages(db, ws)
        while True:
            try:
                txt = await ws.receive_text()
                data = json.loads(txt)
                await handle_chat_message(db, data, user)
            except JSONDecodeError:
                print(f'[ERROR] failed to parse json "{txt}"')
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
    db: Session = Depends(get_db),
):
    print(f"GET / username={username}")
    user = get_user_by_name(db, username)
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
    db: Session = Depends(get_db),
):
    username = username.strip()
    password = password.strip()
    if len(username) == 0 or len(password) == 0:
        print("Empty username or password")
        return templates.TemplateResponse("login.html", {"request": request})
    user = get_user_by_name(db, username)
    if user is not None and verify_pwd(password, user.password):
        print("FAILED: ", user.id, user.name, user.created_at)
        print(f"Password is wrong for user {username}")
        # TODO: пароль или имя неправильные
        return templates.TemplateResponse("login.html", {"request": request})

    # либо он новый либо старый и корректный юзер
    if user is None:
        user = create_user(db, username, password)
        print("CREATED USER ", user.id, user.name, user.created_at)

    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    # TODO: в куках надо хранить session_id а не юзернейм, но так проще пока что, хоть и небезопасно
    response.set_cookie("username", username)
    return response


@app.post("/upload")
async def create_upload_files(
    file: UploadFile,
    username: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    user = get_user_by_name(db, username)
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

    content_type = file.content_type.split("/")[0]

    path = f"/media/{fid}"
    create_message(db, user, file=path, ftype=content_type)
    await cm.broadcast(
        {
            "from": username,
            "type": "message",
            "file": {
                "content_type": content_type,
                "path": path,
            },
        }
    )
    return {"path": f"/media/{fid}", "content_type": content_type}
