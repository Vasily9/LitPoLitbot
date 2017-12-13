# Для работа с базой данных
from pony.orm import *

l_db = Database()
u_db = Database()

#Книга в базе данных
class Book(l_db.Entity):
    id = PrimaryKey(int)
    title = Required(str, 256)
    authors = Set('Author', reverse='books')
    lang = Optional(str, 2)
    file_type = Optional(str, 4)

#Номер книги в базе данных
class FileId(l_db.Entity):
    book_id = Required(int)
    file_type = Required(str, 4)
    file_id = PrimaryKey(str, 64)

#Автор	
class Author(l_db.Entity):
    id = PrimaryKey(int)
    first_name = Optional(str, 99)
    last_name = Optional(str, 99)
    middle_name = Optional(str, 99)
    books = Set(Book, reverse='authors')

	#Полное имя автора
    @property
    def normal_name(self) -> str:
        temp = ''
        if self.last_name:
            temp = self.last_name
        if self.first_name:
            if temp:
                temp += " "
            temp += self.first_name
        if self.middle_name:
            if temp:
                temp += " "
            temp += self.middle_name
        if temp:
            return temp

	#Сокращенное имя автора		
    @property
    def short(self) -> str:
        temp = ''
        if self.last_name:
            temp += self.last_name
        if self.first_name:
            if temp:
                temp += " "
            temp += self.first_name[0]
        if self.middle_name:
            if temp:
                temp += " "
            temp += self.middle_name[0]
        return temp

	#Отправка имени	
    @property
    def to_send(self) -> str:
        return f'рџ‘¤ <b>{self.normal_name}</b>\n/a_{self.id}\n\n'

#Пользователь
class User(u_db.Entity):
    id = PrimaryKey(int)
    allow_be = Required(bool, default=True)
    allow_uk = Required(bool, default=True)
