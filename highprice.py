import telebot as tb
import general as g


def start_high(message: tb.types.Message) -> None:
    """
    Меняет порядок сортировки отелей (сначала дорогие) и вызывает search_locations lowprice.start_low

    :param message: входящее сообщение
    :type message: tb.types.Message
    """
    g.chat_id = message.chat.id
    g.bot.send_message(chat_id=g.chat_id, text="* разработке *")
