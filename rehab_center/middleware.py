"""
Custom middleware for performance optimization.
"""
import time
from django.conf import settings
from django.core.cache import cache

class RequestTimeMiddleware:
    """
    Middleware to measure request time and log slow requests.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Start timer
        start_time = time.time()
        
        # Process the request
        response = self.get_response(request)
        
        # Calculate request time
        total_time = time.time() - start_time
        
        # Log slow requests
        if total_time > 2.0:  # Log requests slower than 2 seconds
            print(f"\n[PERF] Slow request: {request.path} took {total_time:.2f} seconds")
        
        # Add timing header
        response['X-Request-Time'] = f"{total_time:.2f}s"
        return response

class DatabaseQueryCountMiddleware:
    """
    Middleware to count database queries and log if too many.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.db import connection
        
        # Reset query count
        connection.queries_log.clear()
        
        # Process the request
        response = self.get_response(request)
        
        # Get query count
        query_count = len(connection.queries)
        
        # Log if too many queries
        if query_count > 50:  # Log if more than 50 queries
            print(f"\n[PERF] Too many queries ({query_count}) on {request.path}")
        
        # Add query count header
        response['X-Query-Count'] = str(query_count)
        return response

class CacheControlMiddleware:
    """
    Middleware to add cache control headers.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Skip for API and admin
        if request.path.startswith(('/admin/', '/api/')):
            return response
        
        # Skip for authenticated users
        if hasattr(request, 'user') and request.user.is_authenticated:
            return response
        
        # Set cache headers
        max_age = getattr(settings, 'CACHE_CONTROL_MAX_AGE', 3600)
        response['Cache-Control'] = f'max-age={max_age}, public'
        
        # Add stale-while-revalidate and stale-if-error
        stale_while_revalidate = getattr(settings, 'CACHE_CONTROL_STALE_WHILE_REVALIDATE', 604800)
        stale_if_error = getattr(settings, 'CACHE_CONTROL_STALE_IF_ERROR', 86400)
        response['Cache-Control'] += f', stale-while-revalidate={stale_while_revalidate}'
        response['Cache-Control'] += f', stale-if-error={stale_if_error}'
        
        return response
