from rehab_center.seo_settings import SITE_NAME, SITE_DESCRIPTION

def theme(request):
    """Context processor that adds theme and site information to the template context."""
    # Default to 'light' theme if not set
    theme = request.COOKIES.get('theme', 'light')
    
    return {
        'current_theme': theme,
        'SITE_NAME': SITE_NAME,
        'SITE_DESCRIPTION': SITE_DESCRIPTION,
        'request': request  # Make request available in all templates
    }
