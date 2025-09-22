from django.db import models
from django.core.validators import MaxLengthValidator
import os

def logo_upload_path(instance, filename):
    """Generate upload path for clinic logos"""
    return f'logos/{filename}'

class ConsultationReport(models.Model):
    """Model to store consultation report data"""
    
    # Clinic Information
    clinic_name = models.CharField(max_length=255)
    clinic_logo = models.ImageField(upload_to=logo_upload_path, blank=True, null=True)
    
    # Physician Information  
    physician_name = models.CharField(max_length=255)
    physician_contact = models.CharField(max_length=255)
    
    # Patient Information
    patient_first_name = models.CharField(max_length=255)
    patient_last_name = models.CharField(max_length=255)
    patient_dob = models.DateField()
    patient_contact = models.CharField(max_length=255)
    
    # Consultation Details
    chief_complaint = models.TextField(validators=[MaxLengthValidator(5000)])
    consultation_note = models.TextField(validators=[MaxLengthValidator(5000)])
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Consultation Report'
        verbose_name_plural = 'Consultation Reports'
    
    def __str__(self):
        return f"Report for {self.patient_first_name} {self.patient_last_name} - {self.created_at.date()}"
    
    @property
    def patient_full_name(self):
        return f"{self.patient_first_name} {self.patient_last_name}"
    
    @property
    def pdf_filename(self):
        """Generate PDF filename according to specifications"""
        dob_str = self.patient_dob.strftime('%Y%m%d')
        return f"CR_{self.patient_last_name}_{self.patient_first_name}_{dob_str}.pdf"
    
    def delete(self, *args, **kwargs):
        """Delete logo file when model instance is deleted"""
        if self.clinic_logo:
            if os.path.isfile(self.clinic_logo.path):
                os.remove(self.clinic_logo.path)
        super().delete(*args, **kwargs)