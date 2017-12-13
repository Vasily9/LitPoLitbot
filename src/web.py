# Работа с многопоточностью
import threading
# Работа со временем
import time
# Работа с ботом
from telebot import logger
# Работа с ошибками
from requests import RequestException

import config

# Подключения бота к серверу и отслеживание ошибок
class Checker(threading.Thread):
    def __init__(self, bot):
        threading.Thread.__init__(self)
        self.bot = bot
        self.last_update = time.time()
        self.exit = threading.Event()
	# Запуск
    def run(self):
        self.exit.clear()
        time.sleep(30)
        while True:
            if self.exit.is_set():
                break
            self.check()
            self.exit.wait(300)
	# Обновление
    def update(self):
        self.last_update = time.time()
	# Проверка
    def check(self):
        try:
            info = self.bot.get_webhook_info()
        except RequestException as e:
            if config.DEBUG:
                logger.debug(e)
            self.update_webhook()
            self.update()
        else:
            if info.pending_update_count > 10:
                self.update_webhook()
                self.update()

	# Обновление работы с сервером			
    def update_webhook(self):
        self.bot.remove_webhook()
        time.sleep(3)
        self.bot.set_webhook(url=config.WEBHOOK_URL_BASE + config.WEBHOOK_URL_PATH,
                             certificate=open(config.WEBHOOK_SSL_CERT, 'r'))
	#Остановка
    def stop(self):
        print('<< Closing webhook checker... >>')
        self.exit.set()
