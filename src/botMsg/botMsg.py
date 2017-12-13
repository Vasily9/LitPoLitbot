# Раота с запросами
import requests
import json
# Работа бота
from telebot.types import Message, CallbackQuery, InlineQuery

import config

# API для работы бота
TRACK_URL = 'https://api.botan.io/track'
SHORTENER_URL = 'https://api.botan.io/s/'
BOTAN_TOKEN = 'af484e35-7a5c-4c52-97a2-dcba29b12d89'

# Вспомогательная функция для получения и отправки json-запросов
def track(token, uid, message, name='Message'):
    try:
        r = requests.post(
            TRACK_URL,
            params={"token": token, "uid": uid, "name": name},
            data=json.dumps(message),
            headers={'Content-type': 'application/json'},
        )
        return r.json()
	# Работа с ошибками	
    except requests.exceptions.Timeout:
        return False
    except (requests.exceptions.RequestException, ValueError) as e:
        print(e)
        return False

# Читаем введенное
def track_message(uid, msg: Message, name):  # botan tracker
    return track(BOTAN_TOKEN, uid,
                 {msg.from_user.id: {
                     'user': {
                         'username': msg.from_user.username,
                         'first_name': msg.from_user.first_name,
                         'last_name': msg.from_user.last_name
                     },
                     'text': msg.text
                 }
                 },
                 name=name)

# Отправка найденного результата
def track_callback(uid, callback: CallbackQuery, name):
    return track(BOTAN_TOKEN, uid,
                 {callback.from_user.id: {
                     'user': {
                         'username': callback.from_user.username,
                         'first_name': callback.from_user.first_name,
                         'last_name': callback.from_user.last_name
                     },
                     'text': callback.message.text
                 }
                 },
                 name=name)