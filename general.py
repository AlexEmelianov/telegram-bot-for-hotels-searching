import telebot as tb
import requests
import json
import re
import datetime as dt
import os
import csv
import config

bot = tb.TeleBot(config.token, threaded=False)  # Необходимо указать токен вашего бота вместо config.token
headers = config.headers  # Необходимо указать заголовки, которые вы получите после регистрации на rapidapi.com:
                          # 1. Перейти в API Marketplace → категория Travel → Hotels
                          # 2. Нажать кнопку Subscribe to Test
                          # 3. Выбрать бесплатный пакет (Basic)
chat_id = 0
max_n_hotels = 20  # Максимальное количество отелей для вывода пользователю (не больше 25)
max_n_photos = 20  # Максимальное количество фотографий для вывода пользователю
buffer = dict()    # Временное хранилище данных
emoji_sad = u"\U0001F614"  # U+1F614
emoji_town = u"\U0001F306"  # U+1F306


def check_int(message: tb.types.Message) -> None:
    """
    Два варианта:
        - проверяет два вводимых числа, если buffer["bounds"] is None;
        - проверяет одно вводимое число на входимость в диапазон 'buffer["bounds"][0]' - 'buffer["bounds"][1]'

    :param message: входящее сообщение
    :type message: tb.types.Message
    """
    if buffer["bounds"] is None:  # Проверяем два числа
        buffer["number"] = []
        for number in message.text.strip().split()[:2]:
            try:
                buffer["number"].append(abs(int(number)))
            except ValueError:
                bot.send_message(chat_id=chat_id, text="Цифрами, пожалуйста.")
                bot.register_next_step_handler(message=message, callback=check_int)
                return
        if buffer["number"][0] > buffer["number"][1]:
            buffer["number"][0], buffer["number"][1] = buffer["number"][1], buffer["number"][0]

    else:   # Проверяем одно число
        try:
            number = int(message.text)
            if number < buffer["bounds"][0] or number > buffer["bounds"][1]:
                raise ValueError
        except ValueError:
            bot.send_message(chat_id=chat_id, text=f"Я жду от вас число от {buffer['bounds'][0]} "
                                                   f"до {buffer['bounds'][1]}")
            bot.register_next_step_handler(message=message, callback=check_int)
            return
        buffer["number"] = number

    buffer["next_func"](message=message)


def start(message: tb.types.Message) -> None:
    """
    Спрашивает пользователя, в каком городе будем искать отель и передает ответ в search_locations.

    :param message: входящее сообщение
    :type message: tb.types.Message
    """
    bot.send_message(chat_id=chat_id, text=f"В каком городе будем искать отель? {emoji_town}")
    bot.register_next_step_handler(message=message, callback=search_locations)


def search_locations(message: tb.types.Message) -> None:
    """
    Ищет города по вводу пользователя. Если города не найдены, то повторяет поиск.
    Если введен 0, то останавливает поиск.

    :param message: входящее сообщение
    :type message: tb.types.Message
    """
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    if message.text == "0":
        bot.send_message(chat_id=chat_id, text="Останавливаю поиск.")
        return

    bot.send_chat_action(chat_id=chat_id, action="typing")
    response = requests.get(url=url, headers=headers, params={"query": message.text, "locale": "ru_RU"})
    if response.status_code != 200:
        bot.send_message(chat_id=chat_id, text=f"Ошибка соединения с сервером. Код = {response.status_code}\n"
                                               f"Напишите город ещё раз и я попробую повторно.\n"
                                               f"Или напишите 0, чтобы остановить попытки.")
        bot.register_next_step_handler(message=message, callback=search_locations)
        return

    data = json.loads(response.text)
    buffer["cities"] = [(re.sub(r"<.*?>", "", city["caption"]), city["destinationId"])
                        for city in data["suggestions"][0]["entities"]
                        if city["type"] == "CITY"]
    if len(buffer["cities"]) == 0:
        bot.send_message(chat_id=chat_id, text="По вашему запросу город не найден. Учтите, "
                                               "что некоторые города исключены из сервиса hotels.com."
                                               "Введите другое название города.")
        bot.register_next_step_handler(message=message, callback=search_locations)
        return
    elif len(buffer["cities"]) == 1:
        if buffer["sort_order"] == "BEST_SELLER":
            text = "В каком диапазоне цен (в долларах) вы хотите найти отели?" \
                   "Просто напишите пару чисел, например:\n10  30"
            # Проверяем вводимые числа и переходим в choose_prices
            buffer["bounds"] = None
            buffer["next_func"] = choose_prices
        else:
            text = f"Сколько отелей будем искать? Только не больше {max_n_hotels}, пожалуйста."
            # Проверяем вводимое число и переходим в choose_n_hotels
            buffer["bounds"] = (1, max_n_hotels)
            buffer["next_func"] = choose_n_hotels

        bot.send_message(chat_id=chat_id, text=f"По вашему запросу найден город: {buffer['cities'][0][0]}\n\n{text}")
        buffer["destinationId"] = buffer["cities"][0][1]
        bot.register_next_step_handler(message=message, callback=check_int)
    else:
        text = f"По вашему запросу найдено городов: {len(buffer['cities'])}\n"
        text += "\n".join([f"{ind}. {city[0]}" for ind, city in enumerate(buffer["cities"], 1)])
        text += "\n\nВведите номер интересующего вас города или 0 для нового поиска."
        bot.send_message(chat_id=chat_id, text=text)
        # Проверяем вводимое число и переходим в choose_city
        buffer["bounds"] = (0, len(buffer["cities"]))
        buffer["next_func"] = choose_city
        bot.register_next_step_handler(message=message, callback=check_int)


def choose_city(message: tb.types.Message) -> None:
    """
    Сохраняет город из списка по вводу пользователя. Если введён 0, то переходит в search_locations.

    :param message: входящее сообщение
    :type message: tb.types.Message
    """
    num_city = buffer["number"]
    if num_city == 0:
        bot.send_message(chat_id=chat_id, text="Решили поискать сначала? Ладно, поехали!\n"
                                               "В каком городе будем искать отель?")
        bot.register_next_step_handler(message=message, callback=search_locations)
        return

    if buffer["sort_order"] == "BEST_SELLER":
        text = "В каком диапазоне цен (в долларах за ночь) вы хотите найти отели?" \
               "Просто напишите пару чисел, например:\n10  30"
        # Проверяем вводимые числа и переходим в choose_prices
        buffer["bounds"] = None
        buffer["next_func"] = choose_prices
    else:
        text = f"Сколько отелей будем искать? Только не больше {max_n_hotels}, пожалуйста."
        # Проверяем вводимое число и переходим в choose_n_hotels
        buffer["bounds"] = (1, max_n_hotels)
        buffer["next_func"] = choose_n_hotels

    bot.send_message(chat_id=chat_id, text=f"Будем искать в городе:\n"
                                           f"{buffer['cities'][num_city - 1][0]}\n\n{text}")
    buffer["destinationId"] = buffer["cities"][num_city - 1][1]
    bot.register_next_step_handler(message=message, callback=check_int)


def choose_prices(message: tb.types.Message) -> None:
    """
    Сохраняет диапазон цен (в долларах за ночь), в пределах которого будет происходить поиск отелей.

    :param message: входящее сообщение
    :type message: tb.types.Message
    """
    buffer["prices"] = buffer["number"]
    bot.send_message(chat_id=chat_id, text="Теперь напишите ещё два числа. Я буду искать отели в этом диапазоне "
                                           "расстояний (между отелем и центром города, в километрах).")
    # Проверяем вводимые числа и переходим в choose_distances
    buffer["next_func"] = choose_distances
    bot.register_next_step_handler(message=message, callback=check_int)


def choose_distances(message: tb.types.Message) -> None:
    """
    Сохраняет диапазон расстояний между отелем и центром города (в километрах),
    в пределах которого будет происходить поиск отелей.

    :param message: входящее сообщение
    :type message: tb.types.Message
    """
    buffer["distances"] = buffer["number"]
    bot.send_message(chat_id=chat_id, text=f"Примечание: я буду пропускать отели, для которых не указана цена и "
                                           f"расстояние до центра города.\n"
                                           f"Сколько отелей будем искать? Только не больше {max_n_hotels}, пожалуйста.")
    # Проверяем вводимое число и переходим в choose_n_hotels
    buffer["bounds"] = (1, max_n_hotels)
    buffer["next_func"] = choose_n_hotels
    bot.register_next_step_handler(message=message, callback=check_int)


def choose_n_hotels(message: tb.types.Message) -> None:
    """
    Сохраняет количество отелей для поиска.

    :param message: входящее сообщение
    :type message: tb.types.Message
    """
    buffer["n_hotels"] = buffer["number"]
    bot.send_message(chat_id=chat_id, text=f"Отлично, с количеством отелей разобрались. "
                                           f"Хотите посмотреть фотографии для каждого отеля?\n"
                                           f"Введите количество фотографий (не больше {max_n_photos}) "
                                           f"или 0, если без них.")
    # Проверяем вводимое число и переходим в choose_n_photos
    buffer["bounds"] = (0, max_n_photos)
    buffer["next_func"] = choose_n_photos
    bot.register_next_step_handler(message=message, callback=check_int)


def choose_n_photos(message: tb.types.Message) -> None:
    """
    Сохраняет количество фотографий для поиска.

    :param message: входящее сообщение
    :type message: tb.types.Message
    """
    buffer["n_photos"] = buffer["number"]
    if buffer["n_photos"] == 0:
        text = "Понял, без фото.\n"
    else:
        text = f"Отлично, буду искать по {buffer['n_photos']} фото для каждого отеля.\n"
    text += "Остался самый сложный вопрос. С какого по какое число вы планируете проживать в гостинице?\n" \
            "Введите даты въезда и выезда, как указано в примере:\n" \
            "30.12.2022   07.01.2023"
    markup = tb.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(tb.types.KeyboardButton("Мне всё равно.."))
    bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
    bot.register_next_step_handler(message=message, callback=choose_dates)


def choose_dates(message: tb.types.Message) -> None:
    """
    Сохраняет даты въезда и выезда для поиска.

    :param message: входящее сообщение
    :type message: tb.types.Message
    """
    if message.text == "Мне всё равно..":
        bot.send_message(chat_id=chat_id, text="Понимаю. Найду отели на неделю вперед.",
                         reply_markup=tb.types.ReplyKeyboardRemove())
        check_in = dt.date.today()
        check_out = dt.date.today() + dt.timedelta(days=7)
        buffer["dates"] = (check_in.isoformat(), check_out.isoformat())
    else:
        buffer["dates"] = []
        for date in message.text.strip().split()[:2]:
            date = re.sub(r"\D", "-", date)
            isoformat = '-'.join(date.split('-')[::-1])
            try:
                date = dt.date.fromisoformat(isoformat)
            except ValueError:
                bot.send_message(chat_id=chat_id, text="Даты введены неправильно. "
                                                       "Проверьте и введите ещё раз. Пример:\n"
                                                       "30.12.2022   07.01.2023")
                bot.register_next_step_handler(message=message, callback=choose_dates)
                return
            except Exception as exc:
                bot.send_message(chat_id=chat_id, text=f"Неизвестная ошибка: {exc}. Попробуйте ещё раз.")
                bot.register_next_step_handler(message=message, callback=choose_dates)
                return
            if len(buffer["dates"]) == 0 and dt.date.today() > date:
                bot.send_message(chat_id=chat_id, text="Дата въезда уже прошла! Напишите другие даты.")
                bot.register_next_step_handler(message=message, callback=choose_dates)
                return
            if len(buffer["dates"]) == 1 and dt.date.fromisoformat(buffer["dates"][0]) > date:
                bot.send_message(chat_id=chat_id, text="Дата въезда позже даты выезда! Напишите другие даты.")
                bot.register_next_step_handler(message=message, callback=choose_dates)
                return
            buffer["dates"].append(isoformat)
        bot.send_message(chat_id=chat_id, text="Наконец-то, мы закончили с вопросами!",
                         reply_markup=tb.types.ReplyKeyboardRemove())

    buffer["days"] = dt.date.fromisoformat(buffer["dates"][1]) - dt.date.fromisoformat(buffer["dates"][0])
    buffer["days"] = buffer["days"].days
    bot.send_message(chat_id=chat_id, text="Ищу...")
    bot.send_chat_action(chat_id=chat_id, action="typing")

    buffer["found_hotels"] = 0
    for cur_page in range(1, 11):
        if search_hotels(cur_page):
            break

    bot.send_message(chat_id=chat_id, text="Поиск окончен.")
    if buffer["found_hotels"] == 0:
        buffer["history"][2] += "(не нашлось)"

    with open(os.path.join("history", f"{message.from_user.username}.csv"), "a", encoding="utf8") as file:
        writer = csv.writer(file)
        writer.writerow(buffer["history"])
    buffer.clear()


def search_hotels(cur_page: int) -> bool:
    """
    Выводит информацию об отелях.

    :param cur_page: текущая страница поиска
    :type cur_page: int
    :return: True, if the search is over
    :rtype: bool
    """

    url = "https://hotels4.p.rapidapi.com/properties/list"
    params = {
        "destinationId": buffer["destinationId"],
        "pageNumber": f"{cur_page}",
        "pageSize": 25,  # 25 - максимально возможный размер на одной странице
        "checkIn": buffer["dates"][0],
        "checkOut": buffer["dates"][1],
        "adults1": "1",
        "sortOrder": buffer["sort_order"],
        "locale": "ru_RU",
        "currency": "USD"
    }
    for _ in range(3):
        response = requests.get(url=url, headers=headers, params=params)
        if response.status_code == 200:
            break
        bot.send_message(chat_id=chat_id, text=f"Не отвечает сервер... Код = {response.status_code}\nПробую ещё раз.")
    else:
        bot.send_message(chat_id=chat_id, text="Оставляю попытки загрузить информацию.")
        return True

    data = json.loads(response.text)
    if len(data["data"]["body"]["searchResults"]["results"]) == 0:
        bot.send_message(chat_id=chat_id, text="Странно, не нашлось ни одного отеля.")
        return True

    for hotel in data["data"]["body"]["searchResults"]["results"]:
        daily_price = hotel.get("ratePlan", "(без указания цены)")
        if isinstance(daily_price, dict):
            daily_price = daily_price["price"]["exactCurrent"]
            price = f"за ночь: {daily_price}$\n"
            price += " " * 24
            price += f"за {buffer['days']} дней: {daily_price * buffer['days'] :.2f}$"
        else:
            price = daily_price

        try:
            if buffer["sort_order"] == "BEST_SELLER" and \
                    not (buffer["prices"][0] <= daily_price <= buffer["prices"][1]):
                continue
        except TypeError:
            continue

        distance = re.sub(",", ".", hotel['landmarks'][0]['distance'].split()[0])
        try:
            if buffer["sort_order"] == "BEST_SELLER" and \
                    not (buffer["distances"][0] <= float(distance) <= buffer["distances"][1]):
                continue
        except ValueError:
            continue

        if isinstance(hotel['landmarks'][0], dict):
            landmark = f"{hotel['landmarks'][0]['label'].lower()} расположен в {hotel['landmarks'][0]['distance']}"
        else:
            landmark = "(нет информации)"

        name = hotel["name"]
        address = f"{hotel['address'].get('streetAddress', '(без улицы)')}, " \
                  f"{hotel['address'].get('locality', '(без населённого пункта)')}, " \
                  f"{hotel['address'].get('region', '(без региона)')}, " \
                  f"{hotel['address'].get('countryName', '(без страны)')}, " \
                  f"{hotel['address'].get('postalCode', '(без почтового индекса)')}"
        address = re.sub(r",\s*,", ",", address)
        address = re.sub(r",\s*$", "", address)
        link = f"https://www.hotels.com/ho{hotel['id']}"

        buffer["found_hotels"] += 1
        text = f"{buffer['found_hotels']}. {name}\n" \
               f"Адрес: {address}\n" \
               f"Удалённость: {landmark}\n" \
               f"Стоимость: {price}\n" \
               f"Ссылка на отель: {link}\n"
        bot.send_message(chat_id=chat_id, text=text)
        buffer["history"][2] += f"{text}"  # Дозапись истории во временное хранилище
        if buffer["n_photos"]:
            send_photos(hotel["id"])

        if buffer["found_hotels"] == buffer["n_hotels"]:
            return True

    if buffer["found_hotels"] == 0:
        bot.send_message(chat_id=chat_id, text=f"Просмотрено {cur_page * params['pageSize']} отелей. "
                                               f"Условиям ни один не подходит.")
        bot.send_chat_action(chat_id=chat_id, action="typing")
    return False


def send_photos(hotel_id: str) -> None:
    """
    Отправляет фотографии отелей.

    :param hotel_id: hotel id
    :type hotel_id: str
    """

    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    for _ in range(3):
        response = requests.get(url=url, headers=headers, params={"id": hotel_id})
        if response.status_code == 200:
            break
        bot.send_message(chat_id=chat_id, text=f"Не отвечает владелец фотографий... Код = {response.status_code}\n")
    else:
        bot.send_message(chat_id=chat_id, text=f"Оставляю попытки загрузить информацию. Идём дальше.")
        return

    try:
        data = json.loads(response.text)
    except json.decoder.JSONDecodeError:
        bot.send_message(chat_id=chat_id, text=f"К сожалению, владелец отеля не загрузил фотографий... {emoji_sad}")
        return
    except Exception as exc:
        bot.send_message(chat_id=chat_id, text=f"Неизвестная ошибка: {exc}")
        return

    for ind, image in enumerate(data["hotelImages"], 1):
        photo_link = re.sub(r"\{size}", "y", image["baseUrl"])  # Размер 500 х 334
        bot.send_chat_action(chat_id=chat_id, action="upload_photo")
        bot.send_photo(chat_id=chat_id, photo=photo_link)
        if ind == buffer["n_photos"]:
            break
    else:
        bot.send_message(chat_id=chat_id, text=f"Сорян, фотографий нашлось меньше, чем вы хотели... {emoji_sad}")
