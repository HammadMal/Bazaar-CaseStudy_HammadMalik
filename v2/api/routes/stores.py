from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from app import db
from models.store import Store
from utils.validators import validate_store
from utils.auth import admin_required

stores_bp = Blueprint('stores', __name__)

@stores_bp.route('/', methods=['GET'])
@jwt_required()
def get_stores():
    """Get all stores with pagination and filtering."""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    search = request.args.get('search')
    region = request.args.get('region')
    active_only = request.args.get('active_only', type=bool, default=True)
    
    # Base query
    query = Store.query
    
    # Apply filters
    if search:
        query = query.filter(
            (Store.name.ilike(f'%{search}%')) | 
            (Store.code.ilike(f'%{search}%')) |
            (Store.city.ilike(f'%{search}%'))
        )
    
    if region:
        query = query.filter(Store.region == region)
    
    if active_only:
        query = query.filter(Store.active == True)
    
    # Execute with pagination
    stores = query.order_by(Store.name).paginate(page=page, per_page=per_page)
    
    # Format response
    result = {
        'items': [{
            'id': s.id,
            'code': s.code,
            'name': s.name,
            'address': s.address,
            'city': s.city,
            'region': s.region,
            'country': s.country,
            'phone': s.phone,
            'email': s.email,
            'active': s.active,
            'created_at': s.created_at.isoformat()
        } for s in stores.items],
        'pagination': {
            'page': stores.page,
            'per_page': stores.per_page,
            'total_pages': stores.pages,
            'total_items': stores.total
        }
    }
    
    return jsonify(result), 200

@stores_bp.route('/<int:store_id>', methods=['GET'])
@jwt_required()
def get_store(store_id):
    """Get a specific store by ID."""
    store = Store.query.get_or_404(store_id)
    
    result = {
        'id': store.id,
        'code': store.code,
        'name': store.name,
        'address': store.address,
        'city': store.city,
        'region': store.region,
        'country': store.country,
        'phone': store.phone,
        'email': store.email,
        'active': store.active,
        'created_at': store.created_at.isoformat(),
        'updated_at': store.updated_at.isoformat()
    }
    
    return jsonify(result), 200

@stores_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
def create_store():
    """Create a new store. Admin only."""
    data = request.get_json()
    
    # Validate request data
    validation_errors = validate_store(data)
    if validation_errors:
        return jsonify({'errors': validation_errors}), 400
    
    try:
        new_store = Store(
            code=data['code'],
            name=data['name'],
            address=data.get('address'),
            city=data.get('city'),
            region=data.get('region'),
            country=data.get('country'),
            phone=data.get('phone'),
            email=data.get('email'),
            active=data.get('active', True)
        )
        
        db.session.add(new_store)
        db.session.commit()
        
        return jsonify({
            'message': 'Store created successfully',
            'store_id': new_store.id
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Store code already exists'}), 409

@stores_bp.route('/<int:store_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_store(store_id):
    """Update an existing store. Admin only."""
    store = Store.query.get_or_404(store_id)
    data = request.get_json()
    
    # Validate request data
    validation_errors = validate_store(data, update=True)
    if validation_errors:
        return jsonify({'errors': validation_errors}), 400
    
    try:
        # Update fields if they exist in the request
        if 'code' in data:
            store.code = data['code']
        if 'name' in data:
            store.name = data['name']
        if 'address' in data:
            store.address = data['address']
        if 'city' in data:
            store.city = data['city']
        if 'region' in data:
            store.region = data['region']
        if 'country' in data:
            store.country = data['country']
        if 'phone' in data:
            store.phone = data['phone']
        if 'email' in data:
            store.email = data['email']
        if 'active' in data:
            store.active = data['active']
            
        db.session.commit()
        
        return jsonify({
            'message': 'Store updated successfully',
            'store_id': store.id
        }), 200
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Store code already exists'}), 409

@stores_bp.route('/<int:store_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_store(store_id):
    """Delete a store or mark as inactive. Admin only."""
    store = Store.query.get_or_404(store_id)
    
    # Instead of hard deletion, mark as inactive
    store.active = False
    db.session.commit()
    
    return jsonify({
        'message': 'Store deactivated successfully'
    }), 200

@stores_bp.route('/regions', methods=['GET'])
@jwt_required()
def get_regions():
    """Get all unique store regions."""
    regions = db.session.query(Store.region)\
        .filter(Store.region.isnot(None))\
        .distinct()\
        .order_by(Store.region)\
        .all()
    
    return jsonify({
        'regions': [r[0] for r in regions if r[0]]
    }), 200