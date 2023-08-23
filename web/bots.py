import random
from typing import Tuple
from fastapi import WebSocket
from connection_manager import cm
from crud import create_message
from sqlalchemy.orm import Session
import requests
import json

from list_city import DICT_CITY


async def ping_bot(db: Session, ws: WebSocket, username: str, text: str):
    text = "Pong"
    msg = create_message(db, "@PingBot", text=text)
    await cm.broadcast(
        {
            "type": "message",
            "from": "@PingBot",
            "text": text,
            "message_id": msg.id,
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
    msg = create_message(db, "@DiceBot", text=text)
    await cm.broadcast(
        {
            "type": "message",
            "from": "@DiceBot",
            "text": text,
            "message_id": msg.id,
        }
    )


async def flip_bot(db: Session, ws: WebSocket, username: str, text: str):
    flip = random.randint(1, 2)
    if flip == 1:
        text = "🌕 head"
    elif flip == 2:
        text = "🌑 tail"
    msg = create_message(db, "@FlipBot", text=text)
    await cm.broadcast(
        {
            "type": "message",
            "from": "@FlipBot",
            "text": text,
            "message_id": msg.id,
        }
    )


async def weather_bot(db: Session, ws: WebSocket, username: str, text: str):
    text = "This is fine 👌"
    msg = create_message(db, "@Weather", text=text)
    await cm.broadcast(
        {
            "type": "message",
            "from": "@Weather",
            "text": text,
            "message_id": msg.id,
        }
    )


async def help_bot(db: Session, ws: WebSocket, username: str, text: str):
    messages = [
        "@ping return Pong",
        "@city_game to play city game"
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
    gooses = [
        [
            "░░░░░░░░░░░░░░░░░░░░",
            "░░░░░ЗАПУСКАЕМ░░░░░░░",
            "░ГУСЯ░▄▀▀▀▄░РАБОТЯГИ░░",
            "▄███▀░◐░░░▌░░░░░░░░░",
            "░░░░▌░░░░░▐░░░░░░░░░",
            "░░░░▐░░░░░▐░░░░░░░░░",
            "░░░░▌░░░░░▐▄▄░░░░░░░",
            "░░░░▌░░░░▄▀▒▒▀▀▀▀▄",
            "░░░▐░░░░▐▒▒▒▒▒▒▒▒▀▀▄",
            "░░░▐░░░░▐▄▒▒▒▒▒▒▒▒▒▒▀▄",
            "░░░░▀▄░░░░▀▄▒▒▒▒▒▒▒▒▒▒▀▄",
            "░░░░░░▀▄▄▄▄▄█▄▄▄▄▄▄▄▄▄▄▄▀",
            "░░░░░░░░░░░▌▌░▌▌░░░░░",
            "░░░░░░░░░░░▌▌░▌▌░░░░░",
            "░░░░░░░░░▄▄▌▌▄▌▌░░░░░ .",
        ],
        [
            "░░░░░░░░░░░░░░░░░░░░",
            "░ВЗГЛЯНИ ░░ВОКРУГ,░░░░░",
            "░ОГЛЯНИСЬ░НАЗАД!░░░░░░",
            "░ГУСИ░▄▀▀▀▄░С░ТОБОЮ░░",
            "░░░░▀░░░◐░▀███▄░░░░░",
            "░░░░▐░░░░░▐░░░░░░░░░",
            "░░░░▌░░░░▄▀▒▒▀▀▀▀▄",
            "░░░▐░░░░▐▒▒▒▒▒▒▒▒▀▀▄",
            "░░░▐░░░░▐▄▒▒▒▒▒▒▒▒▒▒▀▄",
            "░░░░▀▄░░░░▀▄▒▒▒▒▒▒▒▒▒▒▀▄",
            "░░░░░░▀▄▄▄▄▄█▄▄▄▄▄▄▄▄▄▄▄▀▄",
            "░СВЯЗАТЬСЯ░░▌▌░▌▌░░░░░",
            "░░░ХОТЯТ░░░░▌▌░▌▌░░░░░",
            "░░░░░░░░░░░▄▄▌▌▄▌▌░░",
        ],
        [
            "░░░░░░░▄▀▀▄░░░░░░░░░░░░",
            "░░░░░▄▀▒▒▒▒▀▄░ЗАПУСКАЕМ░░",
            "░░░░░░▀▌▒▒▐▀░░ГУСЕПЕТУХА░░",
            "▄███▀░◐░░░▌░░░РАБОТЯГИ░░░",
            "░░▐▀▌░░░░░▐░░░░░░░░░▄▀▀▀▄▄",
            "░▐░░▐░░░░░▐░░░░░░░░░█░▄█▀",
            "░▐▄▄▌░░░░░▐▄▄░░░░░░█░░▄▄▀▀▀▀▄",
            "░░░░▌░░░░▄▀▒▒▀▀▀▀▄▀░▄▀░▄▄▄▀▀",
            "░░░▐░░░░▐▒▒▒▒▒▒▒▒▀▀▄░░▀▄▄▄░▄",
            "░░░▐░░░░▐▄▒▒▒▒▒▒▒▒▒▒▀▄░▄▄▀▀",
            "░░░░▀▄░░░░▀▄▒▒▒▒▒▒▒▒▒▒▀▄░",
            "░░░░░▀▄▄░░░█▄▄▄▄▄▄▄▄▄▄▄▀▄",
            "░░░░░░░░▀▀▀▄▄▄▄▄▄▄▄▀▀░",
            "░░░░░░░░░░░▌▌░▌▌",
            "░░░░░░░░░▄▄▌▌▄▌▌",
        ],
        [
            "░░░░░░░░░░░░░░░░░░░░",
            "░ЗАПУСКАЕМ░░ГУСЯ-ГИДРУ░",
            "░░░░░░РАБОТЯГИ░░░░░░░",
            "░░░░░░▄▀▀▀▄░░░░░░░░░",
            "▄███▀░◐░▄▀▀▀▄░░░░░░░",
            "░░▄███▀░◐░░░░▌░░░░░░",
            "░░░▌░▄▀▀▀▄░░░▌░░░░░░",
            "▄███▀░◐░░░▌░░▌░░░░░░",
            "░░░░▌░░░░░▐▄▄▌░░░░░░",
            "░░░░▌░░░░░▐▄▄░░░░░░░",
            "░░░░▌░░░░▄▀▒▒▀▀▀▀▄░░",
            "░░░▐░░░░▐▒▒▒▒▒▒▒▒▀▀▄",
            "░░░▐░░░░▐▄▒▒▒▒▒▒▒▒▒▒▀▄",
            "░░░░▀▄░░░░▀▄▒▒▒▒▒▒▒▒▒▒▀▄",
            "░░░░░░▀▄▄▄▄▄█▄▄▄▄▄▄▄▄▄▄▄▀▄",
            "░░░░░░░░░░░▌▌░▌▌░░░░░",
            "░░░░░░░░░░░▌▌░▌▌░░░░░",
            "░░░░░░░░░▄▄▌▌▄▌▌░░░░░",
        ],
        [
            "░░░░░░░░░░░░░░░░░░░░░░",
            "░░ЗАПУСКАЕМ░░МОЩНОГО░░░",
            "░░░░░░░ГУСЯ-ГИДРУ░░░░░░░",
            "░░░░░▄▀▀▀▄░░░░░░░░ ▄▄░░",
            "▄███▀░◐░▄▀▀▀▄░░░▄▀░░█░",
            "░░▄███▀░◐░░░░▌▄▀░░▄▀░░",
            "░░░░▐░▄▀▀▀▄░░░░░▄▀░░░░",
            "▄███▀░◐░░░░▌░░░░░▀▄░░░",
            "▄▄░▌░░░░░▐▄▄▀▄▄▀▄▀░░░░░░░▄▄",
            "█░░▀▄░░░░▄▀▒▒▀▀▀▀▄░░░░░▄▀░░█",
            "░▀▄░░▀▄░▐▒▒▒▒▒▒▒▒▀▀▄▄▄▄▀░░▄▀",
            "░░░▀▄░░▀▐▄▒▒▒▒▒▒▒▒▒▒▒▒░░▄▀",
            "░░░▄▀░░░░░▀▄▒▒▒▒▒▒▒▒▒▒▒▀▄",
            "░░░▀▄▀▄▄▀▄▄▄█▄▄▄▄▄▄▄▀▄▄▀▄▀",
            "░░░░░░░▌▌░▌▌░▌▌░▌▌░░▌▌░▌▌░",
            "░░░░░░░▌▌░▌▌░▌▌░▌▌░░▌▌░▌▌░",
            "░░░░░▄▄▌▌▄▌▌▄▌▌▄▌▌░▄▌▌▄▌▌░",
        ],
        [
            "──────▄▌▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌",
            "───▄▄██▌█░ВЕЗЁМ▄▀▀▀▄░ГУСЕЙ░░░░░░░",
            "───████▌█▄███▀░◐░▄▀▀▀▄░░РАБОТЯГИ░",
            "──██░░█▌█░░▄███▀░◐░░▄▀▀▀▄░░░░░░░",
            "─██░░░█▌█░░░░▐░▄▀▀▀▌░░░░◐░▀███▄░",
            "▄██████▌█▄███▀░◐░░░▌░░░░░▐░░░░░░",
            "███████▌█░░░░▌░░░░░▌░░░░░▐░░░░░░",
            "███████▌█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌",
            "▀(@)▀▀▀▀▀▀▀(@)(@)▀▀▀▀▀▀▀▀▀▀▀▀▀(@)▀(@)",
        ],
        [
            "░░░░░▄▀▀▀▄▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌",
            "▄███▀░◐░░░▌░ЗАПУСКАЕМ░ГУСЯ-ФУРУ░░░",
            "████▌░░░░░▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌",
            "▀(@)▀▀▀▀▀▀▀(@)(@)▀▀▀▀▀▀▀▀▀▀▀▀▀(@)▀",
        ],
        [
            "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
            "░░░░ЗАПУСКАЕМ░ГУСЕЙ-РАЗВЕДЧИКОВ░░░░",
            "░░░░░▄▀▀▀▄░░░▄▀▀▀▀▄░░░▄▀▀▀▄░░░░░",
            "▄███▀░◐░░░▌░▐0░░░░0▌░▐░░░◐░▀███▄",
            "░░░░▌░░░░░▐░▌░▐▀▀▌░▐░▌░░░░░▐░░░░",
            "░░░░▐░░░░░▐░▌░▌▒▒▐░▐░▌░░░░░▌░░░░",
        ],
    ]
    for i in gooses[random.randint(0, len(gooses) - 1)]:
        msg = create_message(db, "@GooseBot", text=i)
        await cm.broadcast(
            {
                "type": "message",
                "from": "@GooseBot",
                "text": i,
                "message_id": msg.id,
            }
        )


# бот, который умеет играть в города: создать большой кортеж, выбирать из них 5 городо, оканчивающиеся на определенную букву и случайно брать 1 город, а затем удалять
async def city_game(db: Session, ws: WebSocket, username: str, text: str):
    used_city = set()
    flag = False
    if flag == False and text is not None:
        flag = False
        user_city = text.replace(" ", "")
        user_city = user_city[0].upper() + user_city[1 : len(user_city)]
        cities_ping = DICT_CITY.get(user_city[0].upper())
        # используется для выбора^ города-ответа
        cities_pong = DICT_CITY.get(user_city[-1].upper())
        bot_city = random.choice(cities_pong)

        if user_city not in cities_ping:
            text = "АААААА, нЕту такОго ГоРоДА!!!!!!"
            flag = True

        elif user_city in used_city:
            text = "Вы уже вводили этот город"
            flag = True

        elif text.lower() == "я проиграл":
            text = "Я победил, :)"
            flag = True
        else:
            cities_pong.remove(bot_city)
            cities_ping.remove(user_city)
        if cities_pong == "":
            text = "Вы победили, :("
            flag = True

        used_city.add(user_city)
        used_city.add(bot_city)
        create_message(db, "@CityGame", text=text)
        await cm.broadcast(
            {
                "type": "message",
                "from": "@city_game",
                "text": bot_city,
            }
        )
    else:
        create_message(db, "City_Game", text=text)
        await cm.broadcast(
            {
                "type": "message",
                "from": "@city_game",
                "text": text,
            }
        )

async def music_bot(db: Session, ws: WebSocket, username: str, text: str):
    base = "http://192.168.1.117:5000"
    res = requests.get(f"{base}?name={text}")
    data = json.loads(res.content.decode())
    path = data.get('path')
    if path is None:
        await cm.broadcast(
            {
                "from": "MusicBot",
                "type": "message",
                "text": "Music not found :(",
            }
        )
        return

    await cm.broadcast(
        {
            "from": "MusicBot",
            "type": "message",
            "file": {
                "content_type": "video",
                "path": f"{base}/music/{path}",
            },
        }
    )


BOTS = {
    "ping": ping_bot,
    # "city_game": city_game,
    "dice": dice_bot,
    "weather": weather_bot,
    "flip": flip_bot,
    "help": help_bot,
    "goose": goose_bot,
    "music": music_bot,
}
