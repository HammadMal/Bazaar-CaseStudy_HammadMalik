from flask import request
from flask_limiter.util import get_remote_address

def get_key_func():
    """
    Custom key function for rate limiting.
    Uses API key from header if available, otherwise falls back to IP address.
    """
    api_key = request.headers.get('X-API-Key')
    if api_key:
        return f"api_key:{api_key}"
    return get_remote_address()

def get_limit_status(limiter, endpoint_name):
    """Get current rate limit status for a specific endpoint."""
    current_limit = limiter.current_limit(request.endpoint, get_key_func())
    if current_limit:
        return {
            'limit': current_limit.amount,
            'remaining': current_limit.remaining,
            'reset': current_limit.reset_at.isoformat() if current_limit.reset_at else None
        }
    return None