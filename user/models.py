from distutils.command.upload import upload
from email.mime import image
from email.policy import default

from django.db import models
from django.contrib.auth.models import User



# Create your models here.



class Profile(models.Model):
    staff = models.OneToOneField(User,on_delete=models.CASCADE,null=True)
    address = models.CharField(max_length=200,null=True)
    phone = models.CharField(max_length=20,null=True)
    image = models.ImageField(default='avatar.jpg',upload_to= 'Profile_Images')
    branchID = models.CharField(max_length=20, blank=True)


    def __str__(self):
        return f'{self.staff.username}-Profile'

class ProductRequest(models.Model):
    product_name = models.CharField(max_length=255)
    description = models.TextField()
    requester = models.ForeignKey(User, on_delete=models.CASCADE)
    accepted_by=models.CharField(max_length=100, null=True,blank=True)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return self.product_name


