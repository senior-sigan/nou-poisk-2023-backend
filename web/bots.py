import random
from fastapi import WebSocket
from connection_manager import cm
from crud import create_message
from sqlalchemy.orm import Session


async def ping_bot(db: Session, ws: WebSocket, username: str, text: str):
    text = "Pong"
    create_message(db, "PingBot", text=text)
    await cm.broadcast(
        {
            "type": "message",
            "from": "PingBot",
            "text": text,
        }
    )


async def dice_bot(db: Session, ws: WebSocket, username: str, text: str):
    text = random.randint(1, 6)
    create_message(db, "DiceBot", text=text)
    await cm.broadcast(
        {
            "type": "message",
            "from": "DiceBot",
            "text": text,
        }
    )


# TODO: бот погода
# TODO: бот который заменяет смайлы на эмоджи или еще что-то
# TODO: бот который запускает гуся


BOTS = {"@ping": ping_bot, "@dice": dice_bot}
