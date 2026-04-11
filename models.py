from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone
import secrets

from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def utcnow():
    """Timezone-aware UTC now helper."""
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=utcnow)
    is_active = db.Column(db.Boolean, default=True)

    borrowed_books = db.relationship(
        'BookBorrowing', backref='borrower', lazy=True,
        foreign_keys='BookBorrowing.user_id'
    )

    def set_password(self, password):
        """Hash password using bcrypt via werkzeug."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self):
        return secrets.token_urlsafe(32)

    def is_admin(self):
        return self.role == 'admin'

    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'department': self.department or '',
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else '',
            'is_active': 'Yes' if self.is_active else 'No'
        }

    def get_borrowed_books(self):
        return BookBorrowing.query.filter_by(
            user_id=self.id, status='borrowed'
        ).order_by(BookBorrowing.due_date).all()


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    book_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    isbn = db.Column(db.String(20))
    subject = db.Column(db.String(50), nullable=False, index=True)
    grade_level = db.Column(db.String(20), index=True)
    publisher = db.Column(db.String(100))
    publication_year = db.Column(db.Integer)
    edition = db.Column(db.String(20))
    copies_available = db.Column(db.Integer, default=1)
    total_copies = db.Column(db.Integer, default=1)
    shelf_location = db.Column(db.String(50))
    date_added = db.Column(db.DateTime, default=utcnow)
    is_available = db.Column(db.Boolean, default=True, index=True)

    borrowing_records = db.relationship(
        'BookBorrowing', backref='book', lazy=True,
        foreign_keys='BookBorrowing.book_id'
    )

    def generate_book_number(self):
        prefix = self.subject[:3].upper() if self.subject else 'GEN'
        year = datetime.now().year
        last_book = Book.query.filter(
            Book.subject == self.subject
        ).order_by(Book.id.desc()).first()

        if last_book and last_book.book_number:
            try:
                last_num = int(last_book.book_number.split('/')[-1])
                return f"{prefix}/{year}/{str(last_num + 1).zfill(3)}"
            except (ValueError, IndexError):
                pass
        return f"{prefix}/{year}/001"

    def to_dict(self):
        return {
            'book_number': self.book_number,
            'title': self.title,
            'author': self.author,
            'subject': self.subject,
            'grade_level': self.grade_level,
            'isbn': self.isbn or '',
            'publisher': self.publisher or '',
            'publication_year': self.publication_year or '',
            'edition': self.edition or '',
            'total_copies': self.total_copies,
            'copies_available': self.copies_available,
            'shelf_location': self.shelf_location or '',
            'date_added': self.date_added.strftime('%Y-%m-%d') if self.date_added else '',
            'is_available': 'Yes' if self.is_available else 'No'
        }

    @staticmethod
    def _parse_int(value, default=1):
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _parse_year(value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def from_dict(data):
        book = Book(
            title=data.get('title', ''),
            author=data.get('author', ''),
            subject=data.get('subject', 'General'),
            grade_level=data.get('grade_level', ''),
            isbn=data.get('isbn', ''),
            publisher=data.get('publisher', ''),
            edition=data.get('edition', ''),
            shelf_location=data.get('shelf_location', ''),
        )
        book.total_copies = Book._parse_int(data.get('total_copies', 1))
        book.copies_available = Book._parse_int(
            data.get('copies_available', book.total_copies), book.total_copies
        )
        book.publication_year = Book._parse_year(data.get('publication_year'))
        book.book_number = book.generate_book_number()
        return book

    @staticmethod
    def create_bulk_books(prefix, year, start_num, end_num, base_book_data):
        books = []
        total_copies = Book._parse_int(base_book_data.get('total_copies', 1))
        for num in range(start_num, end_num + 1):
            book = Book(
                title=base_book_data.get('title', ''),
                author=base_book_data.get('author', ''),
                subject=base_book_data.get('subject', 'General'),
                grade_level=base_book_data.get('grade_level', ''),
                isbn=base_book_data.get('isbn', ''),
                publisher=base_book_data.get('publisher', ''),
                publication_year=Book._parse_year(base_book_data.get('publication_year')),
                edition=base_book_data.get('edition', ''),
                total_copies=total_copies,
                copies_available=total_copies,
                shelf_location=base_book_data.get('shelf_location', ''),
            )
            book.book_number = f"{prefix}/{year}/{str(num).zfill(3)}"
            books.append(book)
        return books


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    section = db.Column(db.String(10))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(15))
    parent_name = db.Column(db.String(100))
    parent_phone = db.Column(db.String(15))
    date_enrolled = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())
    is_active = db.Column(db.Boolean, default=True)


class BookBorrowing(db.Model):
    __tablename__ = 'book_borrowing'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    borrowed_date = db.Column(db.DateTime, default=utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    returned_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='borrowed', index=True)
    fine_amount = db.Column(db.Float, default=0.0)
    fine_paid = db.Column(db.Boolean, default=False)

    FINE_RATE_PER_DAY = 0.50  # $0.50 per day — consistent with PDF receipts

    def calculate_fine(self):
        """Calculate and update fine for overdue books."""
        now = datetime.now(timezone.utc)
        due = self.due_date
        if due.tzinfo is None:
            due = due.replace(tzinfo=timezone.utc)
        if self.status == 'borrowed' and now > due:
            days_overdue = (now - due).days
            self.fine_amount = days_overdue * self.FINE_RATE_PER_DAY
            self.status = 'overdue'
            return self.fine_amount
        return 0

    def to_dict(self):
        return {
            'book_number': self.book.book_number if self.book else '',
            'book_title': self.book.title if self.book else '',
            'borrower_name': self.borrower.full_name if self.borrower else '',
            'borrower_username': self.borrower.username if self.borrower else '',
            'borrowed_date': self.borrowed_date.strftime('%Y-%m-%d') if self.borrowed_date else '',
            'due_date': self.due_date.strftime('%Y-%m-%d') if self.due_date else '',
            'returned_date': self.returned_date.strftime('%Y-%m-%d') if self.returned_date else '',
            'status': self.status,
            'fine_amount': self.fine_amount,
            'fine_paid': 'Yes' if self.fine_paid else 'No'
        }


class Log(db.Model):
    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=utcnow)
