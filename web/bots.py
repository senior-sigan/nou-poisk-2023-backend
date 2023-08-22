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


async def dice_bot(db: Session, ws: WebSocket, username: str, message: str):
    try:
        if message is None:
            text = str(random.randint(1, 6))
        elif len(message.split()) == 1:
            nums = [1, int(message)]
            text = str(random.randint(min(nums), max(nums)))
        else:
            nums = [int(message.split()[0]), int(message.split()[1])]
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
