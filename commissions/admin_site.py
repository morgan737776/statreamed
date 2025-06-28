from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html
from django.template.response import TemplateResponse
from django.http import HttpRequest

class CustomAdminSite(AdminSite):
    site_header = _('Администрирование центра реабилитации')
    site_title = _('Центр реабилитации')
    index_title = _('Панель управления')
    index_template = 'admin/commissions/index.html'  # Path to our custom index template
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        return urls
        
    def each_context(self, request):
        context = super().each_context(request)
        context['site_header'] = self.site_header
        context['site_title'] = self.site_title
        context['site_url'] = '/'  # or your site URL
        return context
        
    def index(self, request: HttpRequest, extra_context=None):
        """
        Display the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        app_list = self.get_app_list(request)
        
        context = {
            **self.each_context(request),
            'title': self.index_title,
            'app_list': app_list,
            **(extra_context or {}),
        }
        
        request.current_app = self.name
        
        return TemplateResponse(
            request,
            self.index_template or 'admin/index.html',
            context,
        )
    
    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        # Get the original app list
        app_dict = self._build_app_dict(request)
        
        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])
            
            # Add custom icons for each app
            if app['app_label'] == 'commissions':
                app['icon'] = 'fa fa-users'
            elif app['app_label'] == 'core':
                app['icon'] = 'fa fa-user'
            elif app['app_label'] == 'emr':
                app['icon'] = 'fa fa-file-medical'
            elif app['app_label'] == 'rehab_programs':
                app['icon'] = 'fa fa-procedures'
            else:
                app['icon'] = 'fa fa-cog'  # Default icon

        return app_list

# Create an instance of our custom admin site
admin_site = CustomAdminSite(name='custom_admin')

# Register all models from all apps
def register_models():
    from django.apps import apps
    for model in apps.get_models():
        try:
            admin_site.register(model)
        except admin.sites.AlreadyRegistered:
            pass

# Call the registration function
register_models()
