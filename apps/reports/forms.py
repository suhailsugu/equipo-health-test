from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
from .models import ConsultationReport

class ConsultationReportForm(forms.ModelForm):
    """Form for creating consultation reports"""
    
    class Meta:
        model = ConsultationReport
        fields = [
            'clinic_name', 'clinic_logo', 'physician_name', 'physician_contact',
            'patient_first_name', 'patient_last_name', 'patient_dob', 'patient_contact',
            'chief_complaint', 'consultation_note'
        ]
        
        widgets = {
            'clinic_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter clinic name'
            }),
            'clinic_logo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'physician_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter physician name'
            }),
            'physician_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email or phone number'
            }),
            'patient_first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter patient first name'
            }),
            'patient_last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter patient last name'
            }),
            'patient_dob': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'patient_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email or phone number'
            }),
            'chief_complaint': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Enter chief complaint...',
                'maxlength': 5000
            }),
            'consultation_note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Enter consultation note...',
                'maxlength': 5000
            }),
        }
        
        labels = {
            'clinic_name': 'Clinic Name',
            'clinic_logo': 'Clinic Logo',
            'physician_name': 'Physician Name',
            'physician_contact': 'Physician Contact',
            'patient_first_name': 'Patient First Name',
            'patient_last_name': 'Patient Last Name',
            'patient_dob': 'Patient DoB',
            'patient_contact': 'Patient Contact',
            'chief_complaint': 'Chief Complaint',
            'consultation_note': 'Consultation Note',
        }

    def clean_physician_contact(self):
        """Validate physician contact (email or phone)"""
        contact = self.cleaned_data.get('physician_contact')
        if contact:
            if not self._is_valid_contact(contact):
                raise ValidationError('Please enter a valid email address or phone number.')
        return contact

    def clean_patient_contact(self):
        """Validate patient contact (email or phone)"""
        contact = self.cleaned_data.get('patient_contact')
        if contact:
            if not self._is_valid_contact(contact):
                raise ValidationError('Please enter a valid email address or phone number.')
        return contact

    def clean_clinic_logo(self):
        """Validate uploaded logo file"""
        logo = self.cleaned_data.get('clinic_logo')
        if logo:
            # Check file size (max 5MB)
            if logo.size > 5 * 1024 * 1024:
                raise ValidationError('File size cannot exceed 5MB.')
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if hasattr(logo, 'content_type') and logo.content_type not in allowed_types:
                raise ValidationError('Please upload a valid image file (JPEG, PNG, GIF, or WebP).')
        
        return logo

    def clean_chief_complaint(self):
        """Validate chief complaint length"""
        complaint = self.cleaned_data.get('chief_complaint')
        if complaint and len(complaint) > 5000:
            raise ValidationError('Chief complaint cannot exceed 5000 characters.')
        return complaint

    def clean_consultation_note(self):
        """Validate consultation note length"""
        note = self.cleaned_data.get('consultation_note')
        if note and len(note) > 5000:
            raise ValidationError('Consultation note cannot exceed 5000 characters.')
        return note

    def _is_valid_contact(self, contact):
        """Check if contact is valid email or phone number"""
        # Check email
        try:
            validate_email(contact)
            return True
        except ValidationError:
            pass
        
        # Check phone number (simple pattern)
        phone_pattern = r'^[\+]?[1-9][\d]{0,15}$|^[\d\s\-\(\)]{10,}$'
        if re.match(phone_pattern, contact.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')):
            return True
        
        return False