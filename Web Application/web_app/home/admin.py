from django.contrib import admin
from home.models import UsersRegistry, File, feedback
# Register your models here.

admin.site.register(UsersRegistry)
admin.site.register(File)
admin.site.register(feedback)