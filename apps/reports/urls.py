"""
URL configuration for reports app
"""

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ConsultationReportView.as_view(), name='index'),
    path('validate/', views.validate_form_ajax, name='validate_ajax'),
]