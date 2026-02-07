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

    def test_analytics(self):
        response = self.client.get("/analytics")
        self.assertEqual(response.status_code, 302)
    
    def test_signup(self):
        response = self.client.get("/signup")
        self.assertEqual(response.status_code, 200)