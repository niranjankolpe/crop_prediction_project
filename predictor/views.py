import random
from django.shortcuts import render, redirect

import pandas as pd
import joblib
import os
from django.conf import settings

import csv
from datetime import datetime
from django.utils import timezone

from predictor.models import ActivityLogs, CropDetails

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from predictor import emailService
from predictor.forms import ContactUsTicketForm

def index(request):
    return redirect("predictor")

def predictor(request):
    return render(request, "predictor/predictor.html")

def predict(request):
    if request.method != 'POST':
        return redirect("predictor")

    if request.method == 'POST':
        predict_value = ""

        N = int(request.POST['N'])
        P = int(request.POST['P'])
        K = int(request.POST['K'])
        temperature = float(request.POST['temperature'])
        humidity = float(request.POST['humidity'])
        ph = float(request.POST['ph'])
        rainfall = float(request.POST['rainfall'])
        
        model = joblib.load(f"{settings.STATIC_ROOT}/crop_prediction_model.pkl")
        input_values = [[N, P, K, temperature, humidity, ph, rainfall]]
        columns = ["N","P","K","temperature","humidity","ph","rainfall"]

        input_df = pd.DataFrame(data=input_values, columns=columns, index=None)
        predict_value = model.predict(input_df)
        predict_value = str(predict_value[0])
        
        timestamp = datetime.now()

        if request.FILES.get("photo"):
            photo = request.FILES["photo"]
            photoExtention = os.path.splitext(photo.name)[1]
            new_filename = f"{predict_value}_{timestamp.strftime('%Y%m%d%H%M%S')}{photoExtention}"
            photo.name = new_filename
            entry = CropDetails(n=N, p=P, k=K, temperature=temperature, humidity=humidity, pH=ph, rainfall=rainfall, prediction=predict_value, timestamp=timezone.now(), photo=photo)
        else:
            entry = CropDetails(n=N, p=P, k=K, temperature=temperature, humidity=humidity, pH=ph, rainfall=rainfall, prediction=predict_value, timestamp=timezone.now())
        entry.save()

        updateCropDetailsCSV()

        data = {'prediction':predict_value, 'static_url': settings.STATIC_URL, 'id':entry.id}
        return render(request, 'predictor/report.html', data)

def updateCropDetailsCSV():
    records = CropDetails.objects.all()
    file_path = os.path.join(settings.MEDIA_ROOT, 'docs/csv/crop_prediction_data.csv')
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'pH', 'rainfall', 'prediction', 'timestamp'])
        for crop in records:
            writer.writerow([crop.id, crop.n, crop.p, crop.k, crop.temperature, crop.humidity, crop.pH, crop.rainfall, crop.prediction, crop.timestamp])
    return

def donate(request):
    return render(request, "predictor/donate.html")

def donateSubmit(request):
    messages.success(request, "Your payment was successful!")
    return render(request, "predictor/donateSubmit.html")

def signup(request):
    return render(request, "predictor/signup.html")

def resetPassword(request):
    if request.user.is_authenticated:
        return redirect("resetPasswordForm")
    send_otp_readonly = False
    show_otp = False
    confirm_new_password = False
    
    vars = dict()
    vars.update({'send_otp_readonly': send_otp_readonly,
                 'show_otp': show_otp,
                 'confirm_new_password': confirm_new_password})

    if request.method == "POST" and "send_otp" in request.POST:
        email = request.POST["email"]
        exists = User.objects.filter(email=email).exists()
        if not exists:
            messages.warning(request, f"No email address as: {email} registered with us!")
            return redirect("resetPassword")
        currentOTP = random.randint(100000, 999999)
        request.session['currentOTP'] = currentOTP
        
        try:
            email_purpose = "password reset"
            emailService.sendOTPForValidation(email, email_purpose, currentOTP)
        except Exception as e:
            messages.warning(f"Exception occured: {e}")
            return redirect("predictor")
        send_otp_readonly = True
        show_otp = True
        confirm_new_password = False
        vars.update({'send_otp_readonly': send_otp_readonly,
                 'show_otp': show_otp,
                 'confirm_new_password': confirm_new_password,
                 'email': email})
    elif request.method == "POST" and "verify_otp" in request.POST:
        currentOTP = str(request.session.get('currentOTP'))
        email = request.POST["email"]

        if request.POST["otp"] == currentOTP:
            messages.success(request, "Logged in successfully!")
            messages.info(request, "You may reset your password now!")
            user = User.objects.get(email=email)
            login(request, user)
            return redirect("resetPasswordForm")
        else:
            send_otp_readonly = True
            show_otp = True
            confirm_new_password = False
            vars.update({'send_otp_readonly': send_otp_readonly,
                    'show_otp': show_otp,
                    'confirm_new_password': confirm_new_password,
                    'email': email})
            messages.warning(request, "Invalid OTP! Try again.")
            return render(request, "predictor/resetPassword.html", vars)
    return render(request, "predictor/resetPassword.html", vars)

def resetPasswordForm(request):
    if request.user.is_authenticated:
        return render(request, "predictor/resetPasswordForm.html", {'email': request.user.email})
    else:
        return redirect("loginUser")

def resetPasswordConfirm(request):
    if request.method == "POST":
        email = request.POST["email"]
        user = User.objects.get(email=email)

        newPassword = request.POST["newPassword"]
        user.set_password(newPassword)
        user.save()
        login(request, user)
        messages.success(request, "Password updated successfully!")
        return redirect("userDashboard")
    else:
        return redirect("loginUser")

def otpValidation(request):
    if request.method == "POST":
        try:
            firstName = request.POST["firstName"]
            lastName = request.POST["lastName"]
            username = request.POST["username"]
            email = request.POST["email"]
            password = request.POST["password"]
            currentOTP = random.randint(100000, 999999)
            request.session['currentOTP'] = currentOTP

            email_purpose = "New Account Creation"
            emailService.sendOTPForValidation(email, email_purpose, currentOTP)
                        
            userData = {'firstName':firstName, 'lastName':lastName, 'username':username, 'email':email, 'password':password}
            return render(request, "predictor/otpValidation.html", userData)
        except Exception as e:
            print(e)
            messages.warning(request, e)
            return redirect("predictor")
    else:
        messages.error(request, "Access to this URL allowed from Signup form submission only!")
        return redirect("signup")

def signupSubmit(request):
    currentOTP = str(request.session.get('currentOTP'))
    if request.method == "POST":
        firstName = request.POST["firstName"]
        lastName = request.POST["lastName"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        otp = request.POST["otp"]
        userData = {'firstName':firstName, 'lastName':lastName, 'username':username, 'email':email, 'password':password}
        if (otp == currentOTP):
            pass
        else:
            messages.error(request, f"Invalid OTP! Please reenter correct OTP.")
            return render(request, "predictor/otpValidation.html", userData)
        newUser = User.objects.create_user(username=username, email=email, password=password)
        newUser.first_name = firstName
        newUser.last_name = lastName
        newUser.save()
        messages.success(request, "Account created successfully! Please login.")
        return redirect("loginUser")
    else:
        messages.error(request, "Access to this URL allowed from Signup form submission only!")
    return redirect("predictor")

def loginUser(request):
    source_url = request.build_absolute_uri()
    if request.user.is_authenticated:
        return redirect("userDashboard")
    activity_type = "Initiated view - loginUser"
    activity = ActivityLogs(source_url=source_url, activity_type=activity_type, timestamp=timezone.now())
    activity.save()
    return render(request, "predictor/login.html")

def loginSubmit(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        # print(username, password)
        currentUser = authenticate(username=username, password=password)
        # print(currentUser)

        if currentUser is not None:
            login(request, currentUser)
            messages.success(request, "Logged in successfully!")
            return redirect("userDashboard")
        else:
            messages.error(request, "Invalid Credentials!")
            return redirect("loginUser")
    return redirect("predictor")

def logoutUser(request):
    try:
        logout(request)
        messages.success(request, "Logged out successfully!")
    except Exception as e:
        messages.error(request, "Failed to logout!")
    return redirect("predictor")

def aboutUs(request):
    return render(request, "predictor/aboutUs.html")

def contactUs(request):
    if request.method == 'POST':
        form = ContactUsTicketForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ticket submitted successfully!")
            return redirect('predictor')
    else:
        form = ContactUsTicketForm()
    return render(request, 'predictor/contactUs.html', {'form': form, 'admin_email_address':settings.EMAIL_HOST_USER})

def userDashboard(request):
    return render(request, "predictor/userDashboard.html")

def deleteUser(request):
    if request.user.is_authenticated and request.method=="POST":
        user = User.objects.get(email=request.user.email)
        username = user.username
        user.delete()
        messages.success(request, f"Account with username: {username} deleted successfully!")
    return redirect("predictor")