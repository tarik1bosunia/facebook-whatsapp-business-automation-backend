"""
URL configuration for facebook_business_automation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .utils.views import HealthCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/chatbot/', include('chatbot.urls')),
    path('api/account/', include('account.urls')),
    path('api/business/', include('business.urls')),
    path('api/customer/', include('customer.urls')),
    path('api/messaging/', include('messaging.urls')),
    path('api/knowledge-base/', include('knowledge_base.urls')),
    path('api/analytics/', include('analytics.urls')),
    # path('api/integrations/', include('apps.integrations.urls')),
    path('health/', HealthCheckView.as_view()),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
