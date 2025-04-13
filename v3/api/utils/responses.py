from flask import jsonify

def success_response(data=None, message=None, status_code=200):
    """Standard success response format."""
    response = {'success': True}
    
    if message:
        response['message'] = message
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code

def error_response(message, errors=None, status_code=400):
    """Standard error response format."""
    response = {
        'success': False,
        'message': message
    }
    
    if errors:
        response['errors'] = errors
    
    return jsonify(response), status_code

def pagination_meta(paginated_query):
    """Return standard pagination metadata."""
    return {
        'page': paginated_query.page,
        'per_page': paginated_query.per_page,
        'total_pages': paginated_query.pages,
        'total_items': paginated_query.total,
        'has_next': paginated_query.has_next,
        'has_prev': paginated_query.has_prev
    }