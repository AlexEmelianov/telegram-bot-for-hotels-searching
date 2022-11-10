from telebot.types import Message
import general as g
from datetime import datetime as dt


def start(message: Message) -> None:
    """
    Меняет порядок сортировки отелей (сначала дорогие) и вызывает цепочку функций из general

    :param message: входящее сообщение
    :type message: Message
    """
    g.chat_id = message.chat.id
    g.buffer["history"] = f"Команда: {__name__}\n" \
                          f"Время: {dt.today().strftime('%H:%M:%S  %d.%m.%Y')}\n" \
                          f"Список отелей:"
    g.buffer["sort_order"] = "PRICE_HIGHEST_FIRST"
    g.start(message=message)
