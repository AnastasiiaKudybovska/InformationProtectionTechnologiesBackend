import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

class RivestShamirAdleman:
    def __init__(self, key_size=1024, private_key=None, public_key=None):
        self.private_key = private_key
        self.public_key = public_key
        self.key_size = key_size
        self.time = None
        
    def generate_keys(self):
        key = RSA.generate(self.key_size)
        self.private_key = key.export_key()
        self.public_key = key.publickey().export_key()
        return self.private_key, self.public_key

    def encrypt_text(self, plaintext, public_key):
        self.public_key = RSA.import_key(public_key)
        cipher_rsa = PKCS1_v1_5.new(self.public_key)
        encrypted_message = cipher_rsa.encrypt(plaintext.encode())
        encrypted_message_base64 = base64.b64encode(encrypted_message).decode('utf-8')
        return encrypted_message_base64
    
    def decrypt_text(self, ciphertext, private_key):
        self.private_key = RSA.import_key(private_key)
        cipher_rsa = PKCS1_v1_5.new(self.private_key)
        ciphertext = base64.b64decode(ciphertext)
        decrypted_message = cipher_rsa.decrypt(ciphertext, sentinel='4ert').decode()
        return decrypted_message
    
    def encrypt_file(self, input_file_data, public_key):
        self.public_key = RSA.import_key(public_key)
        cipher_rsa = PKCS1_v1_5.new(self.public_key)
        res = []
        i = 0
        block_size = self.public_key.size_in_bytes() - 11
        while True:
            block = input_file_data[i * block_size:(i + 1) * block_size]
            if not block:
                break
            i += 1
            res += cipher_rsa.encrypt(block)
        return bytes(res)
    
    def decrypt_file(self, input_file_data, private_key):
        self.private_key = RSA.import_key(private_key)
        cipher_rsa = PKCS1_v1_5.new(self.private_key)
        res = []
        i = 0
        block_size = self.private_key.size_in_bytes()
        while True:
            block = input_file_data[i * block_size:(i + 1) * block_size]
            if not block:
                break
            i += 1
            res += cipher_rsa.decrypt(block, sentinel='4ert')
        return bytes(res)
