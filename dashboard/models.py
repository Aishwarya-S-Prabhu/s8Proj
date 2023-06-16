from pyexpat import model
from re import T
from statistics import mode, quantiles
from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
CATEGORY = (
    ('Stationary','Stationary'),
    ('Electronics','Electronics'),
    ('Food','Food'),

)
class Users(models.Model):
    name = models.CharField(max_length=100,null=True)
    category = models.CharField(max_length=20,choices=CATEGORY,null=True)
    quantity = models.PositiveIntegerField(null=True)


    class Meta:
        verbose_name_plural = 'User'

    def __str__(self):
        return f'{self.name}-{self.quantity}'

class Sales(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE,null=True)
    staff = models.ForeignKey(User, models.CASCADE,null=True)
    order_quantity = models.PositiveIntegerField(null=True)
    date = models.DateTimeField(auto_now_add=True)

   

    class Meta:
        verbose_name_plural = 'Sales'

    def __str(self):
        return f'{self.user} ordered by {self.staff.username}'
    
class Producer(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    username = models.CharField(max_length=20, blank=True)
    producer_id = models.CharField(max_length=20, blank=True)
    
    


