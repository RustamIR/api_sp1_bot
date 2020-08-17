import os
import logging

import requests
import telegram
import time
from dotenv import load_dotenv
from requests.exceptions import RequestException
load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
BOT = telegram.Bot(token=TELEGRAM_TOKEN)
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

def parse_homework_status(homework):
    try:
        homework_name = homework["homework_name"]
    except RequestException as err:
        logging.error('Error: homework_name is "None"')
    homework_status = homework.get('status')
    if homework_status is None:
        return 'Invalid server response'
    if homework.get("status") != "approved":
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = ('Ревьюеру всё понравилось, '
                   'можно приступать к следующему уроку.') 
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        logging.error('Error: current_timestamp is "None"')
        current_timestamp = int(time.time())
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(
            url, 
            headers = HEADERS, 
            params = params
        )
        return homework_statuses.json()
    except RequestException as err:
        logging.debug(err, 'Error getting JSON')


def send_message(message):
    return BOT.send_message(CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(
                        new_homework.get('homeworks')[0]
                    )
                )
            current_timestamp = new_homework.get('current_date')  
            time.sleep(300)  # опрашивать раз в пять минут

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
