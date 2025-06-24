from datetime import datetime
from enum import Enum
from .extensions import db
from sqlalchemy import Enum as PgEnum
from sqlalchemy import Numeric

class StatusEnum(Enum):
    INACTIVE = 0
    ACTIVE = 1
    COMPLETED = 2 

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    status = db.Column(PgEnum(StatusEnum), default=StatusEnum.ACTIVE, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    orders = db.relationship('Order', backref='user', lazy=True)
    complaints = db.relationship('Complaint', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username or self.email or self.phone}>"

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    stock = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(PgEnum(StatusEnum), default=StatusEnum.ACTIVE, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    orders = db.relationship('Order', backref='product', lazy=True)

    def __repr__(self):
        return f"<Product {self.product_name} - {self.model_name}>"

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    total = db.Column(Numeric(10, 2), nullable=False, default=0.00) 
    status = db.Column(PgEnum(StatusEnum), default=StatusEnum.ACTIVE, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    complaints = db.relationship('Complaint', backref='order', lazy=True)

    def __repr__(self):
        return f"<Order {self.order_number}>"

class Complaint(db.Model):
    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=True)
    status = db.Column(PgEnum(StatusEnum), default=StatusEnum.ACTIVE, nullable=False)
    escalated = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)

    def __repr__(self):
        return f"<Complaint {self.id} - {self.status}>"
