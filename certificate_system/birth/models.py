from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class BirthCertificateApplication(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('payment_pending', 'Payment Pending'),
        ('payment_completed', 'Payment Completed'),
        ('processing', 'Processing'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    child_name = models.CharField(max_length=100)
    parent_name = models.CharField(max_length=100)
    parent_aadhaar = models.CharField(max_length=12)
    place_of_birth = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    permanent_address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.child_name}'s Birth Certificate Application"

class BirthCertificateDocument(models.Model):
    application = models.ForeignKey(BirthCertificateApplication, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50)
    document_file = models.FileField(upload_to='birth_certificate_docs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.document_type} for {self.application.child_name}"
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

