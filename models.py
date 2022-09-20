# Из лекции по orm alchemy:
# Теперь поговорим о другой абстракции ORM - о модели.
# Т.к. сессия session хочет работать с такой абстракцией.
# Модель это специальный класс, который наследуется от базового класса Base
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()  # Специальный абстрактный класс, от которого будут наследоваться классы модели


class Publisher(Base):
    __tablename__ = 'publisher'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    name = sq.Column(sq.String(length=40))

    def __str__(self):
        return f'{self.id}: {self.name}'


class Book(Base):
    __tablename__ = 'book'
    id = sq.Column(sq.Integer, primary_key=True)
    title = sq.Column(sq.String(length=100))
    id_publisher = sq.Column(sq.Integer, sq.ForeignKey('publisher.id'), nullable=False)

    publisher = relationship(Publisher, backref='book')  # связь с таблицей publisher

    def __str__(self):
        return f'{self.title}: {self.id_publisher}'


class Shop(Base):
    __tablename__ = 'shop'
    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=40))

    def __str__(self):
        return f'{self.id}: {self.name}'


class Stock(Base):
    __tablename__ = 'stock'
    id = sq.Column(sq.Integer, primary_key=True)
    id_book = sq.Column(sq.Integer, sq.ForeignKey('book.id'), nullable=False)
    id_shop = sq.Column(sq.Integer, sq.ForeignKey('shop.id'), nullable=False)
    count = sq.Column(sq.Integer, sq.CheckConstraint('count >= 0'))

    book = relationship(Book, backref='stock')
    shop = relationship(Shop, backref='stock')

    def __str__(self):
        return f'Stock  {self.id}: {self.id_book}, {self.id_shop}, кол-во: {self.count}'


class Sale(Base):
    __tablename__ = 'sale'
    id = sq.Column(sq.Integer, primary_key=True)
    price = sq.Column(sq.Numeric(10, 2))
    date_sale = sq.Column(sq.DateTime)  # sq.CheckConstraint("date_sale >= '2000-01-01' AND date_sale <= current_date "))
    id_stock = sq.Column(sq.Integer, sq.ForeignKey('stock.id'), nullable=False)
    count = sq.Column(sq.Integer, sq.CheckConstraint('count >= 0'))

    stock = relationship(Stock, backref='sale')


# функция создания всех таблиц
def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)