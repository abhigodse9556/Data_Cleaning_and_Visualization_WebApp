from django.urls import path
from . import views, utils, duplicate, null, outlier

urlpatterns = [
    path('upload_user_file', views.upload_user_file, name='upload_user_file'),
    path('', views.automatic_for_user, name='automatic_for_user'),
    path('duplicate_for_user', views.duplicate_for_user, name='duplicate_for_user'),
    path('null_for_user', views.null_for_user, name='null_for_user'),
    path('outlier_for_user', views.outlier_for_user, name='outlier_for_user'),
    path('displayUserProfile', views.displayUserProfile, name='displayUserProfile'),
    path('updateUserProfile', views.updateUserProfile, name='updateUserProfile'),
    path('displayPreviousWork', views.displayPreviousWork, name='displayPreviousWork'),
    path('view_file', views.view_file, name='view_file'),
    path('uploaduserfile', utils.uploaduserfile, name='uploaduserfile'),
    path('download_modified_userfile', utils.download_modified_userfile, name='download_modified_userfile'),
    path('removeduplicatesforuser', duplicate.removeduplicatesforuser, name='removeduplicatesforuser'),
    path('download_modified_userfile', duplicate.download_modified_userfile, name='download_modified_userfile'),
    path('removenullforuser', null.removenullforuser, name='removenullforuser'),
    path('download_modified_userfile', null.download_modified_userfile, name='download_modified_userfile'),
    path('removeoutlierforuser', outlier.removeoutlierforuser, name='removeoutlierforuser'),
    path('download_modified_userfile', outlier.download_modified_userfile, name='download_modified_userfile'),
]
