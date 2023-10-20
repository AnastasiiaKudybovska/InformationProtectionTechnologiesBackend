import math
 
class MD5:
    def __init__(self):
        self.rotation_amounts = [7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
                          5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
                          4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
                          6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21]
        self.constants = [int(abs(math.sin(i + 1)) * 4294967296) & 0xFFFFFFFF for i in range(64)]
        self.md_hash = None
        self.initial_hash_values  = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476]
        
    def pad_message(self, message):
        message_len_in_bits = (8 * len(message)) & 0xffffffffffffffff
        message.append(0x80)
        while len(message) % 64 != 56:
            message.append(0)
        message += message_len_in_bits.to_bytes(8, byteorder='little')
        return message
 
    def left_rotate(self, x, amount):
        x &= 0xFFFFFFFF
        return (x << amount | x >> (32 - amount)) & 0xFFFFFFFF
    
    def hash_to_hex(self, digest):
        raw_bytes = digest.to_bytes(16, byteorder='little')
        return '{:032x}'.format(int.from_bytes(raw_bytes, byteorder='big'))
 
    def process_message(self, msg):
        init_temp = self.initial_hash_values[:]
 
        for offset in range(0, len(msg), 64):
            A, B, C, D = init_temp
            block = msg[offset:offset + 64]
 
            for i in range(64):
                if i < 16:
                    func = lambda b, c, d: (b & c) | (~b & d)
                    index_func = lambda i: i
                elif 16 <= i < 32:
                    func = lambda b, c, d: (d & b) | (~d & c)
                    index_func = lambda i: (5 * i + 1) % 16
                elif 32 <= i < 48:
                    func = lambda b, c, d: b ^ c ^ d
                    index_func = lambda i: (3 * i + 5) % 16
                elif 48 <= i < 64:
                    func = lambda b, c, d: c ^ (b | ~d)
                    index_func = lambda i: (7 * i) % 16
 
                F = func(B, C, D)
                G = index_func(i)
 
                to_rotate = A + F + self.constants[i] + int.from_bytes(block[4 * G: 4 * G + 4], byteorder='little')
                newB = (B + self.left_rotate(to_rotate, self.rotation_amounts[i])) & 0xFFFFFFFF
 
                A, B, C, D = D, newB, B, C
 
            for i, val in enumerate([A, B, C, D]):
                init_temp[i] += val
                init_temp[i] &= 0xFFFFFFFF
 
        return sum(buffer_content << (32 * i) for i, buffer_content in enumerate(init_temp))
 

    def hash_text_md5(self, message):
        message = bytearray(message.encode('utf-8'))
        message = self.pad_message(message)
        processed_msg = self.process_message(message)
        message_hash = self.hash_to_hex(processed_msg)
        self.md_hash = message_hash
        return message_hash
    
    def hash_file_md5(self, filename):
        with open(filename, 'rb') as file:
            file_data = file.read()
            file_data = bytearray(file_data)
            file_data = self.pad_message(file_data)
            processed_msg = self.process_message(file_data)
            file_hash = self.hash_to_hex(processed_msg)
            self.md_hash = file_hash
            return file_hash
