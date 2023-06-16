from django.contrib import admin
from .models import ProductRequest, Profile

# Register your models here.
admin.site.register(Profile)
admin.site.register(ProductRequest)