from app import cache
from flask import current_app

def clear_product_caches():
    """Clear all product-related caches."""
    keys_pattern = current_app.config.get('CACHE_KEY_PREFIX', '') + 'product*'
    cache_type = current_app.config.get('CACHE_TYPE')
    
    if cache_type == 'redis':
        redis_client = cache.cache._client
        keys = redis_client.keys(keys_pattern)
        if keys:
            redis_client.delete(*keys)
            current_app.logger.info(f"Cleared {len(keys)} product cache keys")
    else:
        cache.clear()
        current_app.logger.info("Cleared entire cache (non-Redis cache)")
    
def get_cache_stats():
    """Get statistics about the cache."""
    try:
        cache_type = current_app.config.get('CACHE_TYPE')
        
        if cache_type == 'redis':
            # Basic connection test
            test_key = 'test_cache_connection'
            test_value = 'working'
            cache.set(test_key, test_value, timeout=10)
            retrieved_value = cache.get(test_key)
            
            stats = {
                'cache_type': cache_type,
                'connection_test': 'successful' if retrieved_value == test_value else 'failed'
            }
            
            # Create a direct Redis connection to get statistics
            try:
                import redis
                redis_url = current_app.config.get('CACHE_REDIS_URL')
                r = redis.from_url(redis_url)
                
                # Get basic Redis info
                info = r.info()
                
                # Add Redis info to stats
                stats.update({
                    'memory_used': info.get('used_memory_human', 'unknown'),
                    'connected_clients': info.get('connected_clients', 'unknown'),
                    'uptime_days': info.get('uptime_in_days', 'unknown'),
                    'version': info.get('redis_version', 'unknown')
                })
                
                # Try to count cache keys
                prefix = current_app.config.get('CACHE_KEY_PREFIX', '')
                all_keys = r.keys(f'{prefix}*')
                product_keys = r.keys(f'{prefix}*product*')
                
                stats.update({
                    'total_cache_keys': len(all_keys) if all_keys else 0,
                    'product_cache_keys': len(product_keys) if product_keys else 0
                })
                
            except Exception as e:
                stats['redis_info_error'] = f"Could not retrieve detailed Redis info: {str(e)}"
            
            return stats
        else:
            return {
                'cache_type': cache_type,
                'note': 'Detailed stats not available for this cache type'
            }
    except Exception as e:
        current_app.logger.error(f"Error getting cache stats: {str(e)}")
        return {
            'cache_type': current_app.config.get('CACHE_TYPE'),
            'error': f'Failed to retrieve cache statistics: {str(e)}'
        }