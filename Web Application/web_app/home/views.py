from django.http import HttpResponseServerError
from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import requires_csrf_token
from home.models import UsersRegistry, feedback
import pandas as pd

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UsersRegistry
@requires_csrf_token

def home(request):
    return render(request, 'home.html')
    #return HttpResponse("this is home page")

def about(request):
    return render(request, 'about.html')
    #return HttpResponse("this is about page")

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('sender_name')
        email = request.POST.get('sender_email')
        mobile = request.POST.get('sender_mobile')
        msg = request.POST.get('message')
        Users_table = feedback(name=name, email=email, mobile=mobile, message=msg)
        Users_table.save()
        messages.success(request, 'Message sent successfully!')
    return render(request, 'contact.html')
    #return HttpResponse("this is contact page")

def upload(request):
    return render(request, 'upload.html')
    #return HttpResponse("this is contact page")

def feature(request):
    return render(request, 'feature.html')
    #return HttpResponse("this is contact page")

# def automatic(request):
    
#     return render(request, 'automatic.html')
#     #return HttpResponse("this is contact page")


def login(request):
    if request.method == 'POST':
        registered_username = request.POST.get('registeredUsername')
        password = request.POST.get('registeredPassword')
        
        try:
            user = UsersRegistry.objects.get(registerUsername=registered_username)
        except UsersRegistry.DoesNotExist:
            user = None
        
        if user is not None and user.registerPassword == password:
            # If the username and password match, set session variables
            request.session['user_id'] = user.id
            request.session['username'] = user.registerUsername
            username = request.session.get('username')
            return render(request, 'userdashboard.html', {'username': username})  # Redirect to home page after successful login
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')


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
    
