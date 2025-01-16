from django.db import models
from datetime import datetime

from crop_prediction_ml.settings import *

# Create your models here.
class CropDetails(models.Model):
    id = models.AutoField(primary_key=True)
    n = models.IntegerField()
    p = models.IntegerField()
    k = models.IntegerField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    pH = models.FloatField()
    rainfall = models.FloatField()
    prediction = models.CharField(max_length=20)
    timestamp = models.DateTimeField(default=datetime.now())
    photo = models.ImageField(upload_to=f"{MEDIA_ROOT}/images", default="")   
    
    def __str__(self):
        return str(self.id)