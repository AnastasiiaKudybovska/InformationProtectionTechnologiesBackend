from time import time
from MD5 import MD5
from LinearCongruentialGenerator import LinearCongruentialGenerator


class RC5:
    def __init__(self, key, w=32, r=12):
        self.w = w * 2
        self.r = 12
        self.key = key
        generator = LinearCongruentialGenerator(44620)
        pseudo_rand = generator.generate_numbers()
        self.res = pseudo_rand[int(time()) % 44620].to_bytes(self.w // 8, byteorder='little')
        self.enc = None
        self.file = None

    def set_key(self, key):
        self.key = key

    def k_to_l(self):
        w2 = self.w // 2
        u = w2 // 8

        res = []
        for i in range(0, len(self.key), u):
            res.append(int.from_bytes(self.key[i:i + u], byteorder='little'))    
        return res
    
    def generate_s(self):
        P = 0xB7E15163
        Q = 0x9E3779B9
        S = [P]

        for i in range(1, 2*(self.r + 1)):
            S.append((S[i-1] + Q) % 2**self.w)
        return S

    def rotate_left(self, value, n):
        w2 = self.w // 2
        n = n % w2
        return ((value << n) & (2**  w2 - 1)) | ((value & (2**  w2 - 1)) >> (w2 - n))


    def rotate_right(self, value, n):
        w2 = self.w // 2
        n = n % w2
        return ((value & (2**w2 - 1)) >> n) | (value << (w2 - n) & (2**w2 - 1))

    def mixer(self, S, L):
        a = 0
        b = 0
        i = 0
        j = 0
        l = len(L)
        t = max(2 * (self.r + 1), len(L))
        for k in range(3*t):
            a = S[i] = self.rotate_left(S[i] + a + b, 3)
            b = L[j] = self.rotate_left(L[j] + a + b, a + b)
            i = (i + 1) % t
            j = (j + 1) % l
        return S
    
    def encode_block(self, mixer_S, data, S):
        w2 = self.w // 2
        b = self.w // 8
        module = 2 ** w2

        A = int.from_bytes(data[:(b // 2)], byteorder='little')
        B = int.from_bytes(data[(b // 2):], byteorder='little')
        A = (A + mixer_S[0]) % module
        B = (B + mixer_S[1]) % module

        for i in range(1, self.r + 1):
            A = (self.rotate_left((A ^ B), B) + S[2 * i]) % module
            B = (self.rotate_left((A ^ B), A) + S[2 * i + 1]) % module

        return A.to_bytes(b // 2, byteorder='little') + B.to_bytes(b // 2, byteorder='little')
    
    def decode_block(self, mixer_S, data):
        w2 = self.w // 2
        b = self.w // 8
        module = 2 ** w2

        A = int.from_bytes(data[:(b // 2)], byteorder='little')
        B = int.from_bytes(data[(b // 2):], byteorder='little')
        
        for i in range(self.r, 0, -1):
            B = self.rotate_right(B - mixer_S[2 * i + 1], A) ^ A
            A = self.rotate_right(A - mixer_S[2 * i], B) ^ B

        B = (B - mixer_S[1]) % module
        A = (A - mixer_S[0]) % module
        

        return A.to_bytes(b // 2, byteorder='little') + B.to_bytes(b // 2, byteorder='little')
    
    def encode(self, mixer_S, data, S):
        w2 = self.w // 2
        b = self.w // 8

        while len(data) % b:
            data += b'\x00'
        
        result = b''
        last = self.res
        result += last 

        for i in range(len(data) // b):
            n_data = data[b * i : b * (i + 1)]
            n_block = bytes([x ^ y for x, y in zip(last, n_data)])
            last = self.encode_block(mixer_S, n_block, S)
            result += last
        self.enc = result
        return result


    def rc5_encode_data(self, data):
        l = self.k_to_l()
        s = self.generate_s()
        mix = self.mixer(s, l)
        result = self.encode(mix, data, s)
        return result
        
    
    def decode(self, mixer_S, data):
        w2 = self.w // 2
        b = self.w // 8

        last = data[:b]
        result = b''

        n_data = data[b:b * 2]

        for i in range(2, len(data) // b + 1):
            uncode = self.decode_block(mixer_S, n_data)
            uncode =  bytes([x ^ y for x, y in zip(last, uncode)])
            last = n_data
            n_data = data[b * i : b * (i + 1)]

            if not n_data:
                uncode = uncode.rstrip(b'\x00')
            result += uncode
        return result
    
    def rc5_decode_data(self, data):
        l = self.k_to_l()
        s = self.generate_s()
        mix = self.mixer(s, l)
        result = self.decode(mix, data)
        return result

    




