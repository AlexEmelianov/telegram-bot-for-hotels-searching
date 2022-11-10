from os import path
from telebot.types import Message
import general as g


def start(message: Message) -> None:
    """
    Открывает файл с историей пользователя и выводит его содержимое

    :param message: входящее сообщение
    :type message: Message
    """

    file_path = path.join("history", f"{message.from_user.username}")
    if not path.isdir("history") or not path.isfile(file_path):
        g.bot.send_message(chat_id=message.chat.id, text="История пуста.")
        return
    with open(file_path, "r", encoding="utf8") as file:
        history = file.read()
    for each_search in history.split(g.sep_history):
        if len(each_search) != 0:
            g.bot.send_message(chat_id=message.chat.id, text=each_search)
