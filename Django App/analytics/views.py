import io
import os
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages

import pandas as pd
import matplotlib
from sklearn.discriminant_analysis import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import plotly.express as px
import base64
import joblib
import csv

from predictor.models import CropDetails

from django.core.paginator import Paginator

def index(request):
    if (not request.user.is_authenticated):
        messages.info(request, "Login to access the Analytics page!")
        return redirect("loginUser")
    
    df = pd.read_csv(f"{settings.STATIC_ROOT}/cp.csv")
    df.index = df.index + 1
    df.index.name = "ID"
    df = df.reset_index()

    columns = df.columns.tolist()
    rows = df.values.tolist()
    paginator = Paginator(rows, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'columns': columns}

    plots = plot_view()
    context.update(plots)
    return render(request, "analytics/analytics.html", context)

def predict_refresh(request):
    df = pd.read_csv(f"{settings.STATIC_ROOT}/cp.csv")
    x = df.drop(columns=['label'])
    y = df['label']

    sclr = StandardScaler()
    columns = x.columns
    x_scaled = sclr.fit_transform(x)

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 42)
    log_reg = LogisticRegression()
    x_train = pd.DataFrame(x_train, columns=columns)
    log_reg.fit(x_train, y_train)
    with open(f'{settings.STATIC_ROOT}/crop_prediction_model.pkl', 'wb') as f:
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
    
    # To be deleted
    # with open(f"predictor/static/training_dataset.html", "w") as file:
    #     file.write(css + df.to_html(index=False))

    with open(f"predictor/static/dataset_description.html", "w") as file:
        file.write(css + df.describe().to_html(index=False))

    with open(f"predictor/static/x.html", "w") as file:
        file.write(css + x.to_html(index=False))

    with open(f"predictor/static/x_scaled.html", "w") as file:
        file.write(css + x_scaled.to_html(index=False))
    
    with open(f"predictor/static/y.html", "w") as file:
        file.write(css + y.to_frame().to_html(index=False))

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
    return redirect("/analytics")

def export_cropdetails_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="crop_prediction_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['id', 'nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'pH', 'rainfall', 'prediction', 'timestamp'])

    for crop in CropDetails.objects.all():
        writer.writerow([crop.id, crop.n, crop.p, crop.k, crop.temperature, crop.humidity, crop.pH, crop.rainfall, crop.prediction, crop.timestamp])
    return response

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