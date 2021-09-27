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
URL = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'


bot = Bot(token=(TELEGRAM_TOKEN))
chat_id = CHAT_ID
text = 'Драдути драдути!!!'

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
bot.send_message(chat_id, text)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework.get('status') == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    url = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': (current_timestamp)}
    homework_statuses = requests.get(url, headers=headers, params=payload)
    # print(homework_statuses.json())
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp
    logger.debug('bot is running')
    updater = Updater(token=TELEGRAM_TOKEN)
    updater.start_polling()
    updater.idle()
    while True:
        try:
            homework = get_homeworks(
                current_timestamp)['homeworks'][0]['status']
            send_message(parse_homework_status(homework))
            logger.info('Бот хорош')
            time.sleep(5 * 60)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
