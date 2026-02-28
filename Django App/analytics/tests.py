from django.test import TestCase

# Create your tests here.
class SimpleTest(TestCase):
    def test_analytics(self):
        response = self.client.get("/analytics/")
        self.assertEqual(response.status_code, 302)