import json
from django.contrib import admin
from django.urls import path
from .models import BirthCertificateApplication, BirthCertificateDocument  # Updated import path
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.html import format_html

@admin.register(BirthCertificateApplication)
class BirthCertificateApplicationAdmin(admin.ModelAdmin):
    list_display = ('child_name', 'parent_name', 'status', 'created_at', 'user', 'admin_actions')
    list_filter = ('status', 'created_at')
    search_fields = ('child_name', 'parent_name', 'parent_aadhaar', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'user', 'ai_analysis_display')
    actions = ['approve_selected', 'reject_selected']
    
    fieldsets = (
        ('Application Details', {
            'fields': ('user', 'child_name', 'parent_name', 'parent_aadhaar')
        }),
        ('Birth Information', {
            'fields': ('place_of_birth', 'date_of_birth', 'permanent_address')
        }),
        ('Status', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
        ('AI Analysis', {
            'fields': ('ai_analysis_display',)
        }),
    )
    
    def ai_analysis_display(self, obj):
        if obj.ai_analysis:
            return format_html('<pre>{}</pre>', json.dumps(obj.ai_analysis, indent=2))
        return "No analysis available"
    ai_analysis_display.short_description = 'AI Analysis'
    
    def admin_actions(self, obj):
        if obj.status in ['submitted', 'processing']:
            return format_html(
                '<a class="button" href="{}">Approve</a> &nbsp;'
                '<a class="button" href="{}">Reject</a>',
                f'{obj.id}/approve/',
                f'{obj.id}/reject/',
            )
        return ""
    admin_actions.short_description = 'Actions'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/approve/',
                 self.admin_site.admin_view(self.process_approval)),
            path('<path:object_id>/reject/',
                 self.admin_site.admin_view(self.process_rejection)),
        ]
        return custom_urls + urls
    
    def process_approval(self, request, object_id):
        application = self.get_object(request, object_id)
        application.status = 'approved'
        application.save()
        messages.success(request, f"Application for {application.child_name} has been approved")
        return redirect('admin:birth_birthcertificateapplication_changelist')
    
    def process_rejection(self, request, object_id):
        application = self.get_object(request, object_id)
        application.status = 'rejected'
        application.save()
        messages.success(request, f"Application for {application.child_name} has been rejected")
        return redirect('admin:birth_birthcertificateapplication_changelist')
    
    def approve_selected(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f"{queryset.count()} applications approved")
    approve_selected.short_description = "Approve selected applications"
    
    def reject_selected(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} applications rejected")
    reject_selected.short_description = "Reject selected applications"

@admin.register(BirthCertificateDocument)
class BirthCertificateDocumentAdmin(admin.ModelAdmin):
    list_display = ('application', 'document_type', 'uploaded_at', 'document_link')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('application__child_name', 'document_type')
    list_per_page = 20
    date_hierarchy = 'uploaded_at'
    
    def document_link(self, obj):
        from django.utils.html import format_html
        if obj.document_file:
            return format_html('<a href="{}" target="_blank">View Document</a>', obj.document_file.url)
        return "-"
    document_link.short_description = 'Document'