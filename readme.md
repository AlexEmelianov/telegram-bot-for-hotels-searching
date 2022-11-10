# Telegram-бот для анализа сайта Hotels.com
Бот анализирует текущие предложения по отелям в соответствии с критериям,
которые вводит пользователь.

Имя бота: 'hotels.com explorer', username: @hotels_com_explorer_bot

## Установка и запуск
Запуск бота осуществляется после клонирования репозитория и установки необходимых библиотек.

- Установите [Python](https://www.python.org/downloads/)
  (обычно, после этого автоматически устанавливается [pip](https://pip.pypa.io/en/stable/installation/))
- Установите библиотеку [pyTelegramBotAPI](https://pypi.org/project/pyTelegramBotAPI/0.3.0/)
- Установите библиотеку [requests](https://pypi.org/project/requests/)
- Клонируйте проект:
```
git clone https://gitlab.skillbox.ru/aleksei_emelianov_1/python_basic_diploma.git
```
- Запустите бот в командной строке из папки с проектом:
```
cd python_basic_diploma
python main.py
```
*Примечание: для поиска отелей используется открытый [API Hotels](https://rapidapi.com/apidojo/api/hotels4/). 
В данном проекте используется базовый пакет доступа, у которого есть ограничение по
количеству запросов в месяц, а именно — 500. Если вам не хватает запросов для работы с ботом,
то зарегистрируйте несколько аккаунтов или измените пакет доступа. Для этого:*

*1. Зарегистрируйтесь на сайте [rapidapi.com](rapidapi.com)*

*2. Перейдите в [API Hotels](https://rapidapi.com/apidojo/api/hotels4/).*

*3. Нажмите кнопку 'Subscribe to Test'.*

*4. Выберите пакет доступа (Basic - бесплатный).*

*5. Скопируйте значение ключа 'X-RapidAPI-Key' и вставьте его в переменную 'headers' в файле 'general'*

## Использование
Найдите бот в Telegram по имени @hotels_com_explorer_bot
При запущенном Python-скрипте Telegram-бот воспринимает следующие команды:
- /help — помощь по командам бота,
- /lowprice — вывод самых дешёвых отелей в городе,
- /highprice — вывод самых дорогих отелей в городе,
- /bestdeal — вывод отелей, наиболее подходящих по цене и расположению от
центра.
- /history — вывод истории поиска отелей

## Автор проекта
Алексей Емельянов — Python developer
- [Telegram](https://web.telegram.org/k/): @emelianov_alex
- e-mail: emelyanov000@gmail.com