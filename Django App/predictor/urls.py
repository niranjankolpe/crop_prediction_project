from django.urls import path

from predictor import views

urlpatterns = [
    path('',     views.index, name="index"),
    path('predictor', views.predictor, name="predictor"),
    path('predict', views.predict, name="predict"),
    path('donate', views.donate, name="donate"),
    path('donateSubmit', views.donateSubmit, name="donateSubmit"),
    path('signup', views.signup, name="signup"),
    path('signupSubmit', views.signupSubmit, name="signupSubmit"),
    path('loginUser', views.loginUser, name="loginUser"),
    path('loginSubmit', views.loginSubmit, name="loginSubmit"),
    path('logoutUser', views.logoutUser, name="logoutUser"),
    path('resetPassword', views.resetPassword, name="resetPassword"),
    path('resetPasswordForm', views.resetPasswordForm, name="resetPasswordForm"),
    path('resetPasswordConfirm', views.resetPasswordConfirm, name="resetPasswordConfirm"),

    path('deleteUser', views.deleteUser, name="deleteUser"),
    
    path('otpValidation', views.otpValidation, name="otpValidation"),
    path('contactUs', views.contactUs, name="contactUs"),
    path('aboutUs', views.aboutUs, name="aboutUs"),
    path('userDashboard', views.userDashboard, name="userDashboard")
]
