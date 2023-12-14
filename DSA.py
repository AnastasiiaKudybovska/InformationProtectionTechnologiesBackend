from Crypto.PublicKey import DSA
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
from Crypto.IO import PEM


class DigitalSignatureAlgorithm:
    def __init__(self, key_size=2048, res = None):
        self.res = res
        self.private_key = None
        self.public_key = None
        self.key_size = key_size

    def generate_keys(self):
        key = DSA.generate(self.key_size)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        return private_key, public_key

    def make_sign(self, private_key_data, message):
        private_key = DSA.import_key(private_key_data)
        hash_obj = SHA256.new(message)
        signer = DSS.new(private_key, 'fips-186-3')
        signature = signer.sign(hash_obj)
        return signature.hex()
    
    def check_sign(self, public_key_data, message, signature):
        public_key = DSA.import_key(public_key_data)
        hash_obj = SHA256.new(message)
        verifier = DSS.new(public_key, 'fips-186-3')
        try:
            verifier.verify(hash_obj, signature)
            return 1
        except ValueError:
            return 0