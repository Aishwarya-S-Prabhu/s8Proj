from django.contrib import admin
from .models import Users, Sales,Producer
from django.contrib.auth.models import Group

admin.site.site_header = 'Simplyfy Dashboard'

class UserAdmin(admin.ModelAdmin):
    list_display = ('name','category','quantity',)
    list_filter = ('category',)

# Register your models here.
admin.site.register(Users,UserAdmin)
admin.site.register(Sales)
admin.site.register(Producer)
#admin.site.unregister(Group)