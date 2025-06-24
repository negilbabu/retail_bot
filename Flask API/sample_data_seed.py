# seed.py

from app import create_app
from app.extensions import db
from app.models import User, Product, Order, Complaint, StatusEnum
from datetime import datetime
import random
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

app = create_app()

with app.app_context():
    # Optional: Drop and recreate all tables (for dev/testing only)
    db.drop_all()
    db.create_all()

    # ---- Users ----
    users = [
        User(username="Negil", email="testnegsam@gmail.com", phone="12345678901"),
        User(username="bob", email="bob@example.com", phone="2222222222"),
        User(username="carol", email="carol@example.com", phone="3333333333"),
        User(username="dave", email="dave@example.com", phone="4444444444"),
        User(username="eve", email="eve@example.com", phone="5555555555"),
    ]

    # ---- Products ----
    products = [
    Product(
        product_name="iPhone 16 Pro Max",
        price=1199.99,
        stock=15,
        details=json.dumps({
            "brand": "Apple",
            "model": "16 Pro",
            "color": "Silver",
            "processor": "A18 Bionic",
            "storage": "256GB",
            "battery": "3200mAh",
            "display": "6.7-inch Super Retina XDR",
            "camera": "Pro camera system"
        })
    ),
        Product(
        product_name="iPhone 16 Pro",
        price=1199.99,
        stock=10,
        details=json.dumps({
            "brand": "Apple",
            "model": "16 Pro",
            "color": "Silver",
            "processor": "A18 Bionic",
            "storage": "256GB",
            "battery": "3200mAh",
            "display": "6.7-inch Super Retina XDR",
            "camera": "Pro camera system"
        })
    ),
        Product(
        product_name="iPhone 16",
        price=1199.99,
        stock=5,
        details=json.dumps({
            "brand": "Apple",
            "model": "16 Pro",
            "color": "Silver",
            "processor": "A18 Bionic",
            "storage": "256GB",
            "battery": "3200mAh",
            "display": "6.7-inch Super Retina XDR",
            "camera": "Pro camera system"
        })
    ),
    Product(
        product_name="Galaxy S25 ultra",
        price=1099.99,
        stock=15,
        details=json.dumps({
            "brand": "Samsung",
            "model": "S23",
            "color": "Phantom Black",
            "processor": "Snapdragon 8 Gen 2",
            "storage": "128GB",
            "battery": "3900mAh",
            "display": "6.1-inch Dynamic AMOLED 2X",
            "camera": "50MP Wide"
        })
    ),
     Product(
        product_name="Galaxy S25",
        price=1099.99,
        stock=10,
        details=json.dumps({
            "brand": "Samsung",
            "model": "S23",
            "color": "Phantom Black",
            "processor": "Snapdragon 8 Gen 2",
            "storage": "128GB",
            "battery": "3900mAh",
            "display": "6.1-inch Dynamic AMOLED 2X",
            "camera": "50MP Wide"
        })
    ),
     Product(
        product_name="Galaxy S25 plus",
        price=1099.99,
        stock=5,
        details=json.dumps({
            "brand": "Samsung",
            "model": "S23",
            "color": "Phantom Black",
            "processor": "Snapdragon 8 Gen 2",
            "storage": "128GB",
            "battery": "3900mAh",
            "display": "6.1-inch Dynamic AMOLED 2X",
            "camera": "50MP Wide"
        })
    ),
    Product(
        product_name="Pixel 9 Pro Fold",
        price=899.99,
        stock=5,
        details=json.dumps({
            "brand": "Google",
            "model": "Pixel 8",
            "color": "Obsidian",
            "processor": "Google Tensor G3",
            "storage": "128GB",
            "battery": "4575mAh",
            "display": "6.2-inch Actua display",
            "camera": "Dual camera system"
        })
    ),
     Product(
        product_name="Pixel 9 pro XL",
        price=899.99,
        stock=10,
        details=json.dumps({
            "brand": "Google",
            "model": "Pixel 8",
            "color": "Obsidian",
            "processor": "Google Tensor G3",
            "storage": "128GB",
            "battery": "4575mAh",
            "display": "6.2-inch Actua display",
            "camera": "Dual camera system"
        })
    ),
     Product(
        product_name="Pixel 9 pro",
        price=899.99,
        stock=15,
        details=json.dumps({
            "brand": "Google",
            "model": "Pixel 8",
            "color": "Obsidian",
            "processor": "Google Tensor G3",
            "storage": "128GB",
            "battery": "4575mAh",
            "display": "6.2-inch Actua display",
            "camera": "Dual camera system"
        })
    ),
     Product(
        product_name="Pixel 9",
        price=899.99,
        stock=20,
        details=json.dumps({
            "brand": "Google",
            "model": "Pixel 8",
            "color": "Obsidian",
            "processor": "Google Tensor G3",
            "storage": "128GB",
            "battery": "4575mAh",
            "display": "6.2-inch Actua display",
            "camera": "Dual camera system"
        })
    ),
    Product(
        product_name="OnePlus 11",
        price=699.99,
        stock=9,
        details=json.dumps({
            "brand": "OnePlus",
            "model": "11",
            "color": "Titan Black",
            "processor": "Snapdragon 8 Gen 2",
            "storage": "256GB",
            "battery": "5000mAh",
            "display": "6.7-inch Fluid AMOLED",
            "camera": "Hasselblad Camera for Mobile"
        })
    ),
    Product(
        product_name="Xiaomi 12T",
        price=649.99,
        stock=8,
        details=json.dumps({
            "brand": "Xiaomi",
            "model": "12T",
            "color": "Blue",
            "processor": "Dimensity 8100 Ultra",
            "storage": "128GB",
            "battery": "5000mAh",
            "display": "6.67-inch AMOLED DotDisplay",
            "camera": "108MP ProLight camera"
        })
    ),
    ]

    db.session.add_all(users + products)
    db.session.commit()

    # ---- Orders ----
    orders = []
    for i in range(5):
        order = Order(
            order_number=f"ORD{i+1001}",
            product_id=random.choice(products).id,
            user_id=random.choice(users).id,
            quantity=random.randint(1, 3),
            total = 100,
            status=random.choice([StatusEnum.ACTIVE, StatusEnum.COMPLETED]),
            created_at=datetime.utcnow()
        )
        orders.append(order)

    db.session.add_all(orders)
    db.session.commit()

    # ---- Complaints ----
    complaints = []
    for i in range(5):
        complaint = Complaint(
            message=f"Complaint message {i+1}",
            answer=None if i % 2 == 0 else f"Resolved answer {i+1}",
            status=StatusEnum.ACTIVE if i % 2 == 0 else StatusEnum.COMPLETED,
            escalated=(i % 2 == 1),
            user_id=random.choice(users).id,
            order_id=random.choice(orders).id,
            created_at=datetime.utcnow()
        )
        complaints.append(complaint)

    db.session.add_all(complaints)
    db.session.commit()

    print("✅ Seed data inserted successfully.")
