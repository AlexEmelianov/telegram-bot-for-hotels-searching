# Telegram-бот для анализа сайта Hotels.com
Бот анализирует текущие предложения по отелям в соответствии с критериям,
которые вводит пользователь.

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
*Примечание 1: в файле general.py укажите токен своего бота*

*Примечание 2: для поиска отелей используется открытый [API Hotels](https://rapidapi.com/apidojo/api/hotels4/). 
В файле general.py необходимо указать заголовки, которые вы получите после следующих действий:*

*1. Зарегистрируйтесь на сайте [rapidapi.com](rapidapi.com)*

*2. Перейдите в [API Hotels](https://rapidapi.com/apidojo/api/hotels4/).*

*3. Нажмите кнопку 'Subscribe to Test'.*

*4. Выберите пакет доступа (Basic - бесплатный).*

*5. Скопируйте переменную 'headers' из Code Snippets и вставьте в файл general.py*

## Использование
Найдите бот в Telegram по имени.
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