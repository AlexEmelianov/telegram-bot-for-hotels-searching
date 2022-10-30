import telebot as tb
import general as g


def start(message: tb.types.Message) -> None:
    """
    Меняет порядок сортировки отелей (сначала дорогие) и вызывает цепочку функций из general

    :param message: входящее сообщение
    :type message: tb.types.Message
    """
    g.chat_id = message.chat.id
    g.buffer["sort_order"] = "PRICE_HIGHEST_FIRST"
    g.start(message=message)
