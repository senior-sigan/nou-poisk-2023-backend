# CRUD = create, read, update, delete
from typing import Optional, List
from sqlalchemy.orm import Session

from models import User, Message
import datetime

from utils import hash_pwd


def get_user_by_name(db: Session, name: str) -> User | None:
    return db.query(User).filter(User.name == name).first()


def create_user(db: Session, name: str, password: str):
    hashed_password = hash_pwd(password)
    user = User(
        name=name,
        password=hashed_password,
        created_at=datetime.datetime.now(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_message(
    db: Session,
    username: str,
    *,
    user_id: Optional[int] = None,
    text: Optional[str] = None,
    file: Optional[str] = None,
    ftype: Optional[str] = None,
):
    msg = Message(
        username=username,
        created_at=datetime.datetime.now(),
    )
    if user_id is not None:
        msg.user_id = user_id
    if text is not None:
        msg.text = text
    if file is not None:
        msg.file = file
        msg.mtype = ftype
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_last_messages(db: Session) -> List[Message]:
    return db.query(Message).limit(1000).all()
