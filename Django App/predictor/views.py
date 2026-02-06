import random
from django.shortcuts import render, redirect
# from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from .models import *
from datetime import datetime
from django.utils import timezone

import pandas as pd
from django.core.mail import send_mail
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import joblib
import os
from django.conf import settings
from django.core.mail import get_connection

from sklearn.metrics import classification_report

import csv
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from predictor import emailService
from .forms import *

def index(request):
    # errorLog = ErrorLogs(error_type="Test error", error_tech_description="No error. Just testing")
    # errorLog.save()
    return redirect("predictor")

def predictor(request):
    # print([settings.EMAIL_HOST, settings.EMAIL_PORT, settings.EMAIL_HOST_USER,
    # settings.EMAIL_HOST_PASSWORD, settings.EMAIL_USE_TLS, settings.EMAIL_USE_SSL])

    # print()

    # print([os.getenv("EMAIL_HOST"),os.getenv("EMAIL_PORT"),
    #        os.getenv("EMAIL_HOST_USER"),os.getenv("EMAIL_HOST_PASSWORD"),
    #        settings.EMAIL_USE_TLS, settings.EMAIL_USE_SSL])
    

    return render(request, "predictor/predictor.html")

def predict_refresh(request):
    df = pd.read_csv(f"{STATIC_ROOT}/cp.csv")
    x = df.drop(columns=['label'])
    y = df['label']

    sclr = StandardScaler()
    columns = x.columns
    x_scaled = sclr.fit_transform(x)

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 42)
    log_reg = LogisticRegression()
    x_train = pd.DataFrame(x_train, columns=columns)
    log_reg.fit(x_train, y_train)
    with open(f'{STATIC_ROOT}/crop_prediction_model.pkl', 'wb') as f:
        joblib.dump(log_reg, f)

    css = """<style>
            table {
                width: 100%;
                border-collapse: collapse;
            }
            table, th, td {
                border: 1px solid black;
            }
            th, td {
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }</style>
        """
    x_scaled = pd.DataFrame(x_scaled, columns=columns)
    
    x_test = pd.DataFrame(x_test, columns=columns)
    
    with open(f"predictor/static/training_dataset.html", "w") as file:
        file.write(css + df.to_html(index=False))

    with open(f"predictor/static/dataset_description.html", "w") as file:
        file.write(css + df.describe().to_html(index=False))

    with open(f"predictor/static/x.html", "w") as file:
        file.write(css + x.to_html(index=False))

    with open(f"predictor/static/x_scaled.html", "w") as file:
        file.write(css + x_scaled.to_html(index=False))

    with open(f"predictor/static/x_train.html", "w") as file:
        file.write(css + x_train.to_html(index=False))

    with open(f"predictor/static/x_test.html", "w") as file:
        file.write(css + x_test.to_html(index=False))

    y_train = pd.DataFrame(y_train)
    with open(f"predictor/static/y_train.html", "w") as file:
        file.write(css + y_train.to_html(index=False))

    y_test = pd.DataFrame(y_test)
    with open(f"predictor/static/y_test.html", "w") as file:
        file.write(css + y_test.to_html(index=False))

    y_pred = log_reg.predict(x_test)
    y_pred = pd.DataFrame(y_pred, columns=["label"])
    with open(f"predictor/static/y_pred.html", "w") as file:
        file.write(css + y_pred.to_html(index=False))

    class_report = classification_report(y_test, y_pred, output_dict=True)
    class_report_df = pd.DataFrame(class_report).transpose()

    with open(f"predictor/static/classification_report.html", "w") as file:
        file.write(css + class_report_df.to_html(index=False))

    messages.success(request, "ML model retrained successfully!")
    return redirect("analytics")
    
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
        
        model = joblib.load(f"{STATIC_ROOT}/crop_prediction_model.pkl")
        input_values = [[N, P, K, temperature, humidity, ph, rainfall]]
        columns = ["N","P","K","temperature","humidity","ph","rainfall"]

        input_df = pd.DataFrame(data=input_values, columns=columns, index=None)
        print(input_df.columns, input_df)
        predict_value = model.predict(input_df)
        # predict_value = "rice"
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

def export_cropdetails_csv(request):
    response = HttpResponse(content_type="text/csv")
    #response["Content-Disposition"] = "attachment; filename='crop_prediction_data.csv'"
    response["Content-Disposition"] = 'attachment; filename="crop_prediction_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['id', 'nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'pH', 'rainfall', 'prediction', 'timestamp'])

    for crop in CropDetails.objects.all():
        writer.writerow([crop.id, crop.n, crop.p, crop.k, crop.temperature, crop.humidity, crop.pH, crop.rainfall, crop.prediction, crop.timestamp])
    
    return response

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
            send_mail(
            subject="OTP from Crop Prediction Platform",
            message=f"Dear user,\n\nYour OTP for password reset is {currentOTP}.\n\nThanks and Regards\nTeam Crop Prediction Platform",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False
            )
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
            # Code to actually login pending
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
        # print(email)
        # print(f"request.user.email", request.user.email)
        # print(f"newPassword: {newPassword}")
        user.set_password(newPassword)
        user.save()
        login(request, user)
        messages.success(request, "Password updated successfully!")
        return redirect("userDashboard")
    else:
        return redirect("loginUser")

def otpValidation(request):
    if request.method == "POST":

        # print("Reached inside otpValidation method")

        try:
            conn = get_connection()
            conn.open()

            firstName = request.POST["firstName"]
            lastName = request.POST["lastName"]
            username = request.POST["username"]
            email = request.POST["email"]
            password = request.POST["password"]
            currentOTP = random.randint(100000, 999999)
            request.session['currentOTP'] = currentOTP       
            
            send_mail(subject="OTP from Crop Prediction Platform",
              message=f"Dear user,\n\nYour OTP is {currentOTP}.\n\nThanks and Regards\nTeam Crop Prediction Platform",
              from_email=settings.EMAIL_HOST_USER,
              recipient_list=[email],
              fail_silently=False
            )
            
            userData = {'firstName':firstName, 'lastName':lastName, 'username':username, 'email':email, 'password':password}
            # print("\n\nUserdata: ", userData)
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
        messages.success(request, "Account created successfully!")
    else:
        messages.error(request, "Access to this URL allowed from Signup form submission only!")
    return redirect("predictor")

def loginUser(request):
    source_url = request.build_absolute_uri()
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
    return render(request, 'predictor/contactUs.html', {'form': form})

def userDashboard(request):
    return render(request, "predictor/userDashboard.html")

def deleteUser(request):
    if request.user.is_authenticated and request.method=="POST":
        user = User.objects.get(email=request.user.email)
        username = user.username
        user.delete()
        messages.success(request, f"Account with username: {username} deleted successfully!")
    return redirect("predictor")