from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app import db
from models.product import Product
from models.inventory import Inventory

class ProductService:
    @staticmethod
    def get_products(page=1, per_page=20, category=None, search=None, active_only=True):
        """Get paginated list of products with optional filtering."""
        # Start with base query
        query = Product.query
        
        # Apply filters if provided
        if active_only:
            query = query.filter(Product.active == True)
            
        if category:
            query = query.filter(Product.category == category)
        
        if search:
            query = query.filter(
                (Product.name.ilike(f'%{search}%')) | 
                (Product.sku.ilike(f'%{search}%')) |
                (Product.description.ilike(f'%{search}%'))
            )
        
        # Get paginated results
        return query.order_by(Product.name).paginate(page=page, per_page=per_page)
    
    @staticmethod
    def get_product_by_id(product_id):
        """Get a product by ID."""
        return Product.query.get(product_id)
    
    @staticmethod
    def create_product(product_data):
        """Create a new product."""
        try:
            new_product = Product(
                sku=product_data['sku'],
                name=product_data['name'],
                description=product_data.get('description'),
                category=product_data.get('category'),
                unit=product_data['unit'],
                price=product_data.get('price'),
                active=product_data.get('active', True)
            )
            
            db.session.add(new_product)
            db.session.commit()
            
            return new_product, None
            
        except IntegrityError:
            db.session.rollback()
            return None, 'SKU already exists'
    
    @staticmethod
    def update_product(product_id, product_data):
        """Update an existing product."""
        product = Product.query.get(product_id)
        
        if not product:
            return None, 'Product not found'
        
        try:
            # Update fields if they exist in the request
            if 'sku' in product_data:
                product.sku = product_data['sku']
            if 'name' in product_data:
                product.name = product_data['name']
            if 'description' in product_data:
                product.description = product_data['description']
            if 'category' in product_data:
                product.category = product_data['category']
            if 'unit' in product_data:
                product.unit = product_data['unit']
            if 'price' in product_data:
                product.price = product_data['price']
            if 'active' in product_data:
                product.active = product_data['active']
                
            db.session.commit()
            
            return product, None
            
        except IntegrityError:
            db.session.rollback()
            return None, 'SKU already exists'
    
    @staticmethod
    def delete_product(product_id):
        """Deactivate a product (soft delete)."""
        product = Product.query.get(product_id)
        
        if not product:
            return False, 'Product not found'
        
        # Soft delete by marking as inactive
        product.active = False
        db.session.commit()
        
        return True, None
    
    @staticmethod
    def get_categories():
        """Get all unique product categories."""
        categories = db.session.query(Product.category)\
            .filter(Product.category.isnot(None))\
            .distinct()\
            .order_by(Product.category)\
            .all()
        
        return [c[0] for c in categories if c[0]]
    
    @staticmethod
    def get_low_stock_products(min_stock_percentage=100):
        """Get products with stock below minimum levels."""
        query = db.session.query(
            Inventory.product_id,
            Product.name,
            Product.sku,
            func.sum(Inventory.quantity).label('total_quantity'),
            func.min(Inventory.min_stock_level).label('min_stock_level')
        ).join(
            Product, Inventory.product_id == Product.id
        ).group_by(
            Inventory.product_id, Product.name, Product.sku
        ).having(
            func.sum(Inventory.quantity) <= func.min(Inventory.min_stock_level) * min_stock_percentage / 100
        ).order_by(
            func.sum(Inventory.quantity) / func.min(Inventory.min_stock_level)
        )
        
        return query.all()