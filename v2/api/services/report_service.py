from sqlalchemy import func, desc
from datetime import datetime, timedelta

from app import db
from models.inventory import Inventory
from models.product import Product
from models.store import Store
from models.stock_movement import StockMovement

class ReportService:
    @staticmethod
    def get_low_stock_report(store_id=None):
        """Generate report on products with low stock levels."""
        # Base query
        query = db.session.query(
            Inventory.store_id,
            Store.name.label('store_name'),
            Inventory.product_id,
            Product.sku,
            Product.name.label('product_name'),
            Product.category,
            Inventory.quantity,
            Inventory.min_stock_level
        ).join(
            Product, Inventory.product_id == Product.id
        ).join(
            Store, Inventory.store_id == Store.id
        ).filter(
            Inventory.quantity <= Inventory.min_stock_level,
            Inventory.min_stock_level > 0
        )
        
        # Apply store filter if provided
        if store_id:
            query = query.filter(Inventory.store_id == store_id)
        
        # Execute query
        low_stock_items = query.order_by(
            Inventory.store_id, 
            (Inventory.quantity / Inventory.min_stock_level)
        ).all()
        
        # Format results
        result = [{
            'store_id': item.store_id,
            'store_name': item.store_name,
            'product_id': item.product_id,
            'sku': item.sku,
            'product_name': item.product_name,
            'category': item.category,
            'current_quantity': item.quantity,
            'min_stock_level': item.min_stock_level,
            'stock_percentage': round((item.quantity / item.min_stock_level) * 100, 2) if item.min_stock_level else 0
        } for item in low_stock_items]
        
        return result

    @staticmethod
    def get_stock_movements_report(start_date=None, end_date=None, store_id=None, 
                                  product_id=None, movement_type=None):
        """Generate report on stock movements with date range and filters."""
        # Set default date range if not provided (last 30 days)
        if not end_date:
            end_date = datetime.utcnow()
        
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Base query for aggregated data
        query = db.session.query(
            func.date(StockMovement.timestamp).label('date'),
            StockMovement.movement_type,
            StockMovement.store_id,
            Store.name.label('store_name'),
            StockMovement.product_id,
            Product.name.label('product_name'),
            func.sum(StockMovement.quantity).label('total_quantity')
        ).join(
            Product, StockMovement.product_id == Product.id
        ).join(
            Store, StockMovement.store_id == Store.id
        ).filter(
            StockMovement.timestamp.between(start_date, end_date)
        )
        
        # Apply filters
        if store_id:
            query = query.filter(StockMovement.store_id == store_id)
        
        if product_id:
            query = query.filter(StockMovement.product_id == product_id)
        
        if movement_type:
            query = query.filter(StockMovement.movement_type == movement_type)
        
        # Group and order
        query = query.group_by(
            func.date(StockMovement.timestamp),
            StockMovement.movement_type,
            StockMovement.store_id,
            'store_name',
            StockMovement.product_id,
            'product_name'
        ).order_by(
            func.date(StockMovement.timestamp).desc()
        )
        
        # Execute query
        movements = query.all()
        
        # Format results
        result = [{
            'date': item.date.isoformat(),
            'movement_type': item.movement_type,
            'store_id': item.store_id,
            'store_name': item.store_name,
            'product_id': item.product_id,
            'product_name': item.product_name,
            'total_quantity': item.total_quantity
        } for item in movements]
        
        return result, start_date, end_date

    @staticmethod
    def get_inventory_summary():
        """Generate summary report of current inventory across all stores."""
        # Get top-level inventory summary
        total_stores = Store.query.filter_by(active=True).count()
        total_products = Product.query.filter_by(active=True).count()
        total_inventory_value = db.session.query(
            func.sum(Inventory.quantity * Product.price)
        ).join(
            Product, Inventory.product_id == Product.id
        ).scalar() or 0
        
        # Get top categories by value
        top_categories = db.session.query(
            Product.category,
            func.sum(Inventory.quantity).label('total_quantity'),
            func.sum(Inventory.quantity * Product.price).label('total_value')
        ).join(
            Product, Inventory.product_id == Product.id
        ).filter(
            Product.category.isnot(None)
        ).group_by(
            Product.category
        ).order_by(
            desc('total_value')
        ).limit(5).all()
        
        # Get top stores by inventory value
        top_stores = db.session.query(
            Store.id,
            Store.name,
            func.sum(Inventory.quantity).label('total_quantity'),
            func.sum(Inventory.quantity * Product.price).label('total_value')
        ).join(
            Inventory, Store.id == Inventory.store_id
        ).join(
            Product, Inventory.product_id == Product.id
        ).group_by(
            Store.id, Store.name
        ).order_by(
            desc('total_value')
        ).limit(5).all()
        
        return {
            'summary': {
                'total_stores': total_stores,
                'total_products': total_products,
                'total_inventory_value': float(total_inventory_value)
            },
            'top_categories': top_categories,
            'top_stores': top_stores
        }

    @staticmethod
    def get_product_performance(start_date=None, end_date=None, category=None, limit=20):
        """Generate report on product sales performance."""
        # Set default date range if not provided (last 30 days)
        if not end_date:
            end_date = datetime.utcnow()
        
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Base query for top selling products
        query = db.session.query(
            StockMovement.product_id,
            Product.sku,
            Product.name,
            Product.category,
            func.sum(StockMovement.quantity).label('total_quantity')
        ).join(
            Product, StockMovement.product_id == Product.id
        ).filter(
            StockMovement.movement_type == 'sale',
            StockMovement.timestamp.between(start_date, end_date)
        )
        
        # Apply category filter if provided
        if category:
            query = query.filter(Product.category == category)
        
        # Group and order
        query = query.group_by(
            StockMovement.product_id,
            Product.sku,
            Product.name,
            Product.category
        ).order_by(
            desc('total_quantity')
        ).limit(limit)
        
        # Execute query
        top_selling = query.all()
        
        return top_selling, start_date, end_date

    @staticmethod
    def get_store_performance(start_date=None, end_date=None, limit=10):
        """Generate report on store sales performance."""
        # Set default date range if not provided (last 30 days)
        if not end_date:
            end_date = datetime.utcnow()
        
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Base query for store sales performance
        query = db.session.query(
            StockMovement.store_id,
            Store.name,
            Store.city,
            Store.region,
            func.sum(StockMovement.quantity).label('total_quantity_sold'),
            func.sum(StockMovement.quantity * Product.price).label('total_sales_value')
        ).join(
            Store, StockMovement.store_id == Store.id
        ).join(
            Product, StockMovement.product_id == Product.id
        ).filter(
            StockMovement.movement_type == 'sale',
            StockMovement.timestamp.between(start_date, end_date)
        ).group_by(
            StockMovement.store_id,
            Store.name,
            Store.city,
            Store.region
        ).order_by(
            desc('total_sales_value')
        ).limit(limit)
        
        # Execute query
        store_performance = query.all()
        
        return store_performance, start_date, end_date