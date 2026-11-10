from sqlalchemy.orm import validates
from project import db, app
from project.validators import validate_text, validate_year, validate_book_type


# Book model
class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    author = db.Column(db.String(64))
    year_published = db.Column(db.Integer) 
    book_type = db.Column(db.String(20))
    status = db.Column(db.String(20), default='available')

    def __init__(self, name, author, year_published, book_type, status='available'):
        self.name = name
        self.author = author
        self.year_published = year_published
        self.book_type = book_type
        self.status = status

    # Validators run on every attribute assignment (create and edit)
    @validates('name', 'author')
    def validate_text_fields(self, key, value):
        return validate_text(key, value)

    @validates('year_published')
    def validate_year_published(self, key, value):
        return validate_year(key, value)

    @validates('book_type')
    def validate_book_type(self, key, value):
        return validate_book_type(key, value)

    def __repr__(self):
        return f"Book(ID: {self.id}, Name: {self.name}, Author: {self.author}, Year Published: {self.year_published}, Type: {self.book_type}, Status: {self.status})"


with app.app_context():
    db.create_all()