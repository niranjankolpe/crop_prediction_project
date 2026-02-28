import io
import os
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib import messages

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import plotly.express as px
import base64



def index(request):
    if (not request.user.is_authenticated):
        messages.info(request, "Login to access the Analytics page!")
        return redirect("loginUser")
    plots = plot_view()
    return render(request, "analytics/analytics.html", plots)

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