from app import db
from models.inventory import Inventory
from models.product import Product
from models.store import Store
from models.stock_movement import StockMovement

class InventoryService:
    @staticmethod
    def get_store_inventory(store_id, page=1, per_page=20, category=None, search=None, low_stock=False):
        """Get inventory for a specific store with filtering."""
        # Check if store exists
        store = Store.query.get(store_id)
        if not store:
            return None, 'Store not found'
        
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
        result = query.order_by(Product.name).paginate(page=page, per_page=per_page)
        
        return result, None

    @staticmethod
    def get_product_inventory(product_id):
        """Get inventory for a specific product across all stores."""
        # Check if product exists
        product = Product.query.get(product_id)
        if not product:
            return None, 'Product not found'
        
        # Get inventory for this product across all stores
        inventories = db.session.query(Inventory, Store)\
            .join(Store, Inventory.store_id == Store.id)\
            .filter(Inventory.product_id == product_id)\
            .all()
        
        return {
            'product': product,
            'inventories': inventories,
            'total_quantity': sum(inv.quantity for inv, _ in inventories)
        }, None

    @staticmethod
    def stock_in(store_id, product_id, quantity, user_id, reference_id=None, notes=None, 
                min_stock_level=None, max_stock_level=None):
        """Add stock to a store inventory."""
        # Validate inputs
        if quantity <= 0:
            return None, 'Quantity must be greater than zero'
        
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
                min_stock_level=min_stock_level or 0,
                max_stock_level=max_stock_level
            )
            db.session.add(inventory)
        elif min_stock_level is not None:
            inventory.min_stock_level = min_stock_level
        elif max_stock_level is not None:
            inventory.max_stock_level = max_stock_level
        
        # Update inventory
        prev_quantity = inventory.quantity
        new_quantity = prev_quantity + quantity
        inventory.quantity = new_quantity
        
        # Record movement
        movement = StockMovement(
            store_id=store_id,
            product_id=product_id,
            user_id=user_id,
            movement_type='stock-in',
            quantity=quantity,
            previous_quantity=prev_quantity,
            new_quantity=new_quantity,
            reference_id=reference_id,
            notes=notes
        )
        
        db.session.add(movement)
        db.session.commit()
        
        return {
            'inventory': inventory,
            'movement': movement
        }, None

    @staticmethod
    def stock_out(store_id, product_id, quantity, user_id, movement_type, reference_id=None, notes=None):
        """Remove stock from inventory (sale or manual removal)."""
        # Validate inputs
        if quantity <= 0:
            return None, 'Quantity must be greater than zero'
        
        if movement_type not in ['sale', 'removal', 'transfer']:
            return None, 'Invalid movement type'
        
        # Get current inventory
        inventory = Inventory.query.filter_by(
            store_id=store_id, 
            product_id=product_id
        ).first()
        
        if not inventory:
            return None, 'Inventory not found'
        
        # Check if enough stock
        if inventory.quantity < quantity:
            return None, f'Not enough stock. Available: {inventory.quantity}, Requested: {quantity}'
        
        # Update inventory
        prev_quantity = inventory.quantity
        new_quantity = prev_quantity - quantity
        inventory.quantity = new_quantity
        
        # Record movement
        movement = StockMovement(
            store_id=store_id,
            product_id=product_id,
            user_id=user_id,
            movement_type=movement_type,
            quantity=quantity,
            previous_quantity=prev_quantity,
            new_quantity=new_quantity,
            reference_id=reference_id,
            notes=notes
        )
        
        db.session.add(movement)
        db.session.commit()
        
        return {
            'inventory': inventory,
            'movement': movement
        }, None

    @staticmethod
    def get_movements(page=1, per_page=20, store_id=None, product_id=None, 
                    movement_type=None, start_date=None, end_date=None, user_id=None):
        """Get stock movements with filtering."""
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
            
        if user_id:
            query = query.filter(StockMovement.user_id == user_id)
        
        # Execute with pagination
        movements = query.order_by(StockMovement.timestamp.desc()).paginate(page=page, per_page=per_page)
        
        return movements, None