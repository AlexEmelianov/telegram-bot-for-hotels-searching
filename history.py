from os import path
from telebot.types import Message
import general as g
import csv


def start(message: Message) -> None:
    """
    Открывает файл с историей пользователя и выводит его содержимое

    :param message: входящее сообщение
    :type message: Message
    """

    file_path = path.join("history", f"{message.from_user.username}.csv")
    if not path.isdir("history") or not path.isfile(file_path):
        g.bot.send_message(chat_id=message.chat.id, text="История пуста.")
        return
    with open(file_path, "r", encoding="utf8") as file:
        reader = csv.reader(file)
        for each_search in reader:
            if len(each_search) != 0:
                text = f"Команда: {each_search[0]}\n" \
                       f"Время: {each_search[1]}\n" \
                       f"Отели:\n{each_search[2]}"
                g.bot.send_message(chat_id=message.chat.id, text=text)
