from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from models.user import User

def admin_required(fn):
    """Decorator to check if current user has admin role."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin privileges required'}), 403
        return fn(*args, **kwargs)
    return wrapper

def store_access_required(fn):
    """
    Decorator to check if user has access to a store.
    For admin users, they have access to all stores.
    For store_manager or store_user, they only have access to their assigned store.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Invalid user'}), 401
        
        # Admin has access to all stores
        if user.role == 'admin':
            return fn(*args, **kwargs)
        
        # Get store_id from endpoint parameters or request body
        from flask import request
        
        # Try to get store_id from URL parameters
        store_id = kwargs.get('store_id')
        
        # If not in URL, try to get from request JSON body
        if not store_id and request.is_json:
            data = request.get_json()
            store_id = data.get('store_id')
        
        # If store_id isn't found or user isn't assigned to this store, deny access
        if not store_id or user.store_id != int(store_id):
            return jsonify({'error': 'You do not have access to this store'}), 403
        
        return fn(*args, **kwargs)
    return wrapper