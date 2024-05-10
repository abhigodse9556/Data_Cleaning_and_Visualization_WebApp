from django.db import models

# Create your models here.
class userFiles(models.Model):
    uploaded_file_name = models.CharField(max_length=255)
    uploaded_file = models.FileField(upload_to='files')
    modified_file_name = models.CharField(max_length=255)
    modified_file = models.FileField(upload_to='files')
    uploaded = models.DateTimeField(auto_now_add = True)
    username = models.CharField(max_length=45)
    
    def __str__(self):
        return f"file_id: {self.id}"
