# Использованные модули

# Библиотека для бота
import telebot  
from telebot.types import (InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery, InlineQuery,
                           InlineQueryResultArticle, InputTextMessageContent)

# Библиотека для работы с разными алфавитами
import transliterate  

# Работа с регулярными выражениями
import re

# Работа с сокетами
import ssl

# Работа с журналом
import logging

# Работа со временем
import time

# Созданные файлы

# Вывод и считывание текста ботом
from botMsg import *

# Конфигурация
import config

# Работа с книгами в базе данных
from database.WorkFiles import *

# Таблицы в базе данных
from database.tables import Book

# Работа с пользователем и языками
from database.users import get_user, set_lang_settings

# Получение автоматических сообщений и обновление данных с сервера
from web import Checker

# Переменные бота
elemPage = 5 # Элементов на странице
countList = 9 # Количество пролистываний

# Запуск бота
bot = telebot.AsyncTeleBot(config.TOKEN)

# Отладка
logger = telebot.logger
if config.DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

# Начальная конфигурация	
logging.basicConfig(filename=('../logs/' + str(int(time.time())) + '.txt'), filemode='w')

# Редактируем введенный текст, убираем нечитаемые символы
def EditText(book: Book, type_: str) -> str:  
    name = '' # Название книги
    authors = authors_by_book_id(book.id) # Авторы
    if authors:
        for a in authors:
            name += a.short + '_'
        name += '-_'
    name += book.title
    name = transliterate.translit(name, 'ru', reversed=True)
    name = name.replace('(', '').replace(')', '').replace(',', '').replace('…', '').replace('.', '')
    name = name.replace('’', '').replace('!', '').replace('"', '').replace('?', '').replace('»', '')
    name = name.replace('«', '').replace('\'', '').replace(':', '')
    name = name.replace('—', '-').replace('/', '_').replace('№', 'N')
    name = name.replace(' ', '_').replace('–', '-').replace('á', 'a').replace(' ', '_')
    return name + '.' + type_

	
# Создание клавиш для работы бота
def createButtons(page: int, pages: int, s: str) -> InlineKeyboardMarkup or None:  
    if pages == 1:
        return None
    buttons = InlineKeyboardMarkup() # Создаем инлайн-клавиатуру
    row = []
	# Создаем клавиши
    if page == 1: # Первая страница
        row.append(InlineKeyboardButton('>', callback_data=f'{s}_2'))
        if pages >= countList:
            nextList = min(pages, page + countList)
            row.append(InlineKeyboardButton(f'{nextList} >>',
                                            callback_data=f'{s}_{nextList}')) # Следующая страница
        buttons.row(*row)
    elif page == pages:
        if pages >= countList:
            previousList = max(1, page - countList)
            row.append(InlineKeyboardButton(f'<< {previousList}',
                                            callback_data=f'{s}_{previousList}')) # Предыдущая страница
        row.append(InlineKeyboardButton('<', callback_data=f'{s}_{pages-1}'))
        buttons.row(*row)
    else:
        if pages >= countList:
            nextList = min(pages, page + countList)
            previousList = max(1, page - countList)

            if previousList != page - 1:
                row.append(InlineKeyboardButton(f'<< {previousList}',
                                                callback_data=f'{s}_{previousList}'))

            row.append(InlineKeyboardButton('<', callback_data=f'{s}_{page-1}'))
            row.append(InlineKeyboardButton('>', callback_data=f'{s}_{page+1}'))

            if nextList != page + 1:
                row.append(InlineKeyboardButton(f'{nextList} >>',
                                                callback_data=f'{s}_{nextList}'))
            buttons.row(*row)
        else:
            buttons.row(InlineKeyboardButton('<', callback_data=f'{s}_{page-1}'),
                         InlineKeyboardButton('>', callback_data=f'{s}_{page+1}'))
    return buttons
	

# Запуск бота
@bot.message_handler(commands=['start'])
def start(msg: Message):
    try: 
        _, rq = msg.text.split(' ')
    except ValueError:
        start_msg = ("Привет! Для поиска введите название книги или автора\n")
        r = bot.reply_to(msg, start_msg)
        track_message(msg.from_user.id, msg, 'start')
        r.wait()
    else:
        type_, id_ = rq.split('_')
        bot_send_book(msg, type_, book_id=int(id_))
        track_message(msg.from_user.id, msg, 'get_shared_book')

				
# Поиск книг по названию		
@bot.callback_query_handler(func=lambda x: re.search(r'b_([0-9])+', x.data) is not None)
def bot_search_by_title(callback: CallbackQuery):  
    msg = callback.message
	# Если введено мало символов для поиска
    if len(msg.reply_to_message.text) < 4:
        bot.edit_message_text('Слишком короткий запрос!', chat_id=msg.chat.id, message_id=msg.message_id)
    user = get_user(callback.from_user.id)
    books = books_by_title(msg.reply_to_message.text, user)
	# Если книги не найдены
    if not books:
        bot.edit_message_text('Книги не найдены!', chat_id=msg.chat.id, message_id=msg.message_id)
        track_callback(msg.from_user.id, callback, 'search_by_title')
        return
    r_action = bot.send_chat_action(msg.chat.id, 'typing')
    try:
        _, page = callback.data.split('_')
    except ValueError as err:
        logger.debug(err)
        return
    page = int(page)
	# Разбиение выведенных данных на страницы
    if len(books) % elemPage == 0:
        page_max = len(books) // elemPage
    else:
        page_max = len(books) // elemPage + 1
    msg_text = ''
    for book in books[elemPage * (page - 1):elemPage * page]:
        msg_text += to_send_book(book)
    msg_text += f'<code>Страница {page}/{page_max}</code>'
	# Добавление клавиш
    button = createButtons(page, page_max, 'b')
    if button:
        r = bot.edit_message_text(msg_text, chat_id=msg.chat.id, message_id=msg.message_id, parse_mode='HTML',
                                  reply_markup=button)
    else:
        r = bot.edit_message_text(msg_text, chat_id=msg.chat.id, message_id=msg.message_id, parse_mode='HTML')
    track_callback(msg.from_user.id, callback, 'search_by_title')
    r_action.wait()
    r.wait()


# Поиск книг по автору
@bot.callback_query_handler(func=lambda x: re.search(r'ba_([0-9])+', x.data) is not None)
def bot_books_by_author(callback: CallbackQuery): 
    msg = callback.message
    _, id_ = msg.reply_to_message.text.split('_')
    id_ = int(id_)
    user = get_user(callback.from_user.id)
    books = books_by_author(id_, user)
	# Если книг не найдено
    if not books:
        bot.edit_message_text('Книги не найдены!', chat_id=msg.chat.id, message_id=msg.message_id)
        track_callback(msg.from_user.id, callback, 'search_by_title')
        return
    _, page = callback.data.split('_')
    page = int(page)
    r_action = bot.send_chat_action(msg.chat.id, 'typing')
	# Разбиение найденных результатов на страницы
    if len(books) % elemPage == 0:
        page_max = len(books) // elemPage
    else:
        page_max = len(books) // elemPage + 1
    msg_text = ''
    author = [author_by_id(id_)]
    for book in books[elemPage * (page - 1):elemPage * page]:
        msg_text += to_send_book(book, authors=author)
    msg_text += f'<code>Страница {page}/{page_max}</code>'
	# Добавление клавиш
    button = createButtons(page, page_max, 'ba')
    if button:
        r = bot.edit_message_text(msg_text, chat_id=msg.chat.id, message_id=msg.message_id, parse_mode='HTML',
                                  reply_markup=button)
    else:
        r = bot.edit_message_text(msg_text, chat_id=msg.chat.id, message_id=msg.message_id, parse_mode='HTML')
    track_callback(msg.from_user.id, callback, 'books_by_author')
    r_action.wait()
    r.wait()


# Поиск авторов
@bot.callback_query_handler(func=lambda x: re.search(r'a_([0-9])+', x.data) is not None)
def bot_search_by_authors(callback: CallbackQuery):
    msg = callback.message
    authors = authors_by_name(msg.reply_to_message.text)
	# Если автор не существует в базе
    if not authors:
        r = bot.send_message(msg.chat.id, 'Автор не найден!')
        track_callback(msg.from_user.id, callback, 'search_by_authors')
        r.wait()
        return
    _, page = callback.data.split('_')
    page = int(page)
    r_action = bot.send_chat_action(msg.chat.id, 'typing')
	# Разбиение найденных результатов на страницы
    if len(authors) % elemPage == 0:
        page_max = len(authors) // elemPage
    else:
        page_max = len(authors) // elemPage + 1
    msg_text = ''
    for author in authors[elemPage * (page - 1):elemPage * page]:
        msg_text += author.to_send
    msg_text += f'<code>Страница {page}/{page_max}</code>'
	# Добавление клавиш
    button = createButtons(page, page_max, 'a')
    if button:
        r = bot.edit_message_text(msg_text, chat_id=msg.chat.id, message_id=msg.message_id, parse_mode='HTML',
                                  reply_markup=button)
    else:
        r = bot.edit_message_text(msg_text, chat_id=msg.chat.id, message_id=msg.message_id, parse_mode='HTML')
    track_callback(msg.from_user.id, callback, 'search_by_authors')
    r_action.wait()
    r.wait()

#Поиск авторов по книге
@bot.message_handler(regexp='/a_([0-9])+')
def bot_books_by_author(msg: Message): 
    _, id_ = msg.text.split('_')
    id_ = int(id_)
    user = get_user(msg.from_user.id)
    books = books_by_author(id_, user)
	# Если книги не найдены
    if not books:
        r = bot.reply_to(msg, 'Книги не найдены!')
        track_message(msg.from_user.id, msg, 'books_by_author')
        r.wait()
        return
    r_action = bot.send_chat_action(msg.chat.id, 'typing')
	# Разбиение найденных результатов на страницы
    if len(books) % elemPage == 0:
        page_max = len(books) // elemPage
    else:
        page_max = len(books) // elemPage + 1
    msg_text = ''
    author = [author_by_id(id_)]
    for book in books[0:elemPage]:
        msg_text += to_send_book(book, authors=author)
    msg_text += f'<code>Страница {1}/{page_max}</code>'
	# Добавление клавиш
    button = createButtons(1, page_max, 'ba')
    if button:
        r = bot.reply_to(msg, msg_text, parse_mode='HTML', reply_markup=button)
    else:
        r = bot.reply_to(msg, msg_text, parse_mode='HTML')
    track_message(msg.from_user.id, msg, 'books_by_author')
    r_action.wait()
    r.wait()

# Сравнение данных с базой данных
def send_by_file_id(foo):  
    def try_send(msg, type_, book_id=None):
        if not book_id:
            _, book_id = msg.text.split('_')
            book_id = int(book_id)
		# Проверяем полученный номер с номером в базе данных	
        file_id = get_file_id(book_id, type_) 
		# Если такого файла не существует
        if file_id:
            return foo(msg, type_, book_id=book_id, file_id=file_id.file_id)  
        else:
            return foo(msg, type_, book_id=book_id)
    return try_send
	

# Создание меню
@bot.message_handler(func=lambda message: True)
def search(msg: Message):
	# Клавиши
    button = InlineKeyboardMarkup()
    button.add(InlineKeyboardButton('По названию', callback_data='b_1'),
                 InlineKeyboardButton('По авторам', callback_data='a_1')
                 )
	# Найденные результаты			 
    r = bot.reply_to(msg, 'Поиск: ', reply_markup=button)
    track_message(msg.from_user.id, msg, 'receive_message')
    r.wait()


# Работа бота с сервером
bot.remove_webhook()
if config.WEBHOOK:
    from aiohttp import web
    app = web.Application()
    checker = Checker(bot)

    async def handle(request):
        if request.match_info.get('token') == config.TOKEN:
            request_body_dict = await request.json()
            update = telebot.types.Update.de_json(request_body_dict)
            bot.process_new_updates([update])
            return web.Response()
        else:
            return web.Response(status=403)
			
    app.router.add_post('/{token}/', handle)
    bot.set_webhook(url=config.WEBHOOK_URL_BASE + config.WEBHOOK_URL_PATH,
                    certificate=open(config.WEBHOOK_SSL_CERT, 'r'))
    checker.start()
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.load_cert_chain(config.WEBHOOK_SSL_CERT, config.WEBHOOK_SSL_PRIV)
    try:
        web.run_app(app,
                    host=config.WEBHOOK_LISTEN,
                    port=config.WEBHOOK_PORT,
                    ssl_context=context)
    except KeyboardInterrupt:
        pass
    checker.stop()
    bot.remove_webhook()
else:
    bot.polling()
