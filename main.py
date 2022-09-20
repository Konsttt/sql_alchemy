import json

import sqlalchemy
from sqlalchemy.orm import sessionmaker

from models import create_tables, Publisher, Book, Stock, Shop, Sale


# Функция запрос. Задание 2. Вывод магазинов, где продаются книги конкретного издателя/автора
def select_shop_by_publ(name):
    subq1 = session.query(Book).join(Publisher).filter(Publisher.name == name).subquery()
    subq2 = session.query(Stock).join(subq1, Stock.id_book == subq1.c.id).subquery()
    return session.query(Shop).join(subq2, Shop.id == subq2.c.id_shop).all()


if __name__ == "__main__":

    DSN = 'postgresql://postgres:Cgfc29Z+@localhost:5432/orm_alchemy_db'  # url для движка
    engine = sqlalchemy.create_engine(DSN)  # Движок абстракция - объект, который может подключиться к БД

    create_tables(engine)

    Session = sessionmaker(bind=engine)  # создали класс Session, экземпляры которого могут подключаться к БД
    session = Session()  # объект класса Session, для подключения запросов и т.д. к БД. Наподобие cursor из psycopg2

    # Заполнение таблиц БД из json-файла.__________________________________________________________________________
    with open('tests_data.json', 'r') as fd:
        data = json.load(fd)

    for record in data:
        model = {
            'publisher': Publisher,
            'shop': Shop,
            'book': Book,
            'stock': Stock,
            'sale': Sale,
        }[record.get('model')]  # теперь model это Класс, берётся значение из json
        session.add(model(**record.get('fields')))  # Здесь в add() создана объект-строка.
        # !!! Убрал id=record.get('pk') - т.к. далее вручную заполнение без id и был конфликт, т.к. почему-то,
        # id-шники не продолжались, а снова начинались с 1.
        # Готовая для записи в БД вида: class1 = Class(id=..., field1=... , field2=..., ...  , fieldn=...)
        # id берётся из json по ключу 'pk' - убрал, поля берутся по ключу 'fields', и вот здесь
        # высший пилотаж, ввиду того что полей в разных таблицах разное кол-во, то используется ** - распаковка словаря
        # в аргументы ключевых слов при вызове функции. (* - распаковка списка, ** - распаковка словаря)
    session.commit()

    # Заполнение БД вручную___________________________________________________________________________________________
    publisher1 = Publisher(name='Иван Тургенев')
    publisher2 = Publisher(name='Лев Толстой')
    publisher3 = Publisher(name='Иван Шмелёв')
    session.add_all([publisher1, publisher2, publisher3])
    session.commit()

    book1 = Book(title='Отцы и дети', id_publisher=publisher1.id)
    book2 = Book(title='Война и мир', id_publisher=publisher2.id)
    book3 = Book(title='Записки охотника', id_publisher=publisher1.id)
    book4 = Book(title='Детство. Отрочество. Юность.', id_publisher=publisher2.id)
    book5 = Book(title='Лето Господне', id_publisher=publisher3.id)
    book6 = Book(title='Куликово поле', id_publisher=publisher3.id)
    session.add_all([book1, book2, book3, book4, book5, book6])
    session.commit()

    shop1 = Shop(name='Полянка')
    shop2 = Shop(name='Читай город')
    session.add_all([shop1, shop2])
    session.commit()

    stock1 = Stock(id_book=book1.id, id_shop=shop1.id, count=100)
    stock2 = Stock(id_book=book2.id, id_shop=shop1.id, count=150)
    stock3 = Stock(id_book=book3.id, id_shop=shop1.id, count=50)
    stock4 = Stock(id_book=book4.id, id_shop=shop1.id, count=75)
    # stock5 = Stock(id_book=book5.id, id_shop=shop1.id, count=80)
    # stock6 = Stock(id_book=book6.id, id_shop=shop1.id, count=90)
    stock7 = Stock(id_book=book1.id, id_shop=shop2.id, count=111)
    stock8 = Stock(id_book=book2.id, id_shop=shop2.id, count=151)
    stock9 = Stock(id_book=book3.id, id_shop=shop2.id, count=51)
    stock10 = Stock(id_book=book4.id, id_shop=shop2.id, count=71)
    stock11 = Stock(id_book=book5.id, id_shop=shop2.id, count=81)
    stock12 = Stock(id_book=book6.id, id_shop=shop2.id, count=91)
    session.add_all([stock1, stock2, stock3, stock4,  # stock5, stock6,
                     stock7, stock8, stock9, stock10, stock11, stock12])
    session.commit()

    sale1 = Sale(price=1000.00, date_sale='2022-09-19', id_stock=stock1.id, count=5)
    sale2 = Sale(price=1000.00, date_sale='2022-08-19', id_stock=stock2.id, count=3)
    sale3 = Sale(price=1000.00, date_sale='2022-07-19', id_stock=stock10.id, count=7)
    session.add_all([sale1, sale2, sale3])
    session.commit()

    # Запросы к БД.___________________________________________________________________________________________________
    # Вывести все книги
    for c in session.query(Book).all():
        print(c)
    print('_'*100)

    # Вывести предложения с количеством книг больше 90
    for c in session.query(Stock).filter(Stock.count > 90).all():
        print(c)
    print('_' * 100)

    # Вывести книги со словом "лето"
    for c in session.query(Book).filter(Book.title.ilike('%лето%')).all():
        print(c)
    print('_' * 100)

    # Вывести книги с указанным именем автора/издателя
    for c in session.query(Book).join(Publisher).filter(Publisher.name == 'Лев Толстой').all():
        print(c)
    print('_' * 100)

    # Обновление записи издателя/автора
    session.query(Publisher).filter(Publisher.name == 'Лев Толстой').update({'name': 'Лев Николаевич Толстой'})
    session.commit()

    # Удаление записи из продаж с кол-вом 5
    session.query(Sale).filter(Sale.count == 5).delete()
    session.commit()

    # Запрос по Заданию 2. Вывести магазины, в которых продаётся введённый издатель/автор
    for x in select_shop_by_publ(input()):
        print(x)

    session.close()