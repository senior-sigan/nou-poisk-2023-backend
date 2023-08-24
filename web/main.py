from json import JSONDecodeError
import json
import os
import shutil
import time
from typing import Dict, Tuple
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
from connection_manager import cm
from pathlib import Path
from bots import BOTS
from crud import (
    create_message,
    create_user,
    get_all_users,
    get_last_messages,
    get_user_by_name,
    like_message,
)
from models import Base, User
from database import SessionLocal, engine
from utils import verify_pwd
from sqlalchemy.orm import Session


MEDIA_DIR = Path("media")

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()
# host files in Caddy server
# app.mount("/static", StaticFiles(directory="static"), name="static")
# app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")
templates = Jinja2Templates("templates")

CHAT_BOT = "ChatBot"


async def handle_mention(
    db: Session, ws: WebSocket, username: str, mention: str, text: str
):
    print(f"User {username} mentioned {mention} with {text}")
    bot = BOTS.get(mention)
    if bot is not None:
        await bot(db, ws, username, text)
    else:
        print(f'[WARN] unknown bot "{mention}" txt={text}')


def online_users(db: Session):
    online_users = set(cm.users)
    allusers = [
        {"name": user.name, "isOnline": user.name in online_users}
        for user in get_all_users(db)
    ]
    allusers.sort(key=lambda a: a["name"])
    allusers.sort(key=lambda a: a["isOnline"], reverse=True)
    return allusers


def find_mentionee(txt: str) -> Tuple[str | None, str]:
    idx = txt.find(" ")
    if idx < 0:
        return txt[1:], None
    if idx < 2:
        return None, txt
    return txt[1:idx], txt[idx + 1 :]


async def handle_chat_message(ws: WebSocket, db: Session, data: Dict, user: User):
    if data["type"] == "message":
        txt: str = data["text"].strip()
        if len(txt) > 512:
            print(f"Message from {user.name} too long. Ignoring...")
            return
        print(f"{user.name}> ", txt)
        mention = None
        to = None
        if txt[0] == "@":
            mention, txt_bot = find_mentionee(txt)
            if mention is not None and mention not in BOTS:
                # то есть это человек, а не бот
                # TODO: проверить что есть такой человек
                to = mention
                mention = None
                txt = txt_bot
        msg = create_message(db, user.name, user_id=user.id, text=txt, to=to)
        await cm.broadcast(
            {
                "type": "message",
                "from": user.name,
                "text": txt,
                "to": to,
                "reaction": msg.reaction,
                "message_id": msg.id,
            }
        )
        if mention is not None:
            await handle_mention(db, ws, user.name, mention, txt_bot)
    elif data["type"] == "typing":
        await cm.broadcast(
            {
                "type": "typing",
                "from": CHAT_BOT,
                "user": user.name,
            }
        )
    elif data["type"] == "likes" and data.get("message_id") is not None:
        msg = like_message(db, data["message_id"])
        await cm.broadcast(
            {
                "type": "reaction",
                "from": CHAT_BOT,
                "message_id": msg.id,
                "reaction": msg.reaction,
                "user": user.name,
            }
        )
    else:
        print(f"[WARN] unknown message type from user {user.name}", data)


async def send_last_messages(db: Session, ws: WebSocket, me: str):
    last_mesages = get_last_messages(db)
    messages = []
    for msg in last_mesages:
        data = {
            "from": msg.username,
            "type": "message",
            "to": msg.to,
            "text": msg.text,
            "ts": int(time.mktime(msg.created_at.timetuple()) * 1000),
            "reaction": msg.reaction,
            "message_id": msg.id,
        }
        if msg.file is not None:
            data["file"] = {
                "content_type": msg.mtype,
                "path": msg.file,
            }
        if msg.to is None or me == msg.to or me == msg.username:
            messages.append(data)
            
    await ws.send_json({
        "from": CHAT_BOT,
        "type": 'history',
        "messages": messages,
    })
        


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
                "users": online_users(db),
                "text": f"Client connected {username}",
            }
        )
        await send_last_messages(db, ws, username)
        while True:
            try:
                txt = await ws.receive_text()
                data = json.loads(txt)
                await handle_chat_message(ws, db, data, user)
            except JSONDecodeError:
                print(f'[ERROR] failed to parse json "{txt}"')
    except WebSocketDisconnect:
        cm.disconnect(ws)
        print(f"Client disconnected {username}")
        await cm.broadcast(
            {
                "from": CHAT_BOT,
                "type": "users_list",
                "users": online_users(db),
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


@app.post('/logout')
async def logout():
    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER) 
    response.delete_cookie("username")
    return response


@app.post("/login")
def login(
    request: Request,
    username: str = Form(),
    password: str = Form(),
    db: Session = Depends(get_db),
):
    username = username.strip()
    password = password.strip()
    print(f'[INFO] /login username="{username}" password="{password}"')

    if len(username) == 0 or len(password) == 0:
        print("Empty username or password")
        return templates.TemplateResponse("login.html", {"request": request})

    if username[0] == '@' or len(username) > 16:
        print('Bad username')
        return templates.TemplateResponse("login.html", {"request": request})

    user = get_user_by_name(db, username)
    
    # либо он новый либо старый и корректный юзер
    if user is None:
        user = create_user(db, username, password)
        print("CREATED USER ", user.id, user.name, user.created_at)
        response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)    
        response.set_cookie("username", user.name)
        return response

    if not verify_pwd(password, user.password):
        print("FAILED: ", user.id, user.name, user.created_at)
        print(f"Password is wrong for user {username}")
        # TODO: пароль или имя неправильные
        return templates.TemplateResponse("login.html", {"request": request})

    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    # TODO: в куках надо хранить session_id а не юзернейм, но так проще пока что, хоть и небезопасно
    response.set_cookie("username", user.name)
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
    msg = create_message(db, user.name, user_id=user.id, file=path, ftype=content_type)
    await cm.broadcast(
        {
            "from": username,
            "type": "message",
            "file": {
                "content_type": content_type,
                "path": path,
            },
            "message_id": msg.id,
            "reaction": msg.reaction,
        }
    )
    return {"path": f"/media/{fid}", "content_type": content_type}
