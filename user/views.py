
import imp
from multiprocessing import context
from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm , UserUpdateForm, ProfileUpdateForm
from .models import ProductRequest
from .forms import ProductRequestForm
from django.urls import path
from . import views


# Create your views here.



def register(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_login')
    else:
        form = CreateUserForm()
    context = {
        'form':form,

    }
    return render(request,'user/register.html',context)

def profile(request):
    return render(request,'user/profile.html')

def profile_update(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('user-profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm( instance=request.user.profile)
    context = {
        'user_form':user_form,
        'profile_form': profile_form,
    }
    return render(request,'user/profile_update.html', context)


def product_request(request):
    if request.method == 'POST':
        form = ProductRequestForm(request.POST)
        if form.is_valid():
            product_request = form.save(commit=False)
            product_request.requester = request.user
            product_request.save()
            return redirect('product_notice_board')
    else:
        form = ProductRequestForm()
    return render(request, 'user/product_request.html', {'form': form})

def product_notice_board(request):
    product_requests = ProductRequest.objects.all()
    return render(request, 'user/product_notice_board.html', {'product_requests': product_requests})

def accept_product_request(request, product_request_id):
    product_request = ProductRequest.objects.get(id=product_request_id)
    product_request.is_accepted = True
    user = request.user
    product_request.accepted_by= user.username
    product_request.save()
    return redirect('product_notice_board')