from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = 'birth'

urlpatterns = [
    # path('', views.home, name='home'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/login/', views.user_login, name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='birth:home'), name='logout'),


    path('birth_certificate_instructions/', views.birth_certificate_instructions, name='birth_certificate_instructions'),
    path('birth-certificate/apply/', views.birth_certificate_application, name='birth_certificate_application'),
    path('birth-certificate/documents/<int:application_id>/', views.document_upload, name='document_upload'),
    path('applications/<int:application_id>/status/', views.application_status, name='application_status'),
    path('my-applications/', views.my_applications, name='my_applications'),
    # path('admin/test-sms/', views.test_sms, name='test_sms'),


    # Payment URLs
    path('application/<int:application_id>/payment/', views.initiate_payment, name='initiate_payment'),
    path('payment/success/<int:application_id>/', views.payment_success, name='payment_success'),
    path('payment/webhook/', views.payment_webhook, name='payment_webhook'),
]