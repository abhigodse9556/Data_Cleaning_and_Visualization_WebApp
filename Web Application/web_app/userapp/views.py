from django.shortcuts import render

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