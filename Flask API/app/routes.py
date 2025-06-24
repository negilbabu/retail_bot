
import re
from flask import Blueprint, request, jsonify
from .models import Product, StatusEnum, User, Order
from app.extensions import db
from fuzzywuzzy import fuzz  
from sqlalchemy.exc import IntegrityError
import logging

api_blueprint = Blueprint("api", __name__)

# --- Utility Functions ---
STATUS_MAP = {
    StatusEnum.INACTIVE: "Inactive",
    StatusEnum.ACTIVE: "Active / In Progress", 
    StatusEnum.COMPLETED: "Completed"
}

def normalize_name(name):
    """Normalize product name by removing spaces and making it lowercase."""
    return re.sub(r"\s+", "", name).lower()

def find_exact_product(product_name):
    """Find a product by normalized name ignoring spaces and case."""
    if not product_name:
        return None
    normalized_input = normalize_name(product_name)
    products = Product.query.all()
    for product in products:
        if normalize_name(product.product_name) == normalized_input:
            return product
    return None

def find_product(product_name):
    if not product_name:
        return None
    normalized_input = normalize_name(product_name)

    # Try exact match first
    products = Product.query.all()
    for product in products:
        if normalize_name(product.product_name) == normalized_input:
            return product

    # Fall back to fuzzy match
    best_match = None
    best_score = 0
    for product in products:
        score = fuzz.ratio(normalized_input, normalize_name(product.product_name))
        if score > best_score:
            best_score = score
            best_match = product
    
    return best_match if best_score > 85 else None

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def check_user_exists(email):
    user = User.query.filter(User.email.ilike(f'%{email}%')).first()
    if not user:
        user = User(email=email)
        db.session.add(user)
    db.session.commit()
    return user.id

@api_blueprint.route('/api/product_stock', methods=['GET'])
def product_stock():
    product_name = request.args.get("product_name")
    if not product_name:
        return {"error": "Missing product_name"}, 400

    product = find_exact_product(product_name)
    if not product:
        return {"error": "Product not found"}, 404

    return {"stock": product.stock}

@api_blueprint.route('/api/product_price', methods=['GET'])
def product_price():
    product_name = request.args.get("product_name")
    if not product_name:
        return {"error": "Missing product_name"}, 400

    product = find_exact_product(product_name)
    if not product:
        return {"error": "Product not found"}, 404

    return {"price": product.price}

@api_blueprint.route('/api/product_details', methods=['GET'])
def product_details():
    product_name = request.args.get("product_name")
    if not product_name:
        return {"error": "Missing product_name"}, 400

    product = find_exact_product(product_name)
    if not product:
        return {"error": "Product not found"}, 404

    return {"details": product.details}

@api_blueprint.route('/api/place_order', methods=['POST'])
def place_order():
    try:
        order_data = request.get_json()
        if not order_data:
            return {"error": "Request body must contain JSON data"}, 400
    except Exception:
        return {"error": "Failed to decode JSON from request body"}, 400

    required_fields = {'order_number', 'product_name', 'user_email', 'product_quantity'}
    missing_fields = required_fields.difference(order_data.keys())
    if missing_fields:
        return {"error": f"Missing required fields: {', '.join(sorted(list(missing_fields)))}"}, 400

    try:
        product_name = order_data['product_name']
        user_email = order_data['user_email']
        quantity = int(order_data['product_quantity'])
        order_number = order_data['order_number'] 
        product = find_exact_product(product_name)
        if not product:
            return {"error": f"Product '{product_name}' not found"}, 404
        user_id = check_user_exists(user_email)
        if not user_id:
             return {"error": f"Could not find or create user for email: {user_email}"}, 400
        grand_total = float(product.price) * quantity
        new_order = Order(
            order_number=order_number,
            product_id=product.id,
            user_id=user_id,
            quantity=quantity,
            total=grand_total
        )
        db.session.add(new_order)
        db.session.commit()
        logging.info(f"Successfully placed order {order_number}")
        return {"status": "success", "message": "Order placed successfully"}, 201

    except IntegrityError as e:
        db.session.rollback()
        logging.error(f"Database integrity error: {e}")
        return {"error": "Database error: An order with this number might already exist."}, 409
    except Exception as e:
        db.session.rollback()
        logging.error(f"An unexpected error occurred while placing order: {e}")
        return {"error": "An unexpected server error occurred"}, 500

@api_blueprint.route('/api/order_history', methods=['GET'])
def order_history():
    user_email = request.args.get("user_email")
    if not user_email:
        return {"error": "Missing email"}, 400
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return {"error": "User not found"}, 404
    orders = Order.query.filter_by(user_id=user.id).all()
    if not orders:
        return {"error": "No order history found"}, 404
    order_history = []
    for order in orders:
        status_display = STATUS_MAP.get(order.status, "Unknown Status")
        order_history.append({
            "order_number": order.order_number,
            "product_name": order.product.product_name, 
            "product_quantity":order.quantity,
            "total_price": order.total,
            "order_status":status_display,
            "date": order.created_at.strftime('%Y-%m-%d') 
        })
    return {"order_history": order_history}, 200

@api_blueprint.route('/api/cancel_order', methods=['POST'])
def cancel_order():
    """
    Validates and cancels an order, combining business logic with robust error handling.
    """
    try:
        data = request.get_json()
        if not data:
            return {"error": "Request body must contain valid JSON"}, 400
        user_email = data.get("user_email")
        order_number = data.get("order_number")
        if not user_email or not order_number:
            return {"error": "Missing 'user_email' or 'order_number'"}, 400
        logging.info(f"[CANCEL_ORDER] Attempting to cancel order '{order_number}' for user '{user_email}'.")
        user = User.query.filter_by(email=user_email.strip()).first()
        if not user:
            logging.warning(f"[CANCEL_ORDER] User not found for email: {user_email}")
            return {"error": "User with this email not found"}, 404
        order = Order.query.filter_by(order_number=order_number.strip().upper(), user_id=user.id).first()
        if not order:
            logging.warning(f"[CANCEL_ORDER] Order '{order_number}' not found for user ID {user.id}.")
            return {"error": "Order not found for this user account"}, 404
        if order.status == StatusEnum.COMPLETED:
            logging.warning(f"[CANCEL_ORDER] Attempted to cancel a COMPLETED order: {order.order_number}")
            return {"error": "This order has already been completed and cannot be cancelled."}, 409 
        elif order.status == StatusEnum.ACTIVE:
            order.status = StatusEnum.INACTIVE
            db.session.commit()
            logging.info(f"[CANCEL_ORDER] Successfully cancelled order: {order.order_number}")
            return {"message": f"Order {order.order_number} has been successfully cancelled."}, 200
        elif order.status == StatusEnum.INACTIVE:
            logging.info(f"[CANCEL_ORDER] Attempted to cancel an already INACTIVE order: {order.order_number}")
            return {"message": f"This order ({order.order_number}) has already been cancelled."}, 200 
        else:
            # Catch any other unforeseen statuses
            return {"error": f"Order is in an un-cancellable state: {order.status.name}"}, 409
    except Exception as e:
        db.session.rollback()
        logging.error(f"[CANCEL_ORDER] An unexpected error occurred: {e}")
        return {"error": "A server error occurred while trying to cancel the order."}, 500
    

@api_blueprint.route('/api/products', methods=['GET'])
def get_all_products():
    """
    Retrieves a list of all products from the database.
    """
    try:
        products_from_db = Product.query.all()
        if not products_from_db:
            # It's okay if there are no products, just return an empty list
            return jsonify({"products": []}), 200
        # Create a list of product dictionaries to return as JSON
        products_list = [
            {"product_name": p.product_name, "price": str(p.price)}
            for p in products_from_db
        ]
        logging.info(f"Returning {len(products_list)} products.")
        return jsonify({"products": products_list}), 200
    except Exception as e:
        logging.error(f"[GET_ALL_PRODUCTS] An unexpected error occurred: {e}")
        return {"error": "A server error occurred while fetching products."}, 500