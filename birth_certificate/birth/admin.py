from django.contrib import admin

# Register your models here.
from .models import BirthCertificateApplication, Document

@admin.register(BirthCertificateApplication)
class BirthCertificateApplicationAdmin(admin.ModelAdmin):
    list_display = ('get_child_name', 'get_parent_name', 'get_status', 'get_created_at')
    list_filter = ('status', 'created_at')
    
    def get_child_name(self, obj):
        return obj.child_name
    get_child_name.short_description = 'Child Name'
    
    def get_parent_name(self, obj):
        return obj.parent_name
    get_parent_name.short_description = 'Parent Name'
    
    def get_status(self, obj):
        return obj.status
    get_status.short_description = 'Status'
    
    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

class DocumentInline(admin.StackedInline):
    model = Document
    extra = 1

# Add the inline to your admin if needed
BirthCertificateApplicationAdmin.inlines = [DocumentInline]