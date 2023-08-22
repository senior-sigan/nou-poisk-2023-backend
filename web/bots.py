import random
from typing import Tuple
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


def dice_parse(text: str | None) -> Tuple[int, int]:
    if text is None or len(text) == 0:
        return 1, 6
    parts = text.split(" ")
    if len(parts) == 0:
        return 1, int(parts[0])
    return int(parts[0]), int(parts[1])


async def dice_bot(db: Session, ws: WebSocket, username: str, message: str):
    try:
        nums = dice_parse(message)
        text = str(random.randint(min(nums), max(nums)))
    except ValueError:
        text = "Пишите @dice или @dice 10 или @dice 2 20"
    create_message(db, "DiceBot", text=text)
    await cm.broadcast(
        {
            "type": "message",
            "from": "DiceBot",
            "text": text,
        }
    )


async def weather_bot(db: Session, ws: WebSocket, username: str, text: str):
    text = "This is fine..."
    create_message(db, "Weather", text=text)
    await cm.broadcast(
        {
            "type": "message",
            "from": "Weather",
            "text": text,
        }
    )


# TODO: бот погода
# TODO: бот который заменяет смайлы на эмоджи или еще что-то
# TODO: бот который запускает гуся


BOTS = {"@ping": ping_bot, "@dice": dice_bot, "@weather": weather_bot}
