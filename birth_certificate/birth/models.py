from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
import requests
from django.conf import settings

class BirthCertificateApplication(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('processing', 'Processing'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    DOCUMENT_TYPES = [
        ('birth_cert', 'Birth Certificate from hospital'),
        ('statement', 'Statement of birth from hospital/birthplace'),
        ('marriage_cert', "Parent's marriage certificate"),
        ('parent_id', "Parent's Identification Documents"),
        ('aadhaar', "Aadhaar card of parents"),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Personal Details
    child_name = models.CharField(max_length=100)
    parent_name = models.CharField(max_length=100)
    parent_aadhaar = models.CharField(max_length=12)
    place_of_birth = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    permanent_address = models.TextField()
    
    # AI suggestions (can be stored as JSON)
    ai_suggestions = models.JSONField(blank=True, null=True)
    
    def __str__(self):
        return f"Birth Certificate Application - {self.child_name}"
    
    def analyze_with_ai(self):
        """Send documents to AI service for analysis"""
        if not settings.AI_SERVICE_URL:
            return None
            
        documents = list(self.documents.all())
        payload = {
            'application_id': self.id,
            'documents': [{'type': doc.document_type, 'url': doc.file.url} for doc in documents],
            'application_data': {
                'child_name': self.child_name,
                'parent_name': self.parent_name,
                'date_of_birth': str(self.date_of_birth),
                'place_of_birth': self.place_of_birth
            }
        }
        
        try:
            response = requests.post(
                settings.AI_SERVICE_URL,
                json=payload,
                headers={'Authorization': f'Bearer {settings.AI_API_KEY}'}
            )
            response.raise_for_status()
            self.ai_suggestions = response.json()
            self.save()
            return self.ai_suggestions
        except requests.RequestException as e:
            print(f"AI Analysis failed: {e}")
            return None

class Document(models.Model):
    application = models.ForeignKey(BirthCertificateApplication, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=BirthCertificateApplication.DOCUMENT_TYPES)
    file = models.FileField(upload_to='birth_cert_docs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    def clean(self):
        # Case-insensitive check for existing documents of same type
        if Document.objects.filter(
            application=self.application,
            document_type__iexact=self.document_type
        ).exclude(pk=self.pk).exists():
            raise ValidationError(
                f"A document of type {self.document_type} already exists for this application"
            )


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['application', 'document_type'],
                name='unique_document_per_application'
            )
        ]

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.application.child_name}"