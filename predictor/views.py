import random
from django.shortcuts import render, redirect
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from .models import *
from datetime import datetime
from django.utils import timezone
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

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import urllib, base64

import plotly.express as px

def index(request):
    return redirect("predictor")

def predictor(request):
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
    plots = plot_view()
    return render(request, "predictor/analytics.html", plots)

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

def matplotlib_chart(x, y):
    # Create a line plot
    plt.figure(figsize=(20,10))
    plt.plot(x, y)
    plt.title("Crop Predictions Data")
    plt.xlabel("Predictions")
    plt.xticks(rotation=10)
    plt.ylabel("Count")
    
    # Save the plot to a BytesIO object
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    # Encode the image to base64 for embedding in HTML
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()
    return image_base64

def plotly_chart(x, y):    
    fig = px.bar(x=x, y=y, title="Sample Bar Chart")

    # Customize the layout to add some visual appeal
    fig.update_layout(
        title="Categorical Value Count in Prediction",
        title_x=0.5,  # Center title
        title_font=dict(size=22, color='purple', family="Helvetica"),
        plot_bgcolor="white",  # Clean white background for the plot
        paper_bgcolor="lightgray",  # Slightly different background for the paper area
        xaxis=dict(
            title="Prediction Type",  # X-axis title
            title_font=dict(size=18, color='blue'),
            tickangle=45,  # Angle the x-axis labels for better visibility
            tickfont=dict(size=14, color='green'),
            showgrid=True,  # Show grid lines
            gridcolor="lightgray"  # Light grid color for subtle appearance
        ),
        yaxis=dict(
            title="Count of Predictions",
            title_font=dict(size=18, color='blue'),
            tickfont=dict(size=14, color='green'),
            showgrid=True,  # Show grid lines on the y-axis
            gridcolor="lightgray"  # Light grid lines for consistency
        ),
        bargap=0.15,  # Slightly reduce the gap between bars for a compact view
        showlegend=False  # Disable the legend since it's not needed here
    )

    # Apply an alternating color pattern to the bars (different for each prediction)
    fig.update_traces(marker=dict(color='rgba(255, 99, 132, 0.6)', line=dict(color='rgba(255, 99, 132, 1)', width=1)))

    # Add hover effects: Hover labels show more detailed information
    fig.update_traces(
        hoverinfo='x+y',  # Display x and y values on hover
        hoverlabel=dict(bgcolor='rgba(255, 255, 255, 0.7)', font_size=14, font_family='Arial')
    )
    graph_html = fig.to_html(full_html=False)
    return graph_html

def plot_view():
    # Example data
    df = pd.read_csv(os.path.join(settings.MEDIA_ROOT, 'docs/csv/crop_prediction_data.csv'))
    x = df['prediction'].unique()
    y = df['prediction'].value_counts()
    image_base64 = matplotlib_chart(x, y)
    graph_html = plotly_chart(x, y)
    #print(y, type(y), list(y))
    plots = {'x':list(x), 'y':list(y), 'image_base64': image_base64, 'graph_html': graph_html}
    return plots

def userDashboard(request):
    return render(request, "predictor/userDashboard.html")