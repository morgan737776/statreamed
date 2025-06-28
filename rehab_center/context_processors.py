from django.conf import settings
from .seo_settings import DEFAULT_META, SITE_NAME, SITE_DOMAIN, SOCIAL_MEDIA, GOOGLE_ANALYTICS_ID

def seo_context(request):
    """Adds SEO and site settings to the template context."""
    return {
        'SITE_NAME': SITE_NAME,
        'SITE_DOMAIN': SITE_DOMAIN,
        'SOCIAL_MEDIA': SOCIAL_MEDIA,
        'GOOGLE_ANALYTICS_ID': GOOGLE_ANALYTICS_ID,
        'meta': DEFAULT_META.copy(),
        'request': request,
    }
