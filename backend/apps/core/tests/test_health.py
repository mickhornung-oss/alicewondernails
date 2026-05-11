from django.test import Client, SimpleTestCase
import json


class HealthCheckTest(SimpleTestCase):
    """Health check endpoint tests. No database required."""
    
    def test_health_endpoint_returns_ok(self):
        """Test: Health endpoint returns 200 OK."""
        client = Client()
        response = client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'status': 'ok',
            'service': 'alice-wonder-nails-backend',
        })
    
    def test_health_response_format_is_valid_json(self):
        """Test: Health response is valid JSON with required fields."""
        client = Client()
        response = client.get('/api/health/')
        
        # Verify response is valid JSON
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        
        # Verify required fields exist
        self.assertIn('status', data)
        self.assertIn('service', data)
        
        # Verify field values
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['service'], 'alice-wonder-nails-backend')
    
    def test_health_endpoint_no_database_required(self):
        """Test: Health endpoint works without database (SimpleTestCase = no DB)."""
        # SimpleTestCase does not set up a database.
        # If this test passes, health endpoint has no database dependency.
        client = Client()
        response = client.get('/api/health/')
        
        # Should succeed even without database
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json())
