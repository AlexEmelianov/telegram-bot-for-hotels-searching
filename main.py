import telebot as tb
from general import bot
import highprice
import lowprice
import bestdeal
import history


@bot.message_handler(commands=["help", "start"])
def help_start_command(message: tb.types.Message) -> None:
	text = "Я помогу подобрать для вас отель. Вы можете отправить мне следующие команды:\n" \
			"/lowprice — вывод самых дешёвых отелей в городе\n" \
			"/highprice — вывод самых дорогих отелей в городе\n" \
			"/bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра\n" \
			"/history — вывод истории поиска отелей\n"
	bot.send_message(chat_id=message.chat.id, text=text)


@bot.message_handler(commands=["lowprice"])
def lowprice_command(message: tb.types.Message) -> None:
	lowprice.start(message=message)


@bot.message_handler(commands=["highprice"])
def highprice_command(message: tb.types.Message) -> None:
	highprice.start(message=message)


@bot.message_handler(commands=["bestdeal"])
def bestdeal_command(message: tb.types.Message) -> None:
	bestdeal.start(message=message)


@bot.message_handler(commands=["history"])
def history_command(message: tb.types.Message) -> None:
	text = history.get_history()
	bot.send_message(chat_id=message.chat.id, text=text)


@bot.message_handler(content_types=['text'])
def get_text_messages(message: tb.types.Message) -> None:
	"""
	Бот принимает текстовые сообщения и выводит ответное приветствие или просьбу написать /help.

	:param message: входящее текстовое сообщение
	:type message: tb.types.Message
	"""
	user_text = message.text.lower()
	if user_text.startswith("привет") or user_text == "/hello-world":
		text = "Привет!"
	else:
		text = "Я тебя не понимаю. Напиши /help."
	bot.send_message(chat_id=message.chat.id, text=text)


if __name__ == '__main__':
	bot.infinity_polling()
