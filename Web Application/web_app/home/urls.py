from django.contrib import admin
from django.urls import path
from home import views, utils

urlpatterns = [
    path("", views.home, name="home"),
    path("about", views.about, name="about"),
    path("contact", views.contact, name="contact"),
    path("login", views.home, name="login"),
    path("register", views.register, name="register"),
    path("upload", utils.upload, name="upload"),
    path('download/', utils.download_modified_file, name='download_modified_file'),
]

