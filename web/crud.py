# CRUD = create, read, update, delete
from sqlalchemy.orm import Session

from models import User
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
