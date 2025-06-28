from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def meta_tags(context, meta=None):
    """Render meta tags."""
    if meta is None:
        meta = context.get('meta', {})
    
    request = context.get('request')
    site_name = context.get('SITE_NAME', '')
    site_domain = context.get('SITE_DOMAIN', '')
    
    # Merge with default meta
    default_meta = {
        'title': site_name,
        'description': '',
        'keywords': '',
        'og_type': 'website',
        'og_image': f'https://{site_domain}/static/images/og-default.jpg',
        'og_url': request.build_absolute_uri(request.path) if request else f'https://{site_domain}/',
        'twitter_card': 'summary_large_image',
    }
    
    default_meta.update(meta)
    
    # Ensure absolute URL for og:image
    if default_meta['og_image'] and not default_meta['og_image'].startswith(('http://', 'https://')):
        default_meta['og_image'] = f'https://{site_domain}{default_meta["og_image"]}'
    
    return mark_safe(render_to_string('seo/meta_tags.html', {
        'meta': default_meta,
        'site_name': site_name,
        'site_domain': site_domain,
    }))
