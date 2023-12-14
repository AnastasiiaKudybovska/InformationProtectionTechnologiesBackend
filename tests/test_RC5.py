from base_test import BaseTestCase

class TestRC5(BaseTestCase):
    def test_rc5(self):
        text_to_encrypt = 'hello'
        test_data_encryption = {
            'key': '111',
            'text': text_to_encrypt
        }
        response = self.client.post('/rc5_encode_text', json=test_data_encryption)
        self.assertEqual(response.status_code, 200)
        encrypted_text = response.get_json()['encrypted_text']
        test_data_decryption = {
            'key': '111',
            'text': encrypted_text
        }
        response2 = self.client.post('/rc5_decode_text', json=test_data_decryption)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.get_json()['decrypted_text'], str(text_to_encrypt.encode("utf-8")))




    