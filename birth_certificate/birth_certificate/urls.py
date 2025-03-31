"""
URL configuration for birth_certificate project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from birth import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from birth.api import BirthCertificateApplicationViewSet, DocumentViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('birth_certificate/instructions/', views.birth_certificate_instructions, name='birth_certificate_instructions'),
    path('birth_certificate/create/', views.create_birth_certificate, name='create_birth_certificate'),
    path('birth_certificate/<int:application_id>/upload_documents/', views.upload_document, name='upload_documents'),
    path('birth_certificate/<int:application_id>/status/', views.application_status, name='application_status'),
    path('applications/', views.view_applications, name='view_applications'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


router = DefaultRouter()
router.register(r'api/applications', BirthCertificateApplicationViewSet)
router.register(r'api/documents', DocumentViewSet)

urlpatterns += router.urls