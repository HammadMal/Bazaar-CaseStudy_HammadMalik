def validate_login(data):
    """Validate login request data."""
    errors = {}
    
    if not data:
        return {'message': 'No data provided'}
    
    if 'username' not in data or not data['username']:
        errors['username'] = 'Username is required'
    
    if 'password' not in data or not data['password']:
        errors['password'] = 'Password is required'
    
    return errors

def validate_registration(data):
    """Validate user registration data."""
    errors = {}
    
    if not data:
        return {'message': 'No data provided'}
    
    if 'username' not in data or not data['username']:
        errors['username'] = 'Username is required'
    elif len(data['username']) < 3:
        errors['username'] = 'Username must be at least 3 characters'
    
    if 'email' not in data or not data['email']:
        errors['email'] = 'Email is required'
    elif '@' not in data['email']:
        errors['email'] = 'Invalid email format'
    
    if 'password' not in data or not data['password']:
        errors['password'] = 'Password is required'
    elif len(data['password']) < 6:
        errors['password'] = 'Password must be at least 6 characters'
    
    if 'role' in data and data['role'] not in ['admin', 'store_manager', 'store_user']:
        errors['role'] = 'Invalid role'
    
    return errors

def validate_product(data, update=False):
    """Validate product data."""
    errors = {}
    
    if not data:
        return {'message': 'No data provided'}
    
    if not update:
        # These fields are required for new products
        if 'sku' not in data or not data['sku']:
            errors['sku'] = 'SKU is required'
        
        if 'name' not in data or not data['name']:
            errors['name'] = 'Product name is required'
        
        if 'unit' not in data or not data['unit']:
            errors['unit'] = 'Unit is required'
    else:
        # For updates, if these fields are provided, they can't be empty
        if 'sku' in data and not data['sku']:
            errors['sku'] = 'SKU cannot be empty'
        
        if 'name' in data and not data['name']:
            errors['name'] = 'Product name cannot be empty'
        
        if 'unit' in data and not data['unit']:
            errors['unit'] = 'Unit cannot be empty'
    
    # Price validation if provided
    if 'price' in data and data['price'] is not None:
        try:
            price = float(data['price'])
            if price < 0:
                errors['price'] = 'Price cannot be negative'
        except (ValueError, TypeError):
            errors['price'] = 'Price must be a valid number'
    
    return errors

def validate_store(data, update=False):
    """Validate store data."""
    errors = {}
    
    if not data:
        return {'message': 'No data provided'}
    
    if not update:
        # These fields are required for new stores
        if 'code' not in data or not data['code']:
            errors['code'] = 'Store code is required'
        
        if 'name' not in data or not data['name']:
            errors['name'] = 'Store name is required'
    else:
        # For updates, if these fields are provided, they can't be empty
        if 'code' in data and not data['code']:
            errors['code'] = 'Store code cannot be empty'
        
        if 'name' in data and not data['name']:
            errors['name'] = 'Store name cannot be empty'
    
    # Email validation if provided
    if 'email' in data and data['email']:
        if '@' not in data['email']:
            errors['email'] = 'Invalid email format'
    
    return errors

def validate_stock_movement(data, movement_type):
    """Validate stock movement data."""
    errors = {}
    
    if not data:
        return {'message': 'No data provided'}
    
    # These fields are required for all movement types
    if 'store_id' not in data or not data['store_id']:
        errors['store_id'] = 'Store ID is required'
    
    if 'product_id' not in data or not data['product_id']:
        errors['product_id'] = 'Product ID is required'
    
    if 'quantity' not in data or not data['quantity']:
        errors['quantity'] = 'Quantity is required'
    else:
        try:
            quantity = int(data['quantity'])
            if quantity <= 0:
                errors['quantity'] = 'Quantity must be greater than zero'
        except (ValueError, TypeError):
            errors['quantity'] = 'Quantity must be a valid number'
    
    # Specific validations per movement type
    if movement_type == 'stock-in':
        pass  # No additional validations for stock-in
    
    elif movement_type == 'sale':
        if 'reference_id' not in data or not data['reference_id']:
            errors['reference_id'] = 'Reference ID (invoice/receipt) is required for sales'
    
    elif movement_type == 'removal':
        if 'notes' not in data or not data['notes']:
            errors['notes'] = 'Notes are required when removing stock'
    
    return errors