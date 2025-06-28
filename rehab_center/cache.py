"""
Custom cache utilities for the Rehab Center project.
"""
from hashlib import md5
from urllib.parse import urlparse

def cache_key_generator(key_prefix, request):
    """
    Generate a cache key for the current request.
    """
    # Get the full path and build a cache key
    path = request.get_full_path()
    url = urlparse(path)
    cache_key = f'{key_prefix}:{request.method}:{url.path}'
    
    # Add query parameters to the cache key if they exist
    if url.query:
        cache_key = f"{cache_key}?{url.query}"
    
    # Add user-specific cache key if user is authenticated
    if hasattr(request, 'user') and request.user.is_authenticated:
        user_id = request.user.id
        cache_key = f"{cache_key}:user:{user_id}"
    else:
        # For anonymous users, use session key
        session_key = getattr(request, 'session', {}).get('_auth_user_hash', 'anonymous')
        cache_key = f"{cache_key}:session:{session_key}"
    
    # Create a hash of the cache key to ensure it's a valid cache key
    cache_key = md5(cache_key.encode('utf-8')).hexdigest()
    return f"{key_prefix}:{cache_key}"

def invalidate_template_cache(fragment_name, *args):
    """
    Invalidate a specific template fragment cache.
    """
    from django.core.cache import cache
    from django.utils.encoding import force_bytes
    from django.utils.http import urlencode
    
    if args:
        args = md5(force_bytes('|'.join([str(arg) for arg in args]))).hexdigest()
        cache_key = 'template.cache.%s.%s' % (fragment_name, args)
    else:
        cache_key = 'template.cache.%s' % fragment_name
    
    cache.delete(cache_key)

def clear_all_cache():
    """
    Clear all cache entries.
    """
    from django.core.cache import caches
    from django.conf import settings
    
    # Clear default cache
    caches['default'].clear()
    
    # Clear session cache if it's different
    if 'sessions' in settings.CACHES and 'sessions' != 'default':
        caches['sessions'].clear()
    
    # Clear template cache
    from django.core.cache import cache
    cache.clear()
