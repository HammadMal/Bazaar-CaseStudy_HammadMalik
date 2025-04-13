from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from app import db
from models.inventory import Inventory
from models.product import Product
from models.store import Store
from models.stock_movement import StockMovement
from utils.auth import admin_required

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/low-stock', methods=['GET'])
@jwt_required()
def low_stock_report():
    """Report on products with low stock levels across stores."""
    store_id = request.args.get('store_id', type=int)
    
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
    
    return jsonify({
        'count': len(result),
        'items': result
    }), 200

@reports_bp.route('/stock-movements', methods=['GET'])
@jwt_required()
def stock_movements_report():
    """Report on stock movements with filtering and date range."""
    # Get filter parameters
    store_id = request.args.get('store_id', type=int)
    product_id = request.args.get('product_id', type=int)
    movement_type = request.args.get('type')
    
    # Get date range (default to last 30 days)
    end_date = request.args.get('end_date')
    if end_date:
        end_date = datetime.fromisoformat(end_date)
    else:
        end_date = datetime.utcnow()
    
    start_date = request.args.get('start_date')
    if start_date:
        start_date = datetime.fromisoformat(start_date)
    else:
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
    
    return jsonify({
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'count': len(result),
        'movements': result
    }), 200

@reports_bp.route('/inventory-summary', methods=['GET'])
@jwt_required()
def inventory_summary():
    """Summary report of current inventory across all stores."""
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
    
    # Format results
    result = {
        'summary': {
            'total_stores': total_stores,
            'total_products': total_products,
            'total_inventory_value': float(total_inventory_value)
        },
        'top_categories': [{
            'category': cat.category,
            'total_quantity': cat.total_quantity,
            'total_value': float(cat.total_value) if cat.total_value else 0
        } for cat in top_categories],
        'top_stores': [{
            'id': store.id,
            'name': store.name,
            'total_quantity': store.total_quantity,
            'total_value': float(store.total_value) if store.total_value else 0
        } for store in top_stores]
    }
    
    return jsonify(result), 200

@reports_bp.route('/product-performance', methods=['GET'])
@jwt_required()
@admin_required
def product_performance():
    """Report on product sales performance."""
    # Get date range (default to last 30 days)
    end_date = request.args.get('end_date')
    if end_date:
        end_date = datetime.fromisoformat(end_date)
    else:
        end_date = datetime.utcnow()
    
    start_date = request.args.get('start_date')
    if start_date:
        start_date = datetime.fromisoformat(start_date)
    else:
        start_date = end_date - timedelta(days=30)
    
    # Get category filter
    category = request.args.get('category')
    
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
    ).limit(20)
    
    # Execute query
    top_selling = query.all()
    
    # Format results
    result = {
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'top_selling_products': [{
            'product_id': item.product_id,
            'sku': item.sku,
            'name': item.name,
            'category': item.category,
            'total_quantity_sold': item.total_quantity
        } for item in top_selling]
    }
    
    return jsonify(result), 200