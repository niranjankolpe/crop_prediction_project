# app/tests.py
from django.test import TestCase

class SimpleTest(TestCase):
    def test_home_status(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302) # Response Code 302 == Redirect
    
    def test_prediction_home(self):
        response = self.client.get("/predictor")
        self.assertEqual(response.status_code, 200) # Respomse Code 200 == Success
    
    def test_contactUs(self):
        response = self.client.get("/contactUs")
        self.assertEqual(response.status_code, 200)

    def test_donate(self):
        response = self.client.get("/donate")
        self.assertEqual(response.status_code, 200)
    
    def test_signup(self):
        response = self.client.get("/signup")
        self.assertEqual(response.status_code, 200)
    
    def test_loginUser(self):
        response = self.client.get("/loginUser")
        self.assertEqual(response.status_code, 200)
    
    def test_userDashboard(self):
        response = self.client.get("/userDashboard")
        self.assertEqual(response.status_code, 200)
    
    def test_resetPassword(self):
        response = self.client.get("/resetPassword")
        self.assertEqual(response.status_code, 200)

    def test_aboutUs(self):
        response = self.client.get("/aboutUs")
        self.assertEqual(response.status_code, 200)
    
    def test_otpValidation(self):
        response = self.client.get("/otpValidation")
        self.assertEqual(response.status_code, 200)
    
    def test_logoutUser(self):
        response = self.client.get("/logoutUser")
        self.assertEqual(response.status_code, 200)