from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import BirthCertificateApplication

@receiver(post_save, sender=BirthCertificateApplication)
def send_status_notification(sender, instance, **kwargs):
    if instance.status_changed():
        subject = f"Birth Certificate Application Status Update - {instance.child_name}"
        message = f"""
        Dear {instance.user.username},
        
        Your application for {instance.child_name}'s birth certificate is now {instance.get_status_display()}.
        
        Application ID: {instance.id}
        Child Name: {instance.child_name}
        Status: {instance.get_status_display()}
        
        Thank you,
        Certificate Issuance System
        """
        send_mail(
            subject,
            message,
            'noreply@certificatesystem.com',
            [instance.user.email],
            fail_silently=False,
        )