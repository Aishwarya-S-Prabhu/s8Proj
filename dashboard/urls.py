from tkinter import N
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',views.index,name='dashboard-index'),
    
    path('staff/', views.staff, name='dashboard-staff'),
    path('users/', views.users, name='dashboard-users'),
    path('sales/', views.sales, name='dashboard-sales')
]