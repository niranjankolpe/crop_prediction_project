# from django.conf.global_settings import *
from django.conf import settings
from django.core.mail import send_mail

import os

def sendOTPForValidation(recipientEmailAddress, currentOTP):
    # print("\nInside sendOTPForValidation method of emailService")
    # print(currentOTP, "\n", settings.EMAIL_HOST, "\n", settings.EMAIL_PORT, "\n", settings.EMAIL_HOST_USER, "\n", settings.EMAIL_HOST_PASSWORD, "\n", settings.EMAIL_USE_TLS, "\n", settings.EMAIL_USE_SSL, "\n", recipientEmailAddress)
    # print(currentOTP, "\n", os.getenv("DJANGO_EMAIL_HOST_USER"), "\n", recipientEmailAddress)
    send_mail(subject="OTP from Crop Prediction Platform",
              message=f"Dear user,\n\nYour OTP is {currentOTP}.\n\nThanks and Regards\nTeam Crop Prediction Platform",
              from_email=settings.EMAIL_HOST_USER,
              recipient_list=[recipientEmailAddress],
              fail_silently=False)
    # print("Email Sent Successfully")
    # print("sendOTPForValidation completed!")