import os
import unittest
from flask import Flask
from routes import app_blueprint

class TestApp(unittest.TestCase):
    def setUp(self):
        self.test_app = Flask(__name__)
        self.test_app.register_blueprint(app_blueprint)
        self.client = self.test_app.test_client()

    def tearDown(self):
        """Cleanup any files created during testing."""
        # if os.path.exists('linear_congruential_generated_sequence.txt'):
        #     os.remove('linear_congruential_generated_sequence.txt')

            

    def test_generate_pseudo_random_sequence(self):
        response = self.client.post('/generate_pseudo_random_sequence', json={'n': 10})
        self.assertEqual(response.status_code, 200)
        rand_numbers = [7377, 7377377, 3791824, 174013, 6241237, 113769, 4717486, 3089243, 2236001, 4631915]
        self.assertSetEqual(set(rand_numbers), set(response.json))
    

    def test_get_period_of_generate_pseudo_random_sequence(self):
        response = self.client.get('/get_period_of_generated_pseudo_random_sequence')
        self.assertEqual(response.status_code, 200)
        self.assertIn('period', response.json)

    def test_write_to_file_generated_pseudo_random_sequence(self):
        response = self.client.get('/write_to_file_generated_pseudo_random_sequence')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(os.path.exists('linear_congruential_generated_sequence.txt'))


if __name__ == '__main__':
    unittest.main()
