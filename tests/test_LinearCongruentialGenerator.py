import os
from base_test import BaseTestCase

class TestLinearCongruentialGenerator(BaseTestCase):
    def test_generate_pseudo_random_sequence(self):
        response = self.client.post('/generate_pseudo_random_sequence', json={'n': 10})
        self.assertEqual(response.status_code, 200)
        rand_numbers = [7377, 7377377, 3791824, 174013, 6241237, 113769, 4717486, 3089243, 2236001, 4631915]
        response_numbers = response.json
        self.assertSetEqual(set(rand_numbers), set(response_numbers))

    def test_get_period_of_generate_pseudo_random_sequence_without_period(self):
        response = self.client.post('/generate_pseudo_random_sequence', json={'n': 20})
        response = self.client.get('/get_period_of_generated_pseudo_random_sequence')
        self.assertEqual(response.status_code, 200)
        self.assertIn('period', response.json)
        expected_period = -1
        actual_period = response.json['period']
        self.assertEqual(actual_period, expected_period)

    def test_get_period_of_generate_pseudo_random_sequence_with_period(self):
        response = self.client.post('/generate_pseudo_random_sequence', json={'n': 44700})
        response = self.client.get('/get_period_of_generated_pseudo_random_sequence')
        self.assertEqual(response.status_code, 200)
        self.assertIn('period', response.json)
        expected_period = 44620
        actual_period = response.json['period']
        self.assertEqual(actual_period, expected_period)

    def test_write_to_file_generated_pseudo_random_sequence(self):
        response = self.client.get('/write_to_file_generated_pseudo_random_sequence')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(os.path.exists('linear_congruential_generated_sequence.txt'))
