import io
from zipfile import ZipFile
from Crypto.PublicKey import DSA
from DSA import DigitalSignatureAlgorithm
from base_test import BaseTestCase

class TestDSA(BaseTestCase):
    def test_dsa_generate_keys(self):
        test_data = {
            'keySize': 2048 
        }
        response = self.client.post('/dsa_generate_keys', json=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/zip')
        with ZipFile(io.BytesIO(response.data), 'r') as zip_file:
            file_list = zip_file.namelist()
            self.assertIn('public_key.pem', file_list)
            self.assertIn('private_key.pem', file_list)

            with zip_file.open('public_key.pem') as public_key_file:
                public_key_content = public_key_file.read()
                public_key = DSA.import_key(public_key_content.decode('utf-8'))
                self.assertFalse(public_key.has_private())

            with zip_file.open('private_key.pem') as private_key_file:
                private_key_content = private_key_file.read()
                private_key = DSA.import_key(private_key_content.decode('utf-8'))
                self.assertTrue(private_key.has_private())
    
    def test_dsa_verify_signature_valid(self):
        text_sign = 'hello'
        dsa_key = DSA.generate(2048)
        private_key = dsa_key.export_key()
        dsa = DigitalSignatureAlgorithm()
        signature = dsa.make_sign(private_key, text_sign.encode('utf-8'))
        public_key = dsa_key.public_key().export_key()
        signature_data = bytes.fromhex(signature)
        expected_result = 1
        result = dsa.check_sign(public_key, text_sign.encode('utf-8'), signature_data)
        self.assertEqual(result, expected_result)

    def test_dsa_verify_signature_invalid(self):
        text_sign = 'hello'
        dsa_key = DSA.generate(2048)
        private_key = dsa_key.export_key()
        public_key = dsa_key.public_key().export_key()
        dsa = DigitalSignatureAlgorithm()
        text_sign_2 = 'hello2'
        signature2 = dsa.make_sign(private_key, text_sign_2.encode('utf-8'))
        signature_data_2 = bytes.fromhex(signature2)
        expected_result = 0
        result = dsa.check_sign(public_key, text_sign.encode('utf-8'), signature_data_2)
        self.assertEqual(result, expected_result)
  



