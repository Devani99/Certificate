from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import BirthCertificateApplication, Document
from .forms import BirthCertificateApplicationForm, DocumentUploadForm
from .utils import generate_birth_certificate_pdf

@login_required
def home(request):
    return render(request, 'birth/home.html')

@login_required
def birth_certificate_instructions(request):
    return render(request, 'birth/birth_certificate_instructions.html')

@login_required
def create_birth_certificate(request):
    if request.method == 'POST':
        form = BirthCertificateApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            messages.success(request, 'Application created successfully!')
            return redirect('upload_documents', application_id=application.id)
    else:
        form = BirthCertificateApplicationForm()
    
    return render(request, 'birth/create_birth_certificate.html', {'form': form})

@login_required
def upload_document(request, application_id):
    application = get_object_or_404(BirthCertificateApplication, id=application_id, user=request.user)
    
    # Prepare document status for template
    document_status = []
    for doc_type, doc_name in BirthCertificateApplication.DOCUMENT_TYPES:
        document = application.documents.filter(document_type=doc_type).first()
        document_status.append({
            'type': doc_type,
            'name': doc_name,
            'uploaded': document is not None,
            'document': document
        })
    
    # Check if all documents are uploaded
    uploaded_types = set(application.documents.values_list('document_type', flat=True))
    required_types = set(dt[0] for dt in BirthCertificateApplication.DOCUMENT_TYPES)
    all_uploaded = uploaded_types.issuperset(required_types)

    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES, application=application)
        if form.is_valid():
            document = form.save(commit=False)
            document.application = application
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('upload_documents', application_id=application.id)
    else:
        form = DocumentUploadForm(application=application)
    
    return render(request, 'birth/upload_documents.html', {
        'form': form,
        'application': application,
        'document_status': document_status,
        'all_uploaded': all_uploaded,
        'DOCUMENT_TYPES': BirthCertificateApplication.DOCUMENT_TYPES
    })

@login_required
def document_update(request, document_id):
    document = get_object_or_404(Document, id=document_id, application__user=request.user)
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            messages.success(request, 'Document updated successfully!')
            return redirect('upload_documents', application_id=document.application.id)
    else:
        form = DocumentUploadForm(instance=document)
    return render(request, 'birth/document_update.html', {
        'form': form,
        'document': document
    })

@login_required
def application_status(request, application_id):
    application = get_object_or_404(BirthCertificateApplication, id=application_id, user=request.user)
    return render(request, 'birth/application_status.html', {
        'application': application
    })

@login_required
def view_applications(request):
    applications = BirthCertificateApplication.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'birth/view_applications.html', {
        'applications': applications
    })

@login_required
def download_certificate(request, application_id):
    application = get_object_or_404(BirthCertificateApplication, id=application_id, user=request.user)
    if application.status != 'approved':
        messages.error(request, 'Certificate not yet approved')
        return redirect('application_status', application_id=application.id)
    
    buffer = generate_birth_certificate_pdf(application)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="birth_certificate_{application.id}.pdf"'
    return response