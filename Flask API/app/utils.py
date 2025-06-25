from .models import Product, StatusEnum, User, Order
import re
from fuzzywuzzy import fuzz  
from app.extensions import db



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

