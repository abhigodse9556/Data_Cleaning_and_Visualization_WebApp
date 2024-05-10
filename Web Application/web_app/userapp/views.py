import base64
import os
from django.conf import settings
from django.shortcuts import render, redirect
from home.models import UsersRegistry
from userapp.models import userFiles

# Create your views here.
def upload_user_file(request):
    username = request.GET.get('username')
    return render(request, 'upload_user_file.html', {'username': username})

def automatic_for_user(request):
    username = request.GET.get('username')
    return render(request, 'automatic_for_user.html', {'username': username})

def duplicate_for_user(request):
    username = request.GET.get('username')
    return render(request, 'duplicate_for_user.html', {'username': username})

def null_for_user(request):
    username = request.GET.get('username')
    return render(request, 'null_for_user.html', {'username': username})

def outlier_for_user(request):
    username = request.GET.get('username')
    return render(request, 'outlier_for_user.html', {'username': username})

def displayUserProfile(request):
    username = request.GET.get('username')
    user_profile = UsersRegistry.objects.get(registerUsername=username)
    return render(request, 'display_user_profile.html', {'username': username, 'user_profile': user_profile})

def displayPreviousWork(request):
    username = request.GET.get('username')
    user_work = userFiles.objects.filter(username=username).values('id', 'uploaded_file_name', 'modified_file_name', 'uploaded')
    return render(request, 'display_previous_work.html', {'username': username, 'user_work': user_work})

def updateUserProfile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user_profile = UsersRegistry.objects.get(registerUsername=username)  # Fetch user profile from database
        
        # Update user profile with form data
        user_profile.firstname = request.POST.get('firstname')
        user_profile.lastname = request.POST.get('lastname')
        user_profile.email = request.POST.get('email')
        user_profile.mobileNo = request.POST.get('mobileNo')
        
        # Save the updated profile to the database
        user_profile.save()
        
        user_profile = UsersRegistry.objects.get(registerUsername=username)
        return render(request, 'display_user_profile.html', {'username': username, 'user_profile': user_profile, 'updateStatus': "Profile updated successfully!"})
    else:
        user_profile = UsersRegistry.objects.get(registerUsername=username)
        return render(request, 'display_user_profile.html', {'username': username, 'user_profile': user_profile, 'updateStatus': "Something went wrong! Please try again..."})

def view_file(request):
    files = userFiles.objects.all()

    for file_record in files:
        # Decode uploaded file content
        uploaded_file_content = base64.b64decode(file_record.uploaded_file)

        # Decode modified file content
        modified_file_content = base64.b64decode(file_record.modified_file)

        # Update file record with decoded content
        file_record.uploaded_file = uploaded_file_content.decode('utf-8')
        file_record.modified_file = modified_file_content.decode('utf-8')

    return render(request, 'view_file.html', {'files': files})