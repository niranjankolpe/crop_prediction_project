from django.urls import path

from predictor import views

urlpatterns = [
    path('',     views.index, name="index"),
    path('predictor', views.predictor, name="predictor"),
    path('predict_refresh', views.predict_refresh, name="predict_refresh"),
    path('predict', views.predict, name="predict"),
    path('export_cropdetails_csv', views.export_cropdetails_csv, name="export_cropdetails_csv"),
    path('donate', views.donate, name="donate"),
    path('donateSubmit', views.donateSubmit, name="donateSubmit")
]
