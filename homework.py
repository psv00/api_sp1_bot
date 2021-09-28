import os
import time
import requests
import logging
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Updater
from logging.handlers import RotatingFileHandler

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
url = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}

bot = Bot(token=(TELEGRAM_TOKEN))  # иниц и передать как арг в main

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('main.log', maxBytes=50000000, backupCount=5)
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

STATUS_HT = {
    'rejected': 'К сожалению, в работе нашлись ошибки.',
    'approved': 'Ревьюеру всё понравилось, работа зачтена!'}


def parse_homework_status(homework):
    status_d = STATUS_HT['rejected']
    homework_name = homework.get('homework_name')
    if homework.get('status') == 'rejected':
        verdict = status_d
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    try:
        payload = {'from_date': (current_timestamp)}
        homework_statuses = requests.get(url, headers=headers, params=payload)
    # print(homework_statuses.json())
        return homework_statuses.json()
    except Exception as e:
        logger.error(e, exc_info=True)
        time.sleep(5)


def send_message(message):
    try:
        return bot.send_message(CHAT_ID, message)
    except Exception as e:
        logger.error(e, exc_info=True)
        time.sleep(5)


def main():
    logger.debug('bot is running')
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    updater.start_polling()
    updater.idle()
    while True:
        try:
            current_timestamp = int(time.time())
            homework = get_homeworks(
                current_timestamp)['homeworks'][0]['status']
            send_message(parse_homework_status(homework))
            logger.info('Бот хорош')
            time.sleep(5 * 60)

        except Exception as e:
            logger.error(e, exc_info=True)
            time.sleep(5)


if __name__ == '__main__':
    main()
