"""
Utility functions for generating PDF reports
"""

import io
import os
import requests
from datetime import datetime
from django.http import HttpResponse
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    # Try to get public IP
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        public_ip = response.json().get('ip')
        return public_ip if public_ip else ip
    except:
        return ip or 'Unknown'

def calculate_age(dob):
    """Calculate age from date of birth"""
    today = datetime.now().date()
    age = today.year - dob.year
    if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
        age -= 1
    return age

class ReportDocTemplate(BaseDocTemplate):
    """Custom document template with headers and footers"""
    
    def __init__(self, filename, report_data, timestamp, user_ip, **kwargs):
        BaseDocTemplate.__init__(self, filename, **kwargs)
        self.report_data = report_data
        self.timestamp = timestamp
        self.user_ip = user_ip
        
        # Create page template
        frame = Frame(
            self.leftMargin, self.bottomMargin,
            self.width, self.height - 100,
            id='normal'
        )
        
        template = PageTemplate(id='main', frames=[frame], onPage=self.add_page_decorations)
        self.addPageTemplates([template])
    
    def add_page_decorations(self, canvas, doc):
        """Add header and footer to each page"""
        canvas.saveState()
        
        # Header
        header_y = A4[1] - 50
        
        # Logo
        if self.report_data.clinic_logo:
            try:
                logo_path = os.path.join(settings.MEDIA_ROOT, str(self.report_data.clinic_logo))
                if os.path.exists(logo_path):
                    canvas.drawImage(
                        logo_path, 
                        72, header_y - 60, 
                        width=120, height=60,
                        preserveAspectRatio=True,
                        mask='auto'
                    )
            except Exception as e:
                print(f"Error adding logo: {e}")
        
        # Clinic name
        canvas.setFont("Helvetica-Bold", 18)
        canvas.setFillColor(HexColor('#1e40af'))
        canvas.drawCentredString(A4[0]/2, header_y - 30, self.report_data.clinic_name)
        
        # Header line
        canvas.setStrokeColor(HexColor('#1e40af'))
        canvas.setLineWidth(2)
        canvas.line(72, header_y - 80, A4[0] - 72, header_y - 80)
        
        # Footer
        footer_text = f"This report is generated on {self.timestamp} from {self.user_ip}"
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(HexColor('#666666'))
        canvas.drawCentredString(A4[0]/2, 50, footer_text)
        
        # Page number
        page_num = canvas.getPageNumber()
        canvas.drawCentredString(A4[0]/2, 35, f"Page {page_num}")
        
        # Footer line
        canvas.setStrokeColor(HexColor('#cccccc'))
        canvas.setLineWidth(1)
        canvas.line(72, 65, A4[0] - 72, 65)
        
        canvas.restoreState()

def generate_pdf_report(report_data, request):
    """Generate PDF report for consultation"""
    
    # Get timestamp and user IP
    timestamp = datetime.now().strftime('%B %d, %Y at %I:%M:%S %p %Z')
    user_ip = get_client_ip(request)
    
    # Create PDF buffer
    buffer = io.BytesIO()
    
    # Create document with custom template
    doc = ReportDocTemplate(
        buffer,
        report_data=report_data,
        timestamp=timestamp,
        user_ip=user_ip,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=130,
        bottomMargin=100
    )
    
    # Create styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=HexColor('#1e40af'),
        alignment=TA_CENTER,
        spaceAfter=30,
        spaceBefore=20
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#1e40af'),
        spaceBefore=25,
        spaceAfter=12,
        borderWidth=0,
        borderColor=HexColor('#e5e7eb'),
        leftIndent=0
    )
    
    content_style = ParagraphStyle(
        'ContentStyle',
        parent=styles['Normal'],
        fontSize=12,
        leftIndent=20,
        spaceAfter=8,
        leading=16
    )
    
    box_style = ParagraphStyle(
        'BoxStyle',
        parent=styles['Normal'],
        fontSize=11,
        leftIndent=20,
        rightIndent=20,
        spaceAfter=15,
        spaceBefore=10,
        borderWidth=1,
        borderColor=HexColor('#d1d5db'),
        borderPadding=15,
        backColor=HexColor('#f9fafb'),
        leading=18
    )
    
    # Build content
    story = []
    
    # Title
    story.append(Paragraph("CONSULTATION REPORT", title_style))
    story.append(Spacer(1, 20))
    
    # Clinic Information
    story.append(Paragraph("Clinic Information", section_style))
    story.append(Spacer(1, 5))
    story.append(Paragraph(f"<b>Clinic Name:</b> {report_data.clinic_name}", content_style))
    story.append(Paragraph(f"<b>Report Generated:</b> {timestamp}", content_style))
    story.append(Spacer(1, 20))
    
    # Physician Information
    story.append(Paragraph("Physician Information", section_style))
    story.append(Spacer(1, 5))
    story.append(Paragraph(f"<b>Physician Name:</b> {report_data.physician_name}", content_style))
    story.append(Paragraph(f"<b>Physician Contact:</b> {report_data.physician_contact}", content_style))
    story.append(Spacer(1, 20))
    
    # Patient Information
    story.append(Paragraph("Patient Information", section_style))
    story.append(Spacer(1, 5))
    story.append(Paragraph(f"<b>Patient Name:</b> {report_data.patient_full_name}", content_style))
    
    # Format date of birth
    dob_formatted = report_data.patient_dob.strftime('%B %d, %Y')
    patient_age = calculate_age(report_data.patient_dob)
    
    story.append(Paragraph(f"<b>Date of Birth:</b> {dob_formatted}", content_style))
    story.append(Paragraph(f"<b>Age:</b> {patient_age} years", content_style))
    story.append(Paragraph(f"<b>Patient Contact:</b> {report_data.patient_contact}", content_style))
    story.append(Spacer(1, 30))
    
    # Chief Complaint
    story.append(Paragraph("Chief Complaint", section_style))
    complaint_text = report_data.chief_complaint.replace('\n', '<br/>')
    story.append(Paragraph(complaint_text, box_style))
    story.append(Spacer(1, 20))
    
    # Page break before consultation note
    story.append(PageBreak())
    
    # Consultation Note
    story.append(Paragraph("Consultation Note", section_style))
    note_text = report_data.consultation_note.replace('\n', '<br/>')
    story.append(Paragraph(note_text, box_style))
    story.append(Spacer(1, 50))
    
    # End of report
    end_style = ParagraphStyle(
        'EndStyle',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=14,
        textColor=HexColor('#6b7280'),
        borderWidth=1,
        borderColor=HexColor('#e5e7eb'),
        borderPadding=20,
        backColor=HexColor('#f9fafb')
    )
    
    story.append(Paragraph(
        "<b>--- End of Consultation Report ---</b><br/><br/>"
        "<i>This document was electronically generated and is valid without signature.</i>", 
        end_style
    ))
    
    # Build PDF
    doc.build(story)
    
    # Get PDF data
    pdf_data = buffer.getvalue()
    buffer.close()
    
    # Create response
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report_data.pdf_filename}"'
    
    return response