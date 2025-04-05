from django import forms
from .models import BirthCertificateApplication, BirthCertificateDocument
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class BirthCertificateApplicationForm(forms.ModelForm):
    class Meta:
        model = BirthCertificateApplication
        fields = [
            'child_name',
            'parent_name',
            'parent_aadhaar',
            'place_of_birth',
            'date_of_birth',
            'permanent_address',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class BirthCertificateDocumentForm(forms.ModelForm):
    class Meta:
        model = BirthCertificateDocument
        fields = ['document_type', 'document_file']

class DocumentUploadForm(forms.Form):
    MAX_UPLOAD_SIZE = 5 * 1024 * 1024
    birth_certificate = forms.FileField(label='Birth Certificate from the hospital', required=True)
    statement_of_birth = forms.FileField(label='Statement of birth from the hospital or birthplace', required=True)
    marriage_certificate = forms.FileField(label="Parent's marriage certificate", required=True)
    parent_id = forms.FileField(label="Parent's Identification Documents", required=True)
    parent_aadhaar = forms.FileField(label="Aadhaar card of parents", required=True)

    def clean(self):
        cleaned_data = super().clean()
        for field_name, file in self.files.items():
            if file.size > self.MAX_UPLOAD_SIZE:
                raise ValidationError(
                    f"The file '{field_name.replace('_', ' ')}' exceeds the 5MB size limit."
                )
        return cleaned_data
    


class CustomRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    

