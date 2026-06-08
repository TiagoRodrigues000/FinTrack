from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(120), nullable=False)
    email        = db.Column(db.String(150), unique=True, nullable=False)
    password_hash= db.Column(db.String(256), nullable=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    categories   = db.relationship('Category',    backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    __tablename__ = 'categories'
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(80), nullable=False)
    icon    = db.Column(db.String(40), default='tag')
    color   = db.Column(db.String(7),  default='#27AE60')
    type    = db.Column(db.String(10), nullable=False)   # 'income' | 'expense'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    transactions = db.relationship('Transaction', backref='category', lazy=True)


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id          = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount      = db.Column(db.Float, nullable=False)
    type        = db.Column(db.String(10), nullable=False)  # 'income' | 'expense'
    date        = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    notes       = db.Column(db.Text, default='')
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'),    nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
