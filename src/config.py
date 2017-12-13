# Работа с ботом

# Токен
TOKEN = '477494269:AAGT3pow_m5B1hulqTIYnB-hQNnbPv7RXjU'
# Отладка
DEBUG = False
# Сервер
WEBHOOK = False


# Для работы с сервером
WEBHOOK_HOST = ''
WEBHOOK_PORT = 443
WEBHOOK_LISTEN = '0.0.0.0'
WEBHOOK_SSL_CERT = './cert/webhook_cert.pem'
WEBHOOK_SSL_PRIV = './cert/webhook_pkey.pem'
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}"
WEBHOOK_URL_PATH = f"/{TOKEN}/"

# Работа с базой данных
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'
LIB_DATABASE = 'flibusta'
USERS_DATABASE = 'flibusta_users'
