from django import template
from django.forms import CheckboxInput, FileInput

register = template.Library()

@register.filter(name='form_as_tailwind')
def form_as_tailwind(form):
    return form.as_p() # Fallback, you can customize this

@register.filter(name='field_as_tailwind')
def field_as_tailwind(field):
    widget = field.field.widget
    css_classes = 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
    
    if isinstance(widget, CheckboxInput):
        # Custom rendering for checkboxes if needed
        pass
    elif isinstance(widget, FileInput):
        css_classes = 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400'

    return field.as_widget(attrs={'class': css_classes})


@register.filter(name='form_as_tailwind')
def form_as_tailwind(form):
    html = ''
    for field in form:
        html += '<div class="mb-4">'
        # Add label
        html += f'<label for="{field.id_for_label}" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">{field.label}</label>'
        
        # Add field with Tailwind classes
        css_classes = 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
        
        if isinstance(field.field.widget, CheckboxInput):
            css_classes = 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600'
            html += f'<div class="flex items-center">{field.as_widget(attrs={"class": css_classes})} <label for="{field.id_for_label}" class="ml-2 text-sm font-medium text-gray-900 dark:text-gray-300">{field.label}</label></div>'
        elif isinstance(field.field.widget, FileInput):
            css_classes = 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400'
            html += field.as_widget(attrs={'class': css_classes})
        else:
            html += field.as_widget(attrs={'class': css_classes})

        # Add help text
        if field.help_text:
            html += f'<p class="mt-2 text-sm text-gray-500 dark:text-gray-400">{field.help_text}</p>'
        
        # Add errors
        if field.errors:
            html += '<div class="mt-2 text-sm text-red-600 dark:text-red-500">'
            for error in field.errors:
                html += f'<p>{error}</p>'
            html += '</div>'
            
        html += '</div>'
        
    return html
