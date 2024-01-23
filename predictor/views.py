from django.shortcuts import render, redirect

from django.conf import settings
# import pandas as pd
# from sklearn.linear_model import LogisticRegression
# from  sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler
import joblib

def index(request):
    return redirect("predictor")

def predictor(request):
    context = {'media_url': settings.MEDIA_URL}
    return render(request, "predictor/predictor.html", context)

def predict_refresh(request):
    # df = pd.read_csv("media_files/cp.csv")
    # x = df.drop(columns=['label'], axis=1)
    # y = df['label']
    # sclr = StandardScaler()
    # x_scaled = sclr.fit_transform(x)
    # x_train, x_test, y_train, y_test = train_test_split(x_scaled, y, test_size = 0.2, random_state = 42)
    # log_reg = LogisticRegression()
    # log_reg.fit(x_train, y_train)
    # with open('media_files/crop_prediction_model', 'wb') as f:
    #     joblib.dump(log_reg, f)
    return redirect("predictor")
    
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
        
        model = joblib.load("media_files/crop_prediction_model")

        predict_value = model.predict([[N, P, K, temperature, humidity, ph, rainfall]])
        predict_value = str(predict_value[0])


        data = {'prediction':predict_value, 'media_url': settings.MEDIA_URL}

        return render(request, 'predictor/report.html', data)