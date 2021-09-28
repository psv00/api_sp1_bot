import os
import time
import requests
import logging
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Updater
from logging.handlers import RotatingFileHandler

load_dotenv()


TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
PRAKTIKUM_URL = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
PRAKTIKUM_HEADERS = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}

bot = Bot(token=(TELEGRAM_TOKEN))

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
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if status not in STATUS_HT:
        return 'работа взята в ревью'
    verdict = STATUS_HT[status]
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    try:
        payload = {'from_date': (current_timestamp)}
        homework_statuses = requests.get(
            PRAKTIKUM_URL, headers=PRAKTIKUM_HEADERS, params=payload)
        return homework_statuses.json()
    except Exception as e:
        logger.error(e, exc_info=True)


def send_message(message):
    try:
        return bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as e:
        logger.error(e, exc_info=True)


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
