from django.test import TestCase, Client
from django.urls import reverse

class RenderDeploymentTest(TestCase):
    """
    Test to verify that your Django app is working correctly on Render.
    Run with: python manage.py test
    """
    
    def setUp(self):
        self.client = Client()
    
    def test_home_endpoint(self):
        """Test that the home endpoint returns 'Render works!'"""
        response = self.client.get('/home')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Render works!")
    
    def test_admin_page_accessible(self):
        """Test that admin page is accessible"""
        response = self.client.get('/admin/')
        # Should redirect to login or show admin
        self.assertIn(response.status_code, [200, 302])
    
    def test_api_gestion_endpoint(self):
        """Test that gestion API endpoints are accessible"""
        response = self.client.get('/api/')
        # Should return 200 or 404 (not 500 error)
        self.assertIn(response.status_code, [200, 404])
