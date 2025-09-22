from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json

from .forms import ConsultationReportForm
from .models import ConsultationReport
from .utils import generate_pdf_report

class ConsultationReportView(View):
    """Main view for consultation report form"""
    
    def get(self, request):
        """Display the consultation report form"""
        form = ConsultationReportForm()
        return render(request, 'reports/index.html', {
            'form': form,
            'page_title': 'Consultation Report Generator'
        })
    
    def post(self, request):
        """Handle form submission"""
        form = ConsultationReportForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Save the report
            report = form.save()
            
            # Generate and return PDF
            try:
                return generate_pdf_report(report, request)
            except Exception as e:
                messages.error(request, f'Error generating PDF: {str(e)}')
                return render(request, 'reports/index.html', {
                    'form': form,
                    'page_title': 'Consultation Report Generator'
                })
        else:
            # Form has errors
            return render(request, 'reports/index.html', {
                'form': form,
                'page_title': 'Consultation Report Generator',
                'form_errors': form.errors
            })

@require_http_methods(["POST"])
def validate_form_ajax(request):
    """AJAX endpoint for real-time form validation"""
    try:
        data = json.loads(request.body)
        field_name = data.get('field')
        field_value = data.get('value')
        
        # Create a temporary form instance with the field data
        form_data = {field_name: field_value}
        form = ConsultationReportForm(form_data)
        
        # Validate specific field
        form.is_valid()
        field_errors = form.errors.get(field_name, [])
        
        return JsonResponse({
            'valid': len(field_errors) == 0,
            'errors': field_errors
        })
    except Exception as e:
        return JsonResponse({
            'valid': False,
            'errors': ['Validation error occurred']
        })

# Function-based views (alternative implementation)
def consultation_form(request):
    """Function-based view for consultation form"""
    if request.method == 'POST':
        form = ConsultationReportForm(request.POST, request.FILES)
        
        if form.is_valid():
            report = form.save()
            
            try:
                return generate_pdf_report(report, request)
            except Exception as e:
                messages.error(request, f'Error generating PDF: {str(e)}')
                
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ConsultationReportForm()
    
    return render(request, 'reports/index.html', {
        'form': form,
        'page_title': 'Consultation Report Generator'
    })

def preview_report(request, report_id):
    """Preview report data before PDF generation"""
    try:
        report = ConsultationReport.objects.get(id=report_id)
        return render(request, 'reports/preview.html', {
            'report': report,
            'page_title': f'Preview Report - {report.patient_full_name}'
        })
    except ConsultationReport.DoesNotExist:
        messages.error(request, 'Report not found.')
        return redirect('reports:index')
    
    