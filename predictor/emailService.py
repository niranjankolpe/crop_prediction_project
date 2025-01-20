from django.conf.global_settings import *
from django.core.mail import send_mail

def sendOTPForValidation(recipientEmailAddress, currentOTP):
    send_mail(subject="OTP from Crop Prediction Platform",
              message=f"Dear user,\n\nYour OTP is {currentOTP}.\n\nThanks and Regards\nTeam Crop Prediction Platform",
              from_email=EMAIL_HOST_USER, recipient_list=[recipientEmailAddress], fail_silently=False)