from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from utils.auth import admin_required
from utils.cache_utils import get_cache_stats, clear_product_caches
from app import cache

cache_bp = Blueprint('cache', __name__)

@cache_bp.route('/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_stats():
    """Get cache statistics (admin only)."""
    stats = get_cache_stats()
    return jsonify(stats), 200

@cache_bp.route('/products/clear', methods=['POST'])
@jwt_required()
@admin_required
def clear_products_cache():
    """Clear all product-related caches (admin only)."""
    clear_product_caches()
    return jsonify({
        'message': 'Product caches cleared successfully'
    }), 200

@cache_bp.route('/clear', methods=['POST'])
@jwt_required()
@admin_required
def clear_all_cache():
    """Clear all caches (admin only)."""
    cache.clear()
    return jsonify({
        'message': 'All caches cleared successfully'
    }), 200