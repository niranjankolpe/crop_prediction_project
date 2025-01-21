import random
from django.shortcuts import render, redirect
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from .models import *
from datetime import datetime

from django.conf import settings
import pandas as pd

from sklearn.linear_model import LogisticRegression
from  sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

from sklearn.metrics import confusion_matrix, classification_report

import csv
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from predictor import emailService
from .forms import *
# from django.contrib.auth.models import User
# user = User.objects.get(username='admin')
# user.set_password("admin")
# user.save()

def index(request):
    return redirect("predictor")

def predictor(request):
    return render(request, "predictor/predictor.html")

def predict_refresh(request):
    df = pd.read_csv(f"{STATIC_ROOT}/cp.csv")
    x = df.drop(columns=['label'], axis=1)
    y = df['label']

    sclr = StandardScaler()
    columns = list(df.columns)
    columns.remove('label')
    x_scaled = sclr.fit_transform(x)
    x_scaled = pd.DataFrame(x_scaled, columns=columns)

    x_train, x_test, y_train, y_test = train_test_split(x_scaled, y, test_size = 0.2, random_state = 42)
    log_reg = LogisticRegression()
    log_reg.fit(x_train, y_train)
    with open(f'{STATIC_ROOT}/crop_prediction_model', 'wb') as f:
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
        
        model = joblib.load(f"{STATIC_ROOT}/crop_prediction_model")

        predict_value = model.predict([[N, P, K, temperature, humidity, ph, rainfall]])
        predict_value = str(predict_value[0])
        
        timestamp = datetime.now()

        if request.FILES.get("photo"):
            photo = request.FILES["photo"]
            photoExtention = os.path.splitext(photo.name)[1]
            new_filename = f"{predict_value}_{timestamp.strftime('%Y%m%d%H%M%S')}{photoExtention}"
            photo.name = new_filename
            entry = CropDetails(n=N, p=P, k=K, temperature=temperature, humidity=humidity, pH=ph, rainfall=rainfall, prediction=predict_value, timestamp=timestamp, photo=photo)
        else:
            entry = CropDetails(n=N, p=P, k=K, temperature=temperature, humidity=humidity, pH=ph, rainfall=rainfall, prediction=predict_value, timestamp=timestamp)
        entry.save()

        data = {'prediction':predict_value, 'static_url': settings.STATIC_URL, 'id':entry.id}

        return render(request, 'predictor/report.html', data)
    
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

def otpValidation(request):
    if request.method == "POST":
        firstName = request.POST["firstName"]
        lastName = request.POST["lastName"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        currentOTP = random.randint(100000, 999999)
        request.session['currentOTP'] = currentOTP
        emailService.sendOTPForValidation(email, currentOTP)
        
        userData = {'firstName':firstName, 'lastName':lastName, 'username':username, 'email':email, 'password':password}
        return render(request, "predictor/otpValidation.html", userData)
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
    return render(request, "predictor/login.html")

def loginSubmit(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        currentUser = authenticate(username=username, password=password)

        if currentUser is not None:
            login(request, currentUser)
            messages.success(request, "Logged in successfully!")
            return redirect("predictor")
        else:
            messages.error(request, "Invalid Credentials!")
            return redirect("login")
    return redirect("predictor")

def logoutUser(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("predictor")

def analytics(request):
    if (not request.user.is_authenticated):
        messages.info(request, "Login to access the Analytics page!")
        return redirect("loginUser")
    return render(request, "predictor/analytics.html")

# def contactUs(request):
#     return render(request, "predictor/contactUs.html")

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