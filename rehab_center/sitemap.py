from django.contrib import sitemaps
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site

User = get_user_model()

class StaticViewSitemap(sitemaps.Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['home', 'about', 'services', 'contact']  # Update with your URL names

    def location(self, item):
        return reverse(item)

class UserSitemap(sitemaps.Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return User.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.date_joined

# Add more sitemap classes for your models as needed

def get_sitemaps(request):
    return {
        'static': StaticViewSitemap(),
        'users': UserSitemap(),
        # Add more sitemaps here
    }
