from django.contrib import admin
from django.urls import path
from home import views, utils, null, outlier, duplicate

urlpatterns = [
    path("", views.home, name="home"),
    path("about", views.about, name="about"),
    path("contact", views.contact, name="contact"),
    path("login", views.login, name="login"),
    path("register", views.register, name="register"),
    path("upload", views.upload, name="upload"),
    path("feature", views.feature, name="feature"),
    path("index", views.index, name="index"),
    path("automatic", utils.upload, name="automatic"),
    path('download/', utils.download_modified_file, name='download_modified_file'),
    path('null/', null.upload, name='null'),
    path('download/', null.download_modified_file, name='download_modified_file'),
    path('outlier/', outlier.upload, name='outlier'),
    path('download/', outlier.download_modified_file, name='download_modified_file'),
    path('duplicate/', duplicate.upload, name='duplicate'),
    path('download/', duplicate.download_modified_file, name='download_modified_file'),
    path('upload_file', views.upload_file, name='upload_file'),
]

