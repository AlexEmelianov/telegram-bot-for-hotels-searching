import telebot as tb

# Telegram bot 'hotels.com explorer' @hotels_com_explorer_bot
bot = tb.TeleBot('5674957505:AAHYD-lzCXY8ZviDoarCW3ZC5-ejgdQMN7k', threaded=False)
chat_id = None
max_n_hotels = 20  # Максимальное количество отелей для вывода пользователю
max_n_photos = 20  # Максимальное количество фотографий для вывода пользователю
buffer = {}        # Хранилище данных

headers = {
    "X-RapidAPI-Key": "b0223e57dfmshcde41c766925241p162c8djsn3d243fb512ac",
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}
emoji_sad = u"\U0001F614"  # U+1F614
emoji_town = u"\U0001F306"  # U+1F306


def check_int(message: tb.types.Message) -> int:
    """
    Проверяет вводимое пользователем число на входимость в диапазон 'buffer["bounds"][0]' - 'buffer["bounds"][1]'
    """
    try:
        number = int(message.text)
        if number < buffer["bounds"][0] or number > buffer["bounds"][1]:
            raise ValueError
    except ValueError:
        bot.send_message(chat_id=message.chat.id,
                         text=f"Я жду от вас число от {buffer['bounds'][0]} до {buffer['bounds'][1]}")
        bot.register_next_step_handler(message=message, callback=check_int)
    else:
        buffer["number"] = number
        buffer["next_func"](message=message)
