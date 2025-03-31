from rest_framework import viewsets, permissions
from .models import BirthCertificateApplication, Document
from .serializers import BirthCertificateApplicationSerializer, DocumentSerializer

class BirthCertificateApplicationViewSet(viewsets.ModelViewSet):
    queryset = BirthCertificateApplication.objects.all()
    serializer_class = BirthCertificateApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]