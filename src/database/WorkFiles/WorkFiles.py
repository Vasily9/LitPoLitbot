# Таблицы из базы данных
from ..tables import *
# Работа с базой данных
from pony.orm import *
# Случайный выбор
from random import choice
# Работа с регулярными выражениями
import re

import config

# Подключение к базе данных
l_db.bind('mysql', host=config.MYSQL_HOST, user=config.MYSQL_USER, passwd=config.MYSQL_PASSWORD,
          db=config.LIB_DATABASE)
l_db.generate_mapping(create_tables=True)

# Установка языка
def lang_filter(books, user):
    langs = ['ru']
    if user.allow_uk:
        langs.append('uk')
    if user.allow_be:
        langs.append('be')
    return [book for book in books if book.lang in langs]

# Сортировка наименований по алфавиту
def sort_by_alphabet(obj: Book) -> str:
    if obj.title:
        return obj.title.replace('«', '').replace('»', '').replace('"', '')
    else:
        return ''

# Сортировка по количеству книг
def sort_by_books_count(obj):
    return obj.books.count()

# Поиск для корректной длины наименований
def for_search(arg):
    res = ''
    for r in re.findall(r'([\w]+)', arg):
        if len(r) >= 3:
            res += f'+{r} '
    return res

# Вывод найденной книги
@db_session
def to_send_book(book, authors=None):
    res = f'<b>{book.title}</b>\n'
    authors = authors if authors else authors_by_book_id(book.id)
    if authors:
        for a in authors:
            res += f'<b>{a.normal_name}</b>\n'
    else:
        res += '\n'
    return res +f'\n' 
			  
# Поиск по названию книги					  
@db_session
def books_by_title(title, user):
    if title:
        title = for_search(title)
    return lang_filter(Book.select_by_sql(
        "SELECT * FROM book WHERE MATCH (title) AGAINST ($title IN BOOLEAN MODE)"), user)

# Сортировка книг по автору
@db_session
def books_by_author(id_, user):
    return sorted(lang_filter(select(b for a in Author if a.id == id_ for b in a.books)[:], user),
                  key=sort_by_alphabet)


# Выборка авторов
@db_session
def authors_by_name(name):
    if name:
        name = for_search(name)
    return sorted(Author.select_by_sql(
        "SELECT * FROM author WHERE MATCH (first_name, middle_name, last_name) AGAINST ($name IN BOOLEAN MODE)"),
                  key=sort_by_books_count, reverse=True)

# Получение номера книги в базе данных
@db_session
def book_by_id(id_):
    return get(b for b in Book if b.id == id_)

# Проверка номера книги в базе данных
@db_session
def get_file_id(book_id, file_type):
    return get(f for f in FileId if f.book_id == book_id and f.file_type == file_type)

# Выбор книги по автору	
@db_session
def authors_by_book_id(id_):
    return select(a for b in Book if b.id == id_ for a in b.authors)[:]

# Номер автора
@db_session
def author_by_id(id_):
    return get(a for a in Author if a.id == id_)

