from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity
)

from app import db, limiter
from models.user import User
from utils.validators import validate_login, validate_registration

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """User login endpoint."""
    data = request.get_json()
    
    # Validate request data
    validation_errors = validate_login(data)
    if validation_errors:
        return jsonify({'errors': validation_errors}), 400
    
    # Find the user
    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is disabled'}), 403
    
    # Update last login timestamp
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Create tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'store_id': user.store_id
        }
    }), 200

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per hour")
def register():
    """User registration endpoint. Admin only in production."""
    data = request.get_json()
    
    # Validate request data
    validation_errors = validate_registration(data)
    if validation_errors:
        return jsonify({'errors': validation_errors}), 400
    
    # Check for existing user
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
    
    # Create new user
    new_user = User(
        username=data['username'],
        email=data['email'],
        role=data.get('role', 'store_user'),
        store_id=data.get('store_id')
    )
    new_user.set_password(data['password'])
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'message': 'User registered successfully',
        'user_id': new_user.id
    }), 201

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({'error': 'Invalid or inactive user'}), 401
    
    access_token = create_access_token(identity=current_user_id)
    return jsonify({'access_token': access_token}), 200