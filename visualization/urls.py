"""
URL configuration for vmshop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from . import views

urlpatterns = [
    
    path('vmshop/', views.vmshop, name='vmshop'),
    path('vmowner/', views.vmowner, name='vmowner'),
    path('outvmo', views.outvmo, name='outvmo'),
    path('outvms', views.outvms, name='outvms'),
    path('vmprod/', views.vmprod, name='vmprod'),
    path('outvmp', views.outvmp, name='outvmp'),
    path('outvmscompare', views.outvmscompare, name='outvmscompare'),
    path('outvmpprodwise', views.outvmpprodwise, name='outvmpprodwise'),
    path('outvmpshopwise', views.outvmpshopwise, name='outvmpshopwise'),

    path('outvmoshop', views.outvmoshop, name='outvmoshop'),
    path('outvmovms/<str:selected_shop>/', views.outvmovms, name='outvmovms'),
    path('outvmoprod', views.outvmoprod, name='outvmoprod'),
    path('outvmovmp/<str:selected_product>/', views.outvmovmp, name='outvmovmp'),
    path('outvmovmscompare/<str:selected_shop>/', views.outvmovmscompare, name='outvmovmscompare'),
  




]
