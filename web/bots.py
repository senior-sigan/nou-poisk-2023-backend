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
            "from": "@PingBot",
            "text": text,
        }
    )


def dice_parse(text: str | None) -> Tuple[int, int]:
    if text is None or len(text) == 0:
        return 1, 6
    parts = text.split(" ")
    if len(parts) == 1:
        return 1, int(parts[0])
    return int(parts[0]), int(parts[1])


async def dice_bot(db: Session, ws: WebSocket, username: str, message: str):
    try:
        nums = dice_parse(message)
        text = f"🎲 {str(random.randint(min(nums), max(nums)))}"
    except ValueError:
        text = "Пишите @dice или @dice 10 или @dice 2 20"
    create_message(db, "DiceBot", text=text)
    await cm.broadcast(
        {
            "type": "message",
            "from": "@DiceBot",
            "text": text,
        }
    )


async def flip_bot(db: Session, ws: WebSocket, username: str, text: str):
    flip = random.randint(1, 2)
    if flip == 1:
        text = "🌕 head"
    elif flip == 2:
        text = "🌑 tail"
    create_message(db, "@FlipBot", text=text)
    await cm.broadcast(
        {
            "type": "message",
            "from": "@FlipBot",
            "text": text,
        }
    )


async def weather_bot(db: Session, ws: WebSocket, username: str, text: str):
    text = "This is fine 👌"
    create_message(db, "Weather", text=text)
    await cm.broadcast(
        {
            "type": "message",
            "from": "@Weather",
            "text": text,
        }
    )


async def help_bot(db: Session, ws: WebSocket, username: str, text: str):
    messages = [
        "@ping return Pong",
        "@weather return precise weather in your location",
        "@dice return random number from x to y",
        "@goose return goose",
        "@flip to flip a coin",
        "@help return help for you)",
    ]
    for i in messages:
        await cm.broadcast(
            {
                "type": "message",
                "from": "@help",
                        "text": i,
            }
        )


# TODO: бот погода
# TODO: бот который заменяет смайлы на эмоджи или еще что-то

async def goose_bot(db: Session, ws: WebSocket, username: str, text: str):
    gooses = [["░░░░░░░░░░░░░░░░░░░░", "░░░░░ЗАПУСКАЕМ░░░░░░░", "░ГУСЯ░▄▀▀▀▄░РАБОТЯГИ░░", "▄███▀░◐░░░▌░░░░░░░░░", "░░░░▌░░░░░▐░░░░░░░░░", "░░░░▐░░░░░▐░░░░░░░░░", "░░░░▌░░░░░▐▄▄░░░░░░░", "░░░░▌░░░░▄▀▒▒▀▀▀▀▄", "░░░▐░░░░▐▒▒▒▒▒▒▒▒▀▀▄", "░░░▐░░░░▐▄▒▒▒▒▒▒▒▒▒▒▀▄", "░░░░▀▄░░░░▀▄▒▒▒▒▒▒▒▒▒▒▀▄", "░░░░░░▀▄▄▄▄▄█▄▄▄▄▄▄▄▄▄▄▄▀", "░░░░░░░░░░░▌▌░▌▌░░░░░", "░░░░░░░░░░░▌▌░▌▌░░░░░", "░░░░░░░░░▄▄▌▌▄▌▌░░░░░ ."],
              ['░░░░░░░░░░░░░░░░░░░░', '░ВЗГЛЯНИ ░░ВОКРУГ,░░░░░', '░ОГЛЯНИСЬ░НАЗАД!░░░░░░', '░ГУСИ░▄▀▀▀▄░С░ТОБОЮ░░', '░░░░▀░░░◐░▀███▄░░░░░', '░░░░▐░░░░░▐░░░░░░░░░', '░░░░▌░░░░▄▀▒▒▀▀▀▀▄',
                  '░░░▐░░░░▐▒▒▒▒▒▒▒▒▀▀▄', '░░░▐░░░░▐▄▒▒▒▒▒▒▒▒▒▒▀▄', '░░░░▀▄░░░░▀▄▒▒▒▒▒▒▒▒▒▒▀▄', '░░░░░░▀▄▄▄▄▄█▄▄▄▄▄▄▄▄▄▄▄▀▄', '░СВЯЗАТЬСЯ░░▌▌░▌▌░░░░░', '░░░ХОТЯТ░░░░▌▌░▌▌░░░░░', '░░░░░░░░░░░▄▄▌▌▄▌▌░░'],
              ['░░░░░░░▄▀▀▄░░░░░░░░░░░░',
               '░░░░░▄▀▒▒▒▒▀▄░ЗАПУСКАЕМ░░',
               '░░░░░░▀▌▒▒▐▀░░ГУСЕПЕТУХА░░',
               '▄███▀░◐░░░▌░░░РАБОТЯГИ░░░',
               '░░▐▀▌░░░░░▐░░░░░░░░░▄▀▀▀▄▄',
               '░▐░░▐░░░░░▐░░░░░░░░░█░▄█▀',
               '░▐▄▄▌░░░░░▐▄▄░░░░░░█░░▄▄▀▀▀▀▄',
               '░░░░▌░░░░▄▀▒▒▀▀▀▀▄▀░▄▀░▄▄▄▀▀',
               '░░░▐░░░░▐▒▒▒▒▒▒▒▒▀▀▄░░▀▄▄▄░▄',
               '░░░▐░░░░▐▄▒▒▒▒▒▒▒▒▒▒▀▄░▄▄▀▀',
               '░░░░▀▄░░░░▀▄▒▒▒▒▒▒▒▒▒▒▀▄░',
               '░░░░░▀▄▄░░░█▄▄▄▄▄▄▄▄▄▄▄▀▄',
               '░░░░░░░░▀▀▀▄▄▄▄▄▄▄▄▀▀░',
               '░░░░░░░░░░░▌▌░▌▌',
               '░░░░░░░░░▄▄▌▌▄▌▌'],
              ['░░░░░░░░░░░░░░░░░░░░',
               '░ЗАПУСКАЕМ░░ГУСЯ-ГИДРУ░',
               '░░░░░░РАБОТЯГИ░░░░░░░',
               '░░░░░░▄▀▀▀▄░░░░░░░░░',
               '▄███▀░◐░▄▀▀▀▄░░░░░░░',
               '░░▄███▀░◐░░░░▌░░░░░░',
               '░░░▌░▄▀▀▀▄░░░▌░░░░░░',
               '▄███▀░◐░░░▌░░▌░░░░░░',
               '░░░░▌░░░░░▐▄▄▌░░░░░░',
               '░░░░▌░░░░░▐▄▄░░░░░░░',
               '░░░░▌░░░░▄▀▒▒▀▀▀▀▄░░',
               '░░░▐░░░░▐▒▒▒▒▒▒▒▒▀▀▄',
               '░░░▐░░░░▐▄▒▒▒▒▒▒▒▒▒▒▀▄',
               '░░░░▀▄░░░░▀▄▒▒▒▒▒▒▒▒▒▒▀▄',
               '░░░░░░▀▄▄▄▄▄█▄▄▄▄▄▄▄▄▄▄▄▀▄',
               '░░░░░░░░░░░▌▌░▌▌░░░░░',
               '░░░░░░░░░░░▌▌░▌▌░░░░░',
               '░░░░░░░░░▄▄▌▌▄▌▌░░░░░'],
              ['░░░░░░░░░░░░░░░░░░░░░░',
               '░░ЗАПУСКАЕМ░░МОЩНОГО░░░',
               '░░░░░░░ГУСЯ-ГИДРУ░░░░░░░',
               '░░░░░▄▀▀▀▄░░░░░░░░ ▄▄░░',
               '▄███▀░◐░▄▀▀▀▄░░░▄▀░░█░',
               '░░▄███▀░◐░░░░▌▄▀░░▄▀░░',
               '░░░░▐░▄▀▀▀▄░░░░░▄▀░░░░',
               '▄███▀░◐░░░░▌░░░░░▀▄░░░',
               '▄▄░▌░░░░░▐▄▄▀▄▄▀▄▀░░░░░░░▄▄',
               '█░░▀▄░░░░▄▀▒▒▀▀▀▀▄░░░░░▄▀░░█',
               '░▀▄░░▀▄░▐▒▒▒▒▒▒▒▒▀▀▄▄▄▄▀░░▄▀',
               '░░░▀▄░░▀▐▄▒▒▒▒▒▒▒▒▒▒▒▒░░▄▀',
               '░░░▄▀░░░░░▀▄▒▒▒▒▒▒▒▒▒▒▒▀▄',
               '░░░▀▄▀▄▄▀▄▄▄█▄▄▄▄▄▄▄▀▄▄▀▄▀',
               '░░░░░░░▌▌░▌▌░▌▌░▌▌░░▌▌░▌▌░',
               '░░░░░░░▌▌░▌▌░▌▌░▌▌░░▌▌░▌▌░',
               '░░░░░▄▄▌▌▄▌▌▄▌▌▄▌▌░▄▌▌▄▌▌░'],
              ['──────▄▌▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌',
               '───▄▄██▌█░ВЕЗЁМ▄▀▀▀▄░ГУСЕЙ░░░░░░░',
               '───████▌█▄███▀░◐░▄▀▀▀▄░░РАБОТЯГИ░',
               '──██░░█▌█░░▄███▀░◐░░▄▀▀▀▄░░░░░░░',
               '─██░░░█▌█░░░░▐░▄▀▀▀▌░░░░◐░▀███▄░',
               '▄██████▌█▄███▀░◐░░░▌░░░░░▐░░░░░░',
               '███████▌█░░░░▌░░░░░▌░░░░░▐░░░░░░',
               '███████▌█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌',
               '▀(@)▀▀▀▀▀▀▀(@)(@)▀▀▀▀▀▀▀▀▀▀▀▀▀(@)▀(@)',],
              ['░░░░░▄▀▀▀▄▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌',
               '▄███▀░◐░░░▌░ЗАПУСКАЕМ░ГУСЯ-ФУРУ░░░',
               '████▌░░░░░▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌',
               '▀(@)▀▀▀▀▀▀▀(@)(@)▀▀▀▀▀▀▀▀▀▀▀▀▀(@)▀'],
              ['░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░',
               '░░░░ЗАПУСКАЕМ░ГУСЕЙ-РАЗВЕДЧИКОВ░░░░',
               '░░░░░▄▀▀▀▄░░░▄▀▀▀▀▄░░░▄▀▀▀▄░░░░░',
               '▄███▀░◐░░░▌░▐0░░░░0▌░▐░░░◐░▀███▄',
               '░░░░▌░░░░░▐░▌░▐▀▀▌░▐░▌░░░░░▐░░░░',
               '░░░░▐░░░░░▐░▌░▌▒▒▐░▐░▌░░░░░▌░░░░']]
    for i in gooses[random.randint(0, len(gooses)-1)]:
        await cm.broadcast(
            {
                "type": "message",
                "from": "@goose",
                "text": i,
            }
        )


BOTS = {"ping": ping_bot, "dice": dice_bot,
        "weather": weather_bot, "flip": flip_bot, "help": help_bot, "goose": goose_bot}
