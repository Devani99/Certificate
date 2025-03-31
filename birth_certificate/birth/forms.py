from django import forms
from .models import BirthCertificateApplication, Document

class BirthCertificateApplicationForm(forms.ModelForm):
    class Meta:
        model = BirthCertificateApplication
        fields = '__all__'
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'permanent_address': forms.Textarea(attrs={'rows': 3}),
        }



class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_type', 'file']
        
    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application', None)
        super().__init__(*args, **kwargs)
        # Filter out already uploaded document types
        if self.application:
            existing_types = self.application.documents.values_list('document_type', flat=True)
            self.fields['document_type'].choices = [
                (k, v) for k, v in BirthCertificateApplication.DOCUMENT_TYPES 
                if k not in existing_types
            ]