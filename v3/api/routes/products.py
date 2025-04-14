from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from app import db, limiter, cache
from models.product import Product
from models.user import User
from utils.validators import validate_product
from utils.auth import admin_required

products_bp = Blueprint('products', __name__)

# Helper function to generate cache key
def make_cache_key():
    """Generate a cache key based on the request parameters."""
    args = request.args
    key_dict = {
        'page': args.get('page', 1),
        'per_page': args.get('per_page', 20),
        'category': args.get('category', ''),
        'search': args.get('search', '')
    }
    # Sort keys to ensure consistent cache keys
    sorted_keys = sorted(key_dict.items())
    return f"products_list:{str(sorted_keys)}"

@products_bp.route('/', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300, key_prefix=make_cache_key)  # Cache for 5 minutes
def get_products():
    """Get all products with pagination and filtering."""
    # Get query parameters for filtering and pagination
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)  # Limit max items per page
    category = request.args.get('category')
    search = request.args.get('search')
    
    # Start with base query
    query = Product.query
    
    # Apply filters if provided
    if category:
        query = query.filter(Product.category == category)
    
    if search:
        query = query.filter(
            (Product.name.ilike(f'%{search}%')) | 
            (Product.sku.ilike(f'%{search}%')) |
            (Product.description.ilike(f'%{search}%'))
        )
    
    # Get paginated results
    products = query.order_by(Product.name).paginate(page=page, per_page=per_page)
    
    # Format response
    result = {
        'items': [{
            'id': p.id,
            'sku': p.sku,
            'name': p.name,
            'description': p.description,
            'category': p.category,
            'unit': p.unit,
            'price': float(p.price) if p.price else None,
            'active': p.active,
            'created_at': p.created_at.isoformat(),
            'updated_at': p.updated_at.isoformat()
        } for p in products.items],
        'pagination': {
            'page': products.page,
            'per_page': products.per_page,
            'total_pages': products.pages,
            'total_items': products.total
        }
    }
    
    return jsonify(result), 200

@products_bp.route('/<int:product_id>', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300, key_prefix=lambda: f"product_detail:{request.view_args['product_id']}")
def get_product(product_id):
    """Get a specific product by ID."""
    product = Product.query.get_or_404(product_id)
    
    result = {
        'id': product.id,
        'sku': product.sku,
        'name': product.name,
        'description': product.description,
        'category': product.category,
        'unit': product.unit,
        'price': float(product.price) if product.price else None,
        'active': product.active,
        'created_at': product.created_at.isoformat(),
        'updated_at': product.updated_at.isoformat()
    }
    
    return jsonify(result), 200

@products_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
@limiter.limit("100 per day")
def create_product():
    """Create a new product. Admin only."""
    data = request.get_json()
    
    # Validate request data
    validation_errors = validate_product(data)
    if validation_errors:
        return jsonify({'errors': validation_errors}), 400
    
    try:
        new_product = Product(
            sku=data['sku'],
            name=data['name'],
            description=data.get('description'),
            category=data.get('category'),
            unit=data['unit'],
            price=data.get('price'),
            active=data.get('active', True)
        )
        
        db.session.add(new_product)
        db.session.commit()
        
        # Clear cache after creating a new product
        cache.delete_memoized(get_products)
        
        return jsonify({
            'message': 'Product created successfully',
            'product_id': new_product.id
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'SKU already exists'}), 409

@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_product(product_id):
    """Update an existing product. Admin only."""
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    # Validate request data
    validation_errors = validate_product(data, update=True)
    if validation_errors:
        return jsonify({'errors': validation_errors}), 400
    
    try:
        # Update fields if they exist in the request
        if 'sku' in data:
            product.sku = data['sku']
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'category' in data:
            product.category = data['category']
        if 'unit' in data:
            product.unit = data['unit']
        if 'price' in data:
            product.price = data['price']
        if 'active' in data:
            product.active = data['active']
            
        db.session.commit()
        
        # Clear specific product cache and products list cache
        cache.delete(f"product_detail:{product_id}")
        cache.delete_memoized(get_products)
        
        return jsonify({
            'message': 'Product updated successfully',
            'product_id': product.id
        }), 200
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'SKU already exists'}), 409

@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_product(product_id):
    """Delete a product or mark as inactive. Admin only."""
    product = Product.query.get_or_404(product_id)
    
    # Instead of hard deletion, mark as inactive
    product.active = False
    db.session.commit()
    
    # Clear specific product cache and products list cache
    cache.delete(f"product_detail:{product_id}")
    cache.delete_memoized(get_products)
    
    return jsonify({
        'message': 'Product deactivated successfully'
    }), 200

@products_bp.route('/categories', methods=['GET'])
@jwt_required()
@cache.cached(timeout=600)  # Cache categories for 10 minutes
def get_categories():
    """Get all unique product categories."""
    categories = db.session.query(Product.category)\
        .filter(Product.category.isnot(None))\
        .distinct()\
        .order_by(Product.category)\
        .all()
    
    return jsonify({
        'categories': [c[0] for c in categories if c[0]]
    }), 200