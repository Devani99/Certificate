from rest_framework import serializers
from .models import BirthCertificateApplication, Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'document_type', 'file', 'uploaded_at']

class BirthCertificateApplicationSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = BirthCertificateApplication
        fields = '__all__'
        read_only_fields = ['user', 'status', 'created_at', 'updated_at']