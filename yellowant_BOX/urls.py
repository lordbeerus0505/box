"""yellowant_BOX URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import include, path
from django.contrib import admin
from django.views.generic.base import TemplateView

from lib.web import urls as web_urls
from lib.yellowant_api import urls as yellowant_api_urls
from lib.yellowant_api import views

urlpatterns = [
    path('', include(yellowant_api_urls)),
    path("accounts/", include('django.contrib.auth.urls')),
    path("admin/", admin.site.urls),
    path('', include(web_urls)),
]
