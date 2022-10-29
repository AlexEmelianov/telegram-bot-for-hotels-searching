import telebot as tb
import requests
import json
import re
import datetime as dt
import general as g
from general import bot


def start_low(message: tb.types.Message) -> None:
    """
    Спрашивает пользователя, в каком городе будем искать отель и передает ответ в search_locations

    :param message: входящее сообщение
    :type message: tb.types.Message
    """
    g.chat_id = message.chat.id
    bot.send_message(chat_id=g.chat_id, text=f"В каком городе будем искать отель? {g.emoji_town}")
    bot.register_next_step_handler(message=message, callback=search_locations)


def search_locations(message: tb.types.Message) -> None:
    """
    Ищет города по вводу пользователя. Следующая функция: choose_n_hotels или choose_city.
    Если города не найдены, то ждёт ответ и повторяет поиск.

    :param message: входящее сообщение
    :type message: tb.types.Message
    """
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    params = {"query": message.text, "locale": "ru_RU"}
    bot.send_chat_action(chat_id=g.chat_id, action="typing")
    response = requests.get(url=url, headers=g.headers, params=params)
    if response.status_code != 200:
        bot.send_message(chat_id=g.chat_id, text=f"Ошибка соединения с сервером hotels.com. "
                                                 f"Код = {response.status_code}\n"
                                                 f"Напишите что-нибудь и я попробую ещё раз.")
        bot.register_next_step_handler(message=message, callback=search_locations)
        return

    data = json.loads(response.text)
    g.buffer["cities"] = [(re.sub(r"<.*?>", "", city["caption"]), city["destinationId"])
                          for city in data["suggestions"][0]["entities"]
                          if city["type"] == "CITY"]
    if len(g.buffer["cities"]) == 0:
        bot.send_message(chat_id=g.chat_id, text="По вашему запросу город не найден. Учтите, "
                                                 "что некоторые города исключены из сервиса hotels.com."
                                                 "Введите другое название города.")
        bot.register_next_step_handler(message=message, callback=search_locations)
        return
    elif len(g.buffer["cities"]) == 1:
        bot.send_message(chat_id=g.chat_id, text=f"По вашему запросу найден город: {g.buffer['cities'][0][0]}\n\n"
                                                 f"Сколько отелей будем искать? "
                                                 f"Только не больше {g.max_n_hotels}, пожалуйста.")
        g.buffer["destinationId"] = g.buffer["cities"][0][1]
        # Проверяем вводимое число и переходим в choose_n_hotels
        g.buffer["bounds"] = (1, g.max_n_hotels)
        g.buffer["next_func"] = choose_n_hotels
        bot.register_next_step_handler(message=message, callback=g.check_int)
    else:
        text = f"По вашему запросу найдено городов: {len(g.buffer['cities'])}\n"
        text += "\n".join([f"{ind}. {city[0]}" for ind, city in enumerate(g.buffer["cities"], 1)])
        text += "\n\nВведите номер интересующего вас города или 0 для нового поиска."
        bot.send_message(chat_id=g.chat_id, text=text)
        # Проверяем вводимое число и переходим в choose_city
        g.buffer["bounds"] = (0, len(g.buffer["cities"]))
        g.buffer["next_func"] = choose_city
        bot.register_next_step_handler(message=message, callback=g.check_int)


def choose_city(message: tb.types.Message) -> None:
    """
    Сохраняет город из списка по вводу пользователя. Следующая функция: choose_n_hotels
    Если введён 0, то переходит в search_locations.

    :param message: входящее сообщение
    :type message: tb.types.Message
    """
    num_city = g.buffer["number"]
    if num_city == 0:
        bot.send_message(chat_id=g.chat_id, text="Решили поискать сначала? Ладно, поехали!\n"
                                                 "В каком городе будем искать отель?")
        bot.register_next_step_handler(message=message, callback=search_locations)
        return

    bot.send_message(chat_id=g.chat_id, text=f"Будем искать в городе:\n"
                                             f"{g.buffer['cities'][num_city - 1][0]}\n\n"
                                             f"Сколько отелей найти? "
                                             f"Только не больше {g.max_n_hotels}, пожалуйста.")
    g.buffer["destinationId"] = g.buffer["cities"][num_city - 1][1]
    # Проверяем вводимое число и переходим в choose_n_hotels
    g.buffer["bounds"] = (1, g.max_n_hotels)
    g.buffer["next_func"] = choose_n_hotels
    bot.register_next_step_handler(message=message, callback=g.check_int)


def choose_n_hotels(message: tb.types.Message) -> None:
    """
    Сохраняет количество отелей для поиска по вводу пользователя. Следующая функция: choose_n_photos

    :param message: входящее сообщение
    :type message: tb.types.Message
    """
    g.buffer["n_hotels"] = g.buffer["number"]
    bot.send_message(chat_id=g.chat_id, text=f"Отлично, с количеством отелей разобрались. "
                                             f"Хотите посмотреть фотографии для каждого отеля?\n"
                                             f"Введите количество фотографий (не больше {g.max_n_photos}) "
                                             f"или 0, если без них.")
    # Проверяем вводимое число и переходим в search_hotels
    g.buffer["bounds"] = (0, g.max_n_photos)
    g.buffer["next_func"] = choose_n_photos
    bot.register_next_step_handler(message=message, callback=g.check_int)


def choose_n_photos(message: tb.types.Message) -> None:
    """
    Сохраняет количество фотографий для поиска по вводу пользователя. Следующая функция: choose_dates

    :param message: входящее сообщение
    :type message: tb.types.Message
    """
    g.buffer["n_photos"] = g.buffer["number"]
    if g.buffer["n_photos"] == 0:
        text = "Понял, без фото.\n"
    else:
        text = f"Отлично, буду искать по {g.buffer['n_photos']} фото для каждого отеля.\n"
    text += "Остался самый сложный вопрос. С какого по какое число вы планируете проживать в гостинице?\n" \
            "Введите даты въезда и выезда, как указано в примере:\n" \
            "30.12.2022   07.01.2023"
    bot.send_message(chat_id=g.chat_id, text=text)
    bot.register_next_step_handler(message=message, callback=choose_dates)


def choose_dates(message: tb.types.Message) -> None:
    """
    Сохраняет даты въезда и выезда по вводу пользователя. Следующая функция: search_hotels

    :param message: входящее сообщение
    :type message: tb.types.Message
    """
    g.buffer["dates"] = []
    for date in message.text.strip().split()[:2]:
        date = re.sub(r"\D", "-", date)
        isoformat = '-'.join(date.split('-')[::-1])
        try:
            date = dt.date.fromisoformat(isoformat)
        except ValueError:
            bot.send_message(chat_id=g.chat_id, text="Даты введены неправильно. "
                                                     "Проверьте и введите ещё раз. Пример:\n"
                                                     "30.12.2022   07.01.2023")
            bot.register_next_step_handler(message=message, callbck=choose_dates)
            return
        except Exception as exc:
            bot.send_message(chat_id=g.chat_id, text=f"Неизвестная ошибка: {exc}")
            bot.register_next_step_handler(message=message, callback=choose_dates)
            return
        if len(g.buffer["dates"]) == 0 and dt.date.today() > date:
            bot.send_message(chat_id=g.chat_id, text="Дата въезда уже прошла! Напишите другие даты.")
            bot.register_next_step_handler(message=message, callback=choose_dates)
            return
        if len(g.buffer["dates"]) == 1 and dt.date.fromisoformat(g.buffer["dates"][0]) > date:
            bot.send_message(chat_id=g.chat_id, text="Дата въезда позже даты выезда! Напишите другие даты.")
            bot.register_next_step_handler(message=message, callback=choose_dates)
            return
        g.buffer["dates"].append(isoformat)

    g.buffer["days"] = dt.date.fromisoformat(g.buffer["dates"][1]) - dt.date.fromisoformat(g.buffer["dates"][0])
    bot.send_message(chat_id=g.chat_id, text="Наконец-то, мы закончили с вопросами!")
    search_hotels(message=message)


def search_hotels(message: tb.types.Message) -> None:
    """
    Выводит информацию об отелях. Следующая функция: send_photos

    :param message: входящее сообщение
    :type message: tb.types.Message
    """
    bot.send_message(chat_id=g.chat_id, text="Ищу...")
    bot.send_chat_action(chat_id=g.chat_id, action="typing")

    url = "https://hotels4.p.rapidapi.com/properties/list"
    params = {
        "destinationId": g.buffer["destinationId"],
        "pageNumber": "1",
        "pageSize": f"{g.buffer['n_hotels']}",
        "checkIn": g.buffer["dates"][0],
        "checkOut": g.buffer["dates"][1],
        "adults1": "1",
        "sortOrder": "PRICE",
        "locale": "ru_RU",
        "currency": "USD"
    }
    response = requests.get(url=url, headers=g.headers, params=params)
    if response.status_code != 200:
        bot.send_message(chat_id=g.chat_id, text=f"Ошибка соединения с сервером hotels.com. "
                                                 f"Код = {response.status_code}\n"
                                                 f"Напишите что-нибудь и я попробую ещё раз.")
        bot.register_next_step_handler(message=message, callback=search_hotels)
        return

    data = json.loads(response.text)
    for ind, hotel in enumerate(data["data"]["body"]["searchResults"]["results"], 1):
        name = hotel["name"]
        address = f"{hotel['address'].get('streetAddress', '(без улицы)')}, " \
                  f"{hotel['address'].get('locality', '(без населённого пункта)')}, " \
                  f"{hotel['address'].get('region', '(без региона)')}, " \
                  f"{hotel['address'].get('countryName', '(без страны)')}, " \
                  f"{hotel['address'].get('postalCode', '(без почтового индекса)')}"
        address = re.sub(r",\s*,", ",", address)
        address = re.sub(r",\s*$", "", address)
        landmark = f"{hotel['landmarks'][0]['label'].lower()} расположен в {hotel['landmarks'][0]['distance']}"
        daily_price = hotel.get("ratePlan", "(без указания цены)")
        if isinstance(daily_price, dict):
            daily_price = daily_price["price"]["exactCurrent"]
            price = f"за ночь: {daily_price}$\n"
            price += " " * 24
            price += f"за {g.buffer['days'].days} дней: {daily_price * g.buffer['days'].days :.2f}$"
        else:
            price = daily_price
        link = f"https://www.hotels.com/ho{hotel['id']}"

        result = f"{ind}. {name}\n" \
                 f"Адрес: {address}\n" \
                 f"Удалённость: {landmark}\n" \
                 f"Стоимость: {price}\n" \
                 f"Ссылка на отель: {link}"

        bot.send_message(chat_id=g.chat_id, text=result)
        if g.buffer["n_photos"]:
            g.buffer["hotel_id"] = hotel["id"]
            send_photos()

        if ind == g.buffer["n_hotels"]:
            break
    else:
        bot.send_message(chat_id=g.chat_id, text=f"Сорян, отелей нашлось меньше, чем вы хотели... {g.emoji_sad}")


def send_photos() -> None:
    """
    Отправляет фотографии отелей.

    """
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    params = {"id": g.buffer["hotel_id"]}
    for _ in range(2):
        response = requests.get(url=url, headers=g.headers, params=params)
        if response.status_code == 200:
            break
        bot.send_message(chat_id=g.chat_id, text=f"Не отвечает владелец фотографий... Код = {response.status_code}\n"
                                                 f"Сейчас попробую загрузить фото ещё раз.")
    else:
        bot.send_message(chat_id=g.chat_id, text=f"Оставляю попытки загрузить информацию. Идём дальше.")
        return

    try:
        data = json.loads(response.text)
    except json.decoder.JSONDecodeError:
        bot.send_message(chat_id=g.chat_id, text=f"К сожалению, владелец этого отеля "
                                                 f"не загрузил фотографий... {g.emoji_sad}")
        return

    for ind, image in enumerate(data["hotelImages"], 1):
        photo_link = re.sub(r"{size}", "y", image["baseUrl"])  # Размер 500 х 334
        bot.send_chat_action(chat_id=g.chat_id, action="upload_photo")
        bot.send_photo(chat_id=g.chat_id, photo=photo_link)
        if ind == g.buffer["n_photos"]:
            break
    else:
        bot.send_message(chat_id=g.chat_id, text=f"Сорян, фотографий нашлось меньше, чем вы хотели... {g.emoji_sad}")
