from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse

def generate_birth_certificate_pdf(application):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    
    # Add certificate content
    p.drawString(100, 800, "OFFICIAL BIRTH CERTIFICATE")
    p.drawString(100, 780, f"Certificate No: {application.id}")
    p.drawString(100, 760, f"Child Name: {application.child_name}")
    # ... add more fields ...
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer