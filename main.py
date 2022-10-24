import telebot as tb
import highprice
import lowprice
import bestdeal
import history


if __name__ != '__main__':
	exit(0)

# Telegram bot 'hotels.com explorer' @hotels_com_explorer_bot
bot = tb.TeleBot('5674957505:AAHYD-lzCXY8ZviDoarCW3ZC5-ejgdQMN7k')


@bot.message_handler(content_types=['text'])
def get_text_messages(message: tb.types.Message) -> None:
	"""
	Telegram бот выводит информацию об отелях (hotels.com) в соответствии с ответами пользователя.

	:param message: входящее сообщение
	:type message: tb.types.Message
	"""
	user_text = message.text.lower()
	if user_text.startswith("привет") or user_text == "/hello-world":
		text = "Привет!"
	elif user_text == "/help":
		text = "Я помогу подобрать для вас отель. Вы можете отправить мне следующие команды:\n" \
				"/lowprice — вывод самых дешёвых отелей в городе\n" \
				"/highprice — вывод самых дорогих отелей в городе\n" \
				"/bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра\n" \
				"/history — вывод истории поиска отелей\n"
	elif user_text == '/lowprice':
		text = lowprice.get_lowprice()
	elif user_text == '/highprice':
		text = highprice.get_highprice()
	elif user_text == '/bestdeal':
		text = bestdeal.get_bestdeal()
	elif user_text == '/history':
		text = history.get_history()
	else:
		text = "Я тебя не понимаю. Напиши /help."
	bot.send_message(message.from_user.id, text)


bot.polling(none_stop=True, interval=0)
