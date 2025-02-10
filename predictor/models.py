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
    photo = models.ImageField(upload_to="images/", default="")   
    
    def __str__(self):
        return str(self.id)
    
class ContactUsTicket(models.Model):
    TICKET_TYPE = [
        (0, 'Complaint'),
        (1, 'Feedback'),
        (2, 'Suggestion')
    ]
    TICKET_STATUS = [
        (1, 'Pending'),
        (2, 'Acknowledged')
    ]

    ticketId = models.AutoField(primary_key=True)
    email = models.CharField(max_length=50)
    ticketType =  models.IntegerField(
        choices=TICKET_TYPE,
        default=0  # Default to 'Complaint' if no choice is made
    )
    description = models.CharField(max_length=200)
    timestamp = models.DateTimeField(default=datetime.now())
    ticketStatus = models.IntegerField(
        choices=TICKET_STATUS,
        default=0
    )

    def __str__(self):
        return str(self.TICKET_STATUS[self.ticketStatus][1])
