from django.shortcuts import redirect
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings

def toggle_theme(request):
    """Toggle between light and dark theme."""
    if not request.method == 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    # Get current theme from cookie or default to 'light'
    current_theme = request.COOKIES.get('theme', 'light')
    new_theme = 'dark' if current_theme == 'light' else 'light'
    
    # Create response with the new theme
    response = JsonResponse({'status': 'success', 'theme': new_theme})
    
    # Set cookie to expire in 1 year
    max_age = 365 * 24 * 60 * 60  # 1 year in seconds
    expires = timezone.now() + timezone.timedelta(seconds=max_age)
    
    # Set cookie with secure and samesite attributes
    response.set_cookie(
        'theme',
        new_theme,
        max_age=max_age,
        expires=expires.strftime("%a, %d-%b-%Y %H:%M:%S GMT"),
        secure=not settings.DEBUG,  # Only send over HTTPS in production
        httponly=False,  # Allow JavaScript to access the cookie
        samesite='Lax'  # Protection against CSRF
    )
    
    return response
