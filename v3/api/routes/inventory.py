from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from app import db, limiter
from models.inventory import Inventory
from models.product import Product
from models.store import Store
from models.stock_movement import StockMovement
from models.user import User
from utils.validators import validate_stock_movement
from utils.auth import store_access_required
from messaging import message_queue, with_message_queue

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/store/<int:store_id>', methods=['GET'])
@jwt_required()
@store_access_required
def get_store_inventory(store_id):
    """Get inventory for a specific store with filtering and pagination."""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    category = request.args.get('category')
    search = request.args.get('search')
    low_stock = request.args.get('low_stock', type=bool)
    
    # Check if store exists
    store = Store.query.get_or_404(store_id)
    
    # Base query - join inventory with products
    query = db.session.query(Inventory, Product)\
        .join(Product, Inventory.product_id == Product.id)\
        .filter(Inventory.store_id == store_id)
    
    # Apply filters
    if category:
        query = query.filter(Product.category == category)
    
    if search:
        query = query.filter(
            (Product.name.ilike(f'%{search}%')) | 
            (Product.sku.ilike(f'%{search}%'))
        )
    
    if low_stock:
        query = query.filter(Inventory.quantity <= Inventory.min_stock_level)
    
    # Execute with pagination
    inventory_data = query.order_by(Product.name).paginate(page=page, per_page=per_page)
    
    # Format response
    result = {
        'store': {
            'id': store.id,
            'code': store.code,
            'name': store.name
        },
        'items': [{
            'inventory_id': inv.id,
            'product': {
                'id': prod.id,
                'sku': prod.sku,
                'name': prod.name,
                'category': prod.category,
                'unit': prod.unit
            },
            'quantity': inv.quantity,
            'min_stock_level': inv.min_stock_level,
            'max_stock_level': inv.max_stock_level,
            'last_updated': inv.last_updated.isoformat()
        } for inv, prod in inventory_data.items],
        'pagination': {
            'page': inventory_data.page,
            'per_page': inventory_data.per_page,
            'total_pages': inventory_data.pages,
            'total_items': inventory_data.total
        }
    }
    
    return jsonify(result), 200

@inventory_bp.route('/product/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product_inventory(product_id):
    """Get inventory for a specific product across all stores."""
    # Check if product exists
    product = Product.query.get_or_404(product_id)
    
    # Get inventory for this product across all stores
    inventories = db.session.query(Inventory, Store)\
        .join(Store, Inventory.store_id == Store.id)\
        .filter(Inventory.product_id == product_id)\
        .all()
    
    result = {
        'product': {
            'id': product.id,
            'sku': product.sku,
            'name': product.name,
            'category': product.category,
            'unit': product.unit
        },
        'store_inventory': [{
            'store': {
                'id': store.id,
                'code': store.code,
                'name': store.name
            },
            'quantity': inv.quantity,
            'last_updated': inv.last_updated.isoformat()
        } for inv, store in inventories],
        'total_quantity': sum(inv.quantity for inv, _ in inventories)
    }
    
    return jsonify(result), 200

@inventory_bp.route('/stock-in', methods=['POST'])
@jwt_required()
@store_access_required
@limiter.limit("200 per day")
def stock_in():
    """Record stock-in (add inventory) to a store."""
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    # Validate request data
    validation_errors = validate_stock_movement(data, 'stock-in')
    if validation_errors:
        return jsonify({'errors': validation_errors}), 400
    
    store_id = data['store_id']
    product_id = data['product_id']
    quantity = data['quantity']
    
    # Get current inventory
    inventory = Inventory.query.filter_by(
        store_id=store_id, 
        product_id=product_id
    ).first()
    
    # If inventory doesn't exist, create it
    if not inventory:
        inventory = Inventory(
            store_id=store_id,
            product_id=product_id,
            quantity=0,
            min_stock_level=data.get('min_stock_level', 0),
            max_stock_level=data.get('max_stock_level')
        )
        db.session.add(inventory)
    
    # Update inventory
    prev_quantity = inventory.quantity
    new_quantity = prev_quantity + quantity
    inventory.quantity = new_quantity
    
    # Record movement
    movement = StockMovement(
        store_id=store_id,
        product_id=product_id,
        user_id=current_user_id,
        movement_type='stock-in',
        quantity=quantity,
        previous_quantity=prev_quantity,
        new_quantity=new_quantity,
        reference_id=data.get('reference_id'),
        notes=data.get('notes')
    )
    
    db.session.add(movement)
    db.session.commit()
    
    return jsonify({
        'message': 'Stock added successfully',
        'inventory': {
            'store_id': store_id,
            'product_id': product_id,
            'previous_quantity': prev_quantity,
            'new_quantity': new_quantity
        },
        'movement_id': movement.id
    }), 200

@inventory_bp.route('/sale', methods=['POST'])
@jwt_required()
@store_access_required
@limiter.limit("300 per day")
def record_sale():
    """Record a sale (reduce inventory) from a store."""
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    # Validate request data
    validation_errors = validate_stock_movement(data, 'sale')
    if validation_errors:
        return jsonify({'errors': validation_errors}), 400
    
    store_id = data['store_id']
    product_id = data['product_id']
    quantity = data['quantity']
    
    # Get current inventory
    inventory = Inventory.query.filter_by(
        store_id=store_id, 
        product_id=product_id
    ).first_or_404()
    
    # Check if enough stock
    if inventory.quantity < quantity:
        return jsonify({
            'error': 'Not enough stock',
            'available': inventory.quantity,
            'requested': quantity
        }), 400
    
    # Update inventory
    prev_quantity = inventory.quantity
    new_quantity = prev_quantity - quantity
    inventory.quantity = new_quantity
    
    # Record movement
    movement = StockMovement(
        store_id=store_id,
        product_id=product_id,
        user_id=current_user_id,
        movement_type='sale',
        quantity=quantity,
        previous_quantity=prev_quantity,
        new_quantity=new_quantity,
        reference_id=data.get('reference_id'),
        notes=data.get('notes')
    )
    
    db.session.add(movement)
    db.session.commit()
    
    return jsonify({
        'message': 'Sale recorded successfully',
        'inventory': {
            'store_id': store_id,
            'product_id': product_id,
            'previous_quantity': prev_quantity,
            'new_quantity': new_quantity
        },
        'movement_id': movement.id
    }), 200

@inventory_bp.route('/remove', methods=['POST'])
@jwt_required()
@store_access_required
def remove_stock():
    """Remove stock (e.g., damaged/expired) from a store."""
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    # Validate request data
    validation_errors = validate_stock_movement(data, 'removal')
    if validation_errors:
        return jsonify({'errors': validation_errors}), 400
    
    store_id = data['store_id']
    product_id = data['product_id']
    quantity = data['quantity']
    
    # Get current inventory
    inventory = Inventory.query.filter_by(
        store_id=store_id, 
        product_id=product_id
    ).first_or_404()
    
    # Check if enough stock
    if inventory.quantity < quantity:
        return jsonify({
            'error': 'Not enough stock',
            'available': inventory.quantity,
            'requested': quantity
        }), 400
    
    # Update inventory
    prev_quantity = inventory.quantity
    new_quantity = prev_quantity - quantity
    inventory.quantity = new_quantity
    
    # Record movement
    movement = StockMovement(
        store_id=store_id,
        product_id=product_id,
        user_id=current_user_id,
        movement_type='removal',
        quantity=quantity,
        previous_quantity=prev_quantity,
        new_quantity=new_quantity,
        reference_id=None,
        notes=data.get('notes')
    )
    
    db.session.add(movement)
    db.session.commit()
    
    return jsonify({
        'message': 'Stock removed successfully',
        'inventory': {
            'store_id': store_id,
            'product_id': product_id,
            'previous_quantity': prev_quantity,
            'new_quantity': new_quantity
        },
        'movement_id': movement.id
    }), 200

@inventory_bp.route('/movements', methods=['GET'])
@jwt_required()
def get_movements():
    """Get stock movements with filtering by store, product, type, etc."""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    store_id = request.args.get('store_id', type=int)
    product_id = request.args.get('product_id', type=int)
    movement_type = request.args.get('type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Base query
    query = StockMovement.query
    
    # Apply filters
    if store_id:
        query = query.filter(StockMovement.store_id == store_id)
    
    if product_id:
        query = query.filter(StockMovement.product_id == product_id)
    
    if movement_type:
        query = query.filter(StockMovement.movement_type == movement_type)
    
    if start_date:
        query = query.filter(StockMovement.timestamp >= start_date)
    
    if end_date:
        query = query.filter(StockMovement.timestamp <= end_date)
    
    # Execute with pagination
    movements = query.order_by(StockMovement.timestamp.desc()).paginate(page=page, per_page=per_page)
    
    # Format response
    result = {
        'items': [{
            'id': m.id,
            'store_id': m.store_id,
            'product_id': m.product_id,
            'movement_type': m.movement_type,
            'quantity': m.quantity,
            'previous_quantity': m.previous_quantity,
            'new_quantity': m.new_quantity,
            'reference_id': m.reference_id,
            'notes': m.notes,
            'timestamp': m.timestamp.isoformat(),
            'user_id': m.user_id
        } for m in movements.items],
        'pagination': {
            'page': movements.page,
            'per_page': movements.per_page,
            'total_pages': movements.pages,
            'total_items': movements.total
        }
    }
    
    return jsonify(result), 200