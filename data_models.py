from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Date, ForeignKey, Integer, String, update

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'author'

    author_id = Column(Integer, primary_key=True, autoincrement=True)
    author_name = Column(String)
    author_birth_date = Column(Date)
    author_date_of_death = Column(Date)

    def __repr__(self):
        return f"Author(author_id = {self.author_id}, name = {self.author_name})"


class Book(db.Model):
    __tablename__ = 'book'

    book_id = Column(Integer, primary_key=True, autoincrement=True)
    book_isbn = Column(Integer)
    book_title = Column(String)
    book_publication_year = Column(Date)
    author_id = Column(Integer, ForeignKey('author.author_id'))

    def __repr__(self):
        return f"Book(book_id = {self.book_id}, title = {self.book_title}, author_id={self.author_id})"

