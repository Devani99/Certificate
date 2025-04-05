import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from .models import BirthCertificateApplication, BirthCertificateDocument
from .forms import CustomRegisterForm, BirthCertificateApplicationForm, DocumentUploadForm
from .ai_services import analyze_document
import razorpay
from razorpay.errors import SignatureVerificationError
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

@login_required
def home(request):
    return render(request, 'birth/home.html')

@login_required
def birth_certificate_instructions(request):
    return render(request, 'birth/birth_certificate_instructions.html')

@login_required
def birth_certificate_application(request):
    if request.method == 'POST':
        form = BirthCertificateApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            return redirect('document_upload', application_id=application.id)
    else:
        form = BirthCertificateApplicationForm()
    return render(request, 'birth/birth_certificate_application.html', {'form': form})

@login_required
def document_upload(request, application_id):
    application = get_object_or_404(BirthCertificateApplication, id=application_id, user=request.user)
    
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                ai_results = {}
                for field_name, file in request.FILES.items():
                    ai_results[field_name] = analyze_document(file)
                
                application.ai_analysis = ai_results
                application.save()
                
                has_errors = any(not result['is_valid'] for result in ai_results.values())
                
                if has_errors:
                    return render(request, 'birth/document_errors.html', {
                        'application': application,
                        'ai_results': ai_results
                    })
                
                document_types = {
                    'birth_certificate': 'Birth Certificate from Hospital',
                    'statement_of_birth': 'Statement of Birth',
                    'marriage_certificate': 'Parent Marriage Certificate',
                    'parent_id': 'Parent Identification',
                    'parent_aadhaar': 'Parent Aadhaar Card',
                }
                
                for field_name, doc_type in document_types.items():
                    if field_name in request.FILES:
                        BirthCertificateDocument.objects.create(
                            application=application,
                            document_type=doc_type,
                            document_file=request.FILES[field_name]
                        )
                
                application.status = 'submitted'
                application.save()
                messages.success(request, 'Application submitted successfully!')
                return redirect('application_status', application_id=application.id)
            
            except Exception as e:
                messages.error(request, f"Error saving documents: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = DocumentUploadForm()
    
    return render(request, 'birth/document_upload.html', {
        'form': form,
        'application': application
    })

@login_required
def application_status(request, application_id):
    application = get_object_or_404(BirthCertificateApplication, id=application_id, user=request.user)
    return render(request, 'birth/application_status.html', {'application': application})

@login_required
def my_applications(request):
    applications = BirthCertificateApplication.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'birth/my_applications.html', {'applications': applications})

@login_required
def initiate_payment(request, application_id):
    application = get_object_or_404(BirthCertificateApplication, id=application_id, user=request.user)
    
    if application.status != 'payment_pending':
        messages.warning(request, "Payment is not required for this application")
        return redirect('application_status', application_id=application.id)
    
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    payment_data = {
        'amount': 10000,  # 100 INR in paise
        'currency': 'INR',
        'receipt': f'birth_cert_{application.id}',
        'notes': {
            'application_id': application.id,
            'user_id': request.user.id
        }
    }
    
    order = client.order.create(data=payment_data)
    
    return render(request, 'birth/payment.html', {
        'application': application,
        'order_id': order['id'],
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount': payment_data['amount'],
        'currency': payment_data['currency'],
        'user': request.user
    })

@login_required
def payment_success(request, application_id):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    if request.method == 'POST':
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': request.POST.get('razorpay_order_id'),
                'razorpay_payment_id': request.POST.get('razorpay_payment_id'),
                'razorpay_signature': request.POST.get('razorpay_signature')
            })
            
            application = get_object_or_404(BirthCertificateApplication, id=application_id, user=request.user)
            application.status = 'payment_completed'
            application.save()
            
            messages.success(request, "Payment successful! Your application is now being processed.")
            return redirect('application_status', application_id=application.id)
            
        except SignatureVerificationError:
            messages.error(request, "Payment verification failed")
            return redirect('initiate_payment', application_id=application_id)
    
    return redirect('home')

@csrf_exempt
def payment_webhook(request):
    if request.method == 'POST':
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            client.utility.verify_webhook_signature(
                request.body.decode('utf-8'),
                request.META.get('HTTP_X_RAZORPAY_SIGNATURE', ''),
                settings.RAZORPAY_WEBHOOK_SECRET
            )
            return HttpResponse(status=200)
        except Exception as e:
            print(f"Error processing webhook: {str(e)}")
            return HttpResponse(status=500)
    return HttpResponse(status=405)

def register(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login')
    else:
        form = CustomRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

@staff_member_required
def test_sms(request):
    if not request.user.is_superuser:
        return JsonResponse({"error": "Unauthorized"}, status=403)
    
    try:
        if not all(hasattr(settings, attr) for attr in ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_PHONE_NUMBER']):
            return JsonResponse({"error": "Twilio not configured"}, status=500)
        
        phone_number = request.GET.get('to')
        if not phone_number:
            return JsonResponse({"error": "Missing 'to' parameter"}, status=400)
        
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body="[Test] Birth Certificate App: SMS system is working!",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return JsonResponse({
            "status": "success",
            "sid": message.sid,
            "to": phone_number
        })
    except TwilioRestException as e:
        return JsonResponse({"error": str(e)}, status=500)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'registration/login.html')

# def custom_logout(request):
#     logout(request)
#     messages.success(request, "You have been logged out successfully.")
#     return redirect('home')

# def logout_confirm(request):
#     return render(request, 'registration/logout_confirm.html')