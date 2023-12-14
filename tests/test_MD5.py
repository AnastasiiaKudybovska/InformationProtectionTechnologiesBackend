import os
from base_test import BaseTestCase

class TestMD5(BaseTestCase):

    def test_md5_hash(self):
        data = {'s': 'hello'}
        response = self.client.post('/md5_hash', json=data)
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertEqual(result, "5d41402abc4b2a76b9719d911017c592")

    def test_md5_hash_file(self):
        data = 'hello'
        with open('test_file_md5_hash.txt', "w") as file:
            file.write(data)
        with open('test_file_md5_hash.txt', 'rb') as file:
            file_data = file.read()
        data = {'input_file': file_data}
        response = self.client.post('/md5_hash_file', data=data)
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertEqual(result, "5d41402abc4b2a76b9719d911017c592")

    def test_md5_hash_file(self):
        data = 'hello'
        with open('test_file_md5_hash.txt', 'w') as file:
            file.write(data)
        with open('test_file_md5_hash.txt', 'rb') as file:
            response = self.client.post('/md5_hash_file', data={'input_file': (file, 'test_file_md5_hash.txt')})
        self.assertEqual(response.status_code, 200)
        expected_result =  '5d41402abc4b2a76b9719d911017c592'
        self.assertEqual(response.get_json(), expected_result)
       