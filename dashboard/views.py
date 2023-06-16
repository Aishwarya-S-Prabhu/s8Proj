import imp
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Producer, Users

# Create your views here.

#@login_required(login_url='user_login')
@login_required
def index(request):
    producer = None
    print("hello")
    user=request.user
    queryset=Producer.objects.filter(username=user.username)
    print(user)
    if queryset.exists():
    # Do something with the objects in the queryset
        producer=True
    else:
            # The queryset is empty
        producer=False
    context={'producer':producer}
    return render(request,'dashboard/index.html',context=context)

#@login_required(login_url='user_login')
@login_required
def staff(request):
    return render(request,'dashboard/staff.html')
 
#@login_required(login_url='user_login')
@login_required
def users(request):
    return render(request,'dashboard/users.html')

#@login_required(login_url='user_login')
@login_required
def sales(request):
    return render(request,'dashboard/sales.html')

def active_user(request):
    producer = None
    print("hello")

    if request.method == 'GET':
        user=request.user
        queryset=Producer.objects.filter(name=user.username)
        print(user)
        if queryset.exists():
            # Do something with the objects in the queryset
            producer=True
        else:
            # The queryset is empty
            producer=False
        context={'producer':producer}
    return render(request,'dashboard/active_index.html',context=context)



