from django.http import HttpResponseServerError
from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import requires_csrf_token
from home.models import UsersRegistry
from django.contrib import messages
import pandas as pd

@requires_csrf_token

def home(request):
    return render(request, 'home.html')
    #return HttpResponse("this is home page")

def about(request):
    return render(request, 'about.html')
    #return HttpResponse("this is about page")

def contact(request):
    return render(request, 'contact.html')
    #return HttpResponse("this is contact page")

def login(request):
    return HttpResponse("this is login page")

def register(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        mobileNo = request.POST.get('mobileNo')
        registerUsername = request.POST.get('registerUsername')
        registerPassword = request.POST.get('registerPassword')
        Users_table = UsersRegistry(firstname=firstname, lastname=lastname, email=email, mobileNo=mobileNo, registerUsername=registerUsername, registerPassword=registerPassword)
        Users_table.save()
        messages.success(request, 'User registered successfully! You can go now on sign in page.')
    return render(request, 'register.html')

    #return HttpResponse("this is register page")
    
