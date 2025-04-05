from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import BirthCertificateApplication
import logging
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from .models import Profile
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Profile


logger = logging.getLogger(__name__)

@receiver(post_save, sender=BirthCertificateApplication)
def send_status_notification(sender, instance, **kwargs):
    """
    Send email and SMS notifications when application status changes
    """
    if kwargs.get('created', False):
        return  # Skip for new creations
    
    try:
        # Get previous status from database
        if instance.pk:
            old_instance = BirthCertificateApplication.objects.get(pk=instance.pk)
            previous_status = old_instance.status
        else:
            previous_status = None
        
        # Only send if status changed
        if previous_status != instance.status:
            # Email Notification
            subject = f"Birth Certificate Status Update: {instance.get_status_display()}"
            
            context = {
                'application': instance,
                'status': instance.get_status_display(),
                'child_name': instance.child_name,
                'support_email': settings.SUPPORT_EMAIL
            }
            
            html_message = render_to_string('birth/email/status_notification.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            # SMS Notification (if Twilio is configured)
            if all(hasattr(settings, attr) for attr in ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_PHONE_NUMBER']):
                try:
                    from twilio.rest import Client
                    
                    # Get phone number from user profile
                    phone_number = getattr(instance.user, 'profile', None) and instance.user.profile.phone_number
                    if phone_number:
                        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                        client.messages.create(
                            body=f"Birth Cert Status: {instance.get_status_display()} for {instance.child_name}",
                            from_=settings.TWILIO_PHONE_NUMBER,
                            to=phone_number
                        )
                        logger.info(f"SMS notification sent to {phone_number}")
                    else:
                        logger.warning("No phone number found for SMS notification")
                except Exception as sms_error:
                    logger.error(f"Failed to send SMS: {str(sms_error)}")
            
            logger.info(f"Notifications sent for application {instance.id}")
            
    except Exception as e:
        logger.error(f"Error sending notifications: {str(e)}")


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        
        # Check if profile exists and has valid phone number
        if not hasattr(user, 'profile'):
            try:
                Profile.objects.create(user=user, phone_number=None)
            except ValidationError:
                # Redirect to profile completion page
                return redirect('profile_complete')  # You'll need to create this view
        
        elif not user.profile.phone_number:
            return redirect('profile_complete')
            
        return response
    


