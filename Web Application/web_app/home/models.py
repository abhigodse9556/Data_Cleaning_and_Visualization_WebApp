from django.db import models

# Create your models here.
class UsersRegistry(models.Model):
    firstname = models.CharField(max_length=20)
    lastname = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    mobileNo = models.CharField(max_length=15)
    registerUsername = models.CharField(max_length=50)
    registerPassword = models.CharField(max_length=20)
    

class File(models.Model):
    file = models.FileField(upload_to="files")
    uploaded = models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        return f"file_id: {self.id}"