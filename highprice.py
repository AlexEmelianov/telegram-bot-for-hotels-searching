from telebot.types import Message
import general as g
from datetime import datetime as dt
import os
import csv


def start(message: Message) -> None:
    """
    Меняет порядок сортировки отелей (сначала дорогие) и вызывает цепочку функций из general

    :param message: входящее сообщение
    :type message: Message
    """
    g.chat_id = message.chat.id
    file_path = os.path.join("history", f"{message.from_user.username}.csv")
    if not os.path.isdir("history"):
        os.mkdir("history")

    g.buffer["history"] = [__name__, dt.today().strftime('%H:%M:%S  %d.%m.%Y'), ""]
    g.buffer["sort_order"] = "PRICE_HIGHEST_FIRST"
    g.start(message=message)
