# tests/test_api.py

import unittest
from src.api.app import create_app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
    
    def test_health_check(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'llama-rag-api')
    
    def test_index_status(self):
        response = self.client.get('/index/status')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('index_exists', data)
        self.assertIn('query_engine_loaded', data)
        self.assertIn('files_in_data_directory', data)

if __name__ == '__main__':
    unittest.main()