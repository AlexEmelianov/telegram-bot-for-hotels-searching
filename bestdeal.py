import telebot as tb
import general as g


def start(message: tb.types.Message) -> None:
    """
    Меняет порядок сортировки отелей (лучшее предложение) и вызывает цепочку функций из general

    :param message: входящее сообщение
    :type message: tb.types.Message
    """
    g.chat_id = message.chat.id
    g.buffer["sort_order"] = "BEST_SELLER"
    g.buffer["cur_page"] = 1
    g.buffer["found_hotels"] = 0
    g.start(message=message)
