# app/tests.py
from django.test import TestCase

class SimpleTest(TestCase):
    def test_home_status(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302) # Response Code 302 == Redirect
    
    def test_prediction_home(self):
        response = self.client.get("/predictor")
        self.assertEqual(response.status_code, 200) # Respomse Code 200 == Success
