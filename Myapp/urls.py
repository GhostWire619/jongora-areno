"""
URL configuration for Myapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include, get_resolver
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.shortcuts import render
from drf_yasg.generators import OpenAPISchemaGenerator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.schemas import AutoSchema
from .api_docs import get_all_urls, categorize_url, generate_swagger_paths

class CustomSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        # Add all URL patterns to schema
        schema.paths = self._get_all_paths(schema)
        return schema
    
    def _get_all_paths(self, schema):
        paths = schema.paths
        
        # Generate paths for all URLs
        auto_paths = generate_swagger_paths()
        
        # Merge auto-generated paths with existing paths
        for path, methods in auto_paths.items():
            if path not in paths:
                paths[path] = methods
            else:
                # If path exists, merge methods
                for method, operation in methods.items():
                    if method not in paths[path]:
                        paths[path][method] = operation
        
        # Add any manually specified paths
        self._add_manual_paths(paths)
        
        return paths
    
    def _add_manual_paths(self, paths):
        """Add important paths that might not be captured automatically"""
        # Main pages
        self._add_path(paths, '/', 'Home page', 'Main landing page of the application')
        self._add_path(paths, '/api/', 'API Root', 'Root of all API endpoints')
        self._add_path(paths, '/admin/', 'Admin Interface', 'Django admin interface')
        self._add_path(paths, '/swagger/', 'Swagger UI', 'API documentation')
        self._add_path(paths, '/redoc/', 'ReDoc', 'Alternative API documentation')
    
    def _add_path(self, paths, path, summary, description):
        """Add a path with basic documentation"""
        if path not in paths:
            paths[path] = {
                'get': {
                    'tags': self._get_tag_for_path(path),
                    'summary': summary,
                    'description': description,
                    'responses': {
                        '200': {
                            'description': 'Successful operation'
                        }
                    }
                }
            }
    
    def _get_tag_for_path(self, path):
        """Get appropriate tag based on path"""
        return [categorize_url(path)]

schema_view = get_schema_view(
    openapi.Info(
        title="ArenoApp Complete Documentation",
        default_version='v1',
        description="""
        Complete documentation for ArenoApp - an e-commerce platform with multiple modules:
        
        * **API Endpoints** - REST API endpoints for integration
        * **Shopping** - Products, brands, categories, and sellers
        * **Restaurants** - Food items, restaurant listings, and meal ordering
        * **Booking** - Events, accommodations, adventures, and car rentals
        * **User Management** - Registration, authentication, and profiles
        * **Admin** - Administrative interfaces and tools
        
        Note: This documentation includes both API endpoints (under the API tag) 
        and regular web views. API endpoints are suitable for programmatic integration,
        while web views are designed for browser access.
        """,
        terms_of_service="https://www.areno.co.tz/terms/",
        contact=openapi.Contact(email="contact@areno.co.tz"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    generator_class=CustomSchemaGenerator,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ArenoApp.urls')),
    path('api/', include('Customer_Apis.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger/custom/', lambda request: render(request, 'swagger-ui.html'), name='schema-swagger-custom'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    #ck editor
    path("ckeditor5/", include('django_ckeditor_5.urls'), name="ck_editor_5_upload_file"),

] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


import os
from urllib.parse import urljoin

from django.core.files.storage import FileSystemStorage


class CustomStorage(FileSystemStorage):
    """Custom storage for django_ckeditor_5 images."""

    location = os.path.join(settings.MEDIA_ROOT, "django_ckeditor_5")
    base_url = urljoin(settings.MEDIA_URL, "django_ckeditor_5/")







