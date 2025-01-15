from django.shortcuts import render, redirect
from sklearn.model_selection import train_test_split
from .models import *
from datetime import datetime
from crop_prediction_ml.settings import *

from django.conf import settings
import pandas as pd
from sklearn.linear_model import LogisticRegression
from  sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

import csv
from django.http import HttpResponse, JsonResponse
from django.contrib import messages

# from django.contrib.auth.models import User
# user = User.objects.get(username='admin')
# user.set_password("admin")
# user.save()

def index(request):
    return redirect("predictor")

def predictor(request):
    context = {'static_url': settings.STATIC_URL}
    return render(request, "predictor/predictor.html", context)

def predict_refresh(request):
    df = pd.read_csv(f"{STATIC_ROOT}/cp.csv")
    x = df.drop(columns=['label'], axis=1)
    y = df['label']
    sclr = StandardScaler()
    x_scaled = sclr.fit_transform(x)
    x_train, x_test, y_train, y_test = train_test_split(x_scaled, y, test_size = 0.2, random_state = 42)
    log_reg = LogisticRegression()
    log_reg.fit(x_train, y_train)
    with open(f'{STATIC_ROOT}/crop_prediction_model', 'wb') as f:
        joblib.dump(log_reg, f)
    return JsonResponse({"message": "ML Model Retrained Successfully!"})
    
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