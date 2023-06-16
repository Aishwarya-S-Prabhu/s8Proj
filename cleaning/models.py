from django.db import models

# Create your models here.
class CSVModel(models.Model):
    csv_file = models.FileField(upload_to='csv_files/')
    # uploaded_at = models.DateTimeField(auto_now_add=True)
    branch = models.CharField(max_length=100)