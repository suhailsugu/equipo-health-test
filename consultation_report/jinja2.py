"""
Jinja2 configuration for Django
"""

from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from jinja2 import Environment


def environment(**options):
    """
    Create Jinja2 environment with Django integration
    """
    env = Environment(**options)
    
    # Add Django functions to Jinja2 globals
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
    })
    
    # Add custom filters
    env.filters.update({
        'field_type': get_field_type,
        'add_class': add_css_class,
        'format_errors': format_form_errors,
    })
    
    return env


def get_field_type(field):
    """Get the widget type of a form field"""
    widget_name = field.field.widget.__class__.__name__
    return widget_name.lower()


def add_css_class(field, css_class):
    """Add CSS class to form field widget"""
    existing_classes = field.field.widget.attrs.get('class', '')
    field.field.widget.attrs['class'] = f'{existing_classes} {css_class}'.strip()
    return field


def format_form_errors(errors):
    """Format form errors for display"""
    if not errors:
        return []
    
    formatted_errors = []
    for field, error_list in errors.items():
        for error in error_list:
            formatted_errors.append({
                'field': field,
                'message': str(error)
            })
    
    return formatted_errors