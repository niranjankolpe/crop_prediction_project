from django.urls import path

from predictor import views

urlpatterns = [
    path('',     views.index, name="index"),
    path('home', views.home,  name="home"),
    path('predictor', views.predictor, name="predictor"),
    path('predict_refresh', views.predict_refresh, name="predict_refresh"),
    path('predict', views.predict, name="predict"),
]
