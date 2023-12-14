import io
import tempfile
from zipfile import ZipFile
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from RSA import RivestShamirAdleman
from base_test import BaseTestCase

class TestRSA(BaseTestCase):
    def test_rsa_generate_keys(self):
        test_data = {
            'keySize': 2048 
        }
        response = self.client.post('/rsa_generate_keys', json=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/zip')
        with ZipFile(io.BytesIO(response.data), 'r') as zip_file:
            file_list = zip_file.namelist()
            self.assertIn('public_key.pem', file_list)
            self.assertIn('private_key.pem', file_list)

            with zip_file.open('public_key.pem') as public_key_file:
                public_key_content = public_key_file.read()
                public_key = RSA.import_key(public_key_content.decode('utf-8'))
                self.assertFalse(public_key.has_private())

            with zip_file.open('private_key.pem') as private_key_file:
                private_key_content = private_key_file.read()
                private_key = RSA.import_key(private_key_content.decode('utf-8'))
                self.assertTrue(private_key.has_private())
   
    def test_rsa_encrypt_text(self):
        text_to_encrypt = 'hello'
        rsa_key = RSA.generate(2048)
        with open("private_key.pem", "wb") as file:
            file.write(rsa_key.export_key())
        with open("public_key.pem", "wb") as file1:
            file1.write(rsa_key.publickey().export_key())
        with open('public_key.pem', 'rb') as file:  
            response = self.client.post('/rsa_encrypt_text', data={'text_encrypt': text_to_encrypt, 'public_key': (file, 'public_key.pem')})
        self.assertEqual(response.status_code, 200)
        encrypted_text = response.get_json()['encrypted_text']
        with open('private_key.pem', 'rb') as file:  
            response2 = self.client.post('/rsa_decrypt_text', data={'text_decrypt': encrypted_text, 'private_key': (file, 'private_key.pem')})
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.get_json()['decrypted_text'], str(text_to_encrypt))

    def test_rsa_encrypt_file(self):
        rsa_key = RSA.generate(2048)
        private_key = rsa_key.export_key()
        public_key = rsa_key.publickey().export_key()
        data = 'hello'
        with open('test_file_rsa.txt', 'w') as file:
            file.write(data)
        with open('test_file_rsa.txt', 'rb') as file2:
            data_encrypt = file2.read()
        rsa = RivestShamirAdleman()
        encrypted_file_data = rsa.encrypt_file(data_encrypt, public_key)

       

      
    
   
    
