"""
SEO and Analytics Configuration
"""

# Basic SEO settings
SITE_NAME = "StatReaMed - Центр Реабилитации"
SITE_DOMAIN = "ваш-сайт.ру"
SITE_DESCRIPTION = "Профессиональная медицинская реабилитация"

# Google Analytics
GOOGLE_ANALYTICS_ID = "G-ВАШ_ID"  # Замените на ваш ID

# Social Media
SOCIAL_MEDIA = {
    'facebook': 'https://facebook.com/ваша-страница',
    'instagram': 'https://instagram.com/ваш-аккаунт',
    'telegram': 'https://t.me/ваш-канал',
}

# Default meta tags
DEFAULT_META = {
    'title': SITE_NAME.replace('StatReaMed - ', ''),
    'description': SITE_DESCRIPTION,
    'keywords': 'реабилитация, медицина, здоровье, восстановление',
    'og_type': 'website',
    'og_image': '/static/images/og-default.jpg',
    'og_url': f'https://{SITE_DOMAIN}',
    'twitter_card': 'summary_large_image',
}
