from django.urls import path

from analytics import views

urlpatterns = [
    path('', views.index, name="index"),
    path('predict_refresh', views.predict_refresh, name="predict_refresh"),
    path('export_cropdetails_csv', views.export_cropdetails_csv, name="export_cropdetails_csv"),
]