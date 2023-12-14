import base64
from distutils.file_util import write_file
from io import BytesIO
import os
import tempfile
import time
import uuid
import zipfile
from werkzeug.utils import secure_filename
from flask import Blueprint, jsonify, make_response, request, send_file
from DSA import DigitalSignatureAlgorithm
from LinearCongruentialGenerator import LinearCongruentialGenerator
from MD5 import MD5
from RC5 import RC5
from RSA import RivestShamirAdleman
from config import ConfigDataLinearCongurentialGenerator
from resp_errors import errors

app_blueprint = Blueprint('app_routes', __name__)

generator = None
md5 = None
rc5 = None
rsa = None
dsa = None

@app_blueprint.route('/generate_pseudo_random_sequence', methods=['POST'])
def generate_pseudo_random_sequence():
    global generator 
    try:
        n = int(request.json.get('n', 10))
    except (ValueError, TypeError):
        return errors.bad_request
    if n is None:
        return errors.bad_request
    param = ConfigDataLinearCongurentialGenerator
    generator = LinearCongruentialGenerator(n, param.x0, param.m, param.a, param.c)
    generator.generate_numbers()
    return jsonify(generator.rand_numbers), 200

@app_blueprint.route('/get_period_of_generated_pseudo_random_sequence', methods=['GET'])
def get_period_of_generate_pseudo_random_sequence():
    global generator  
    if generator is None:
        return jsonify({'error': {'code': 404, 'message': "The generator is not initialized"}})
        
    period = generator.find_period()
    return jsonify({"period": period})


@app_blueprint.route('/write_to_file_generated_pseudo_random_sequence', methods=['GET'])
def write_to_file_generated_pseudo_random_sequence():
    global generator
    if generator is None:
        return jsonify({'error': {'code': 404, 'message': "The generator is not initialized"}})
    try:
        with open('linear_congruential_generated_sequence.txt', "w") as file:
            for x in generator.rand_numbers:
                file.write(str(x) + "\n")
        path = 'linear_congruential_generated_sequence.txt'
        return send_file(path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": {"code": 500, "message": f"Error writing to file: {str(e)}"}})
    

@app_blueprint.route('/md5_hash', methods=['POST'])
def md5_hash():
    global md5
    try:
        s = request.json.get('s', "")
    except (ValueError, TypeError):
        return errors.bad_request
    if s is None:
        return errors.bad_request
    md5 = MD5()
    return jsonify(md5.hash_text_md5(s)), 200


@app_blueprint.route('/md5_hash_file', methods=['POST'])
def md5_hash_file():
    global md5
    try:
        file = request.files['input_file']
        if file.filename != '':
            file.save(file.filename)
    except (ValueError, TypeError):
        return errors.bad_request
    md5 = MD5()
    file_data = file.read()
    md5.content_for_hash = file_data
    res = md5.hash_file_md5(file.filename)  
    os.remove(file.filename)
    return jsonify(res)

@app_blueprint.route('/download_file_with_hash', methods=['GET'])
def download_file_with_hash():
    global md5
    if md5 is None:
        return jsonify({'error': {'code': 404, 'message': "MD5 is not initialized"}})
    try:
        with open('md5_hash.txt', "w") as file:
            file.write(md5.md_hash)
        path = 'md5_hash.txt'
        return send_file(path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": {"code": 500, "message": f"Error writing to file: {str(e)}"}})

@app_blueprint.route('/check_hash', methods=['POST'])
def md5_check_hash():
    global md5
    try:
        s = request.json.get('s', "")
        hash_check = request.json.get('hash_check', "")
    except (ValueError, TypeError):
        return errors.bad_request
    if hash_check is None:
        return errors.bad_request
    md5 = MD5()
    if (md5.hash_text_md5(s) == hash_check):
        return jsonify("The hash is crrect!"), 200
    else: 
        return jsonify("The hash is incorrect!"), 200

@app_blueprint.route('/check_hash_file', methods=['POST'])
def md5_check_hash_for_file():
    global md5
    try:
        file = request.files['input_file']
        hash_check =  request.form.get('hash_check', "")
        if file.filename != '':
            file.save(file.filename)
    except (ValueError, TypeError):
        return errors.bad_request
    md5 = MD5()
    file_data = file.read()
    md5.content_for_hash = file_data
    res = md5.hash_file_md5(file.filename) 
    os.remove(file.filename)
    if (res == hash_check):
        return jsonify("The hash is correct. File is intact."), 200
    else: 
        return jsonify("The hash is incorrect. File has been modified."), 200


@app_blueprint.route('/rc5_encode_text', methods=['POST'])
def rc5_encrypt_text():
    global rc5
    try:
        user_key = str(request.json.get('key'))
        text = str(request.json.get('text'))
    except (ValueError, TypeError):
        return errors.bad_request
    md5 = MD5()
    start_time = time.time()
    hash = md5.hash_text_md5(user_key)
    key = md5.hash_text_md5(hash)
    key = (key + hash).encode('utf-8')
    rc5 = RC5(key) 
    data = text.encode('utf-8')
    res = rc5.rc5_encode_data(data)
    rc5.enc = res
    # print(rc5.enc)
    res_base64 = base64.b64encode(res).decode('utf-8')
    end_time = time.time()
    rc5.time = end_time - start_time
    return jsonify({
        'encrypted_text': res_base64,
        'encryption_time': rc5.time
    })

@app_blueprint.route('/rc5_encode_file', methods=['POST'])
def rc5_encrypt_file():
    global rc5
    try:
        user_key = str(request.form.get('key'))
        file = request.files['selected_file']    
        if file.filename != '':
            original_filename = secure_filename(file.filename)
            file.save(original_filename) 
    except (ValueError, TypeError):
        return errors.bad_request

    with open(original_filename, 'rb') as file:
        file_data = file.read()

    md5 = MD5()
    start_time = time.time()
    hash = md5.hash_text_md5(user_key)
    key = md5.hash_text_md5(hash)
    key = (key + hash).encode('utf-8')
    rc5 = RC5(key)
    res = rc5.rc5_encode_data(file_data)
    with open("code_" + original_filename, 'wb') as file2:
        file2.write(res)
    end_time = time.time()
    path = "code_" + original_filename
    os.remove(original_filename)
    # print(send_file(path, as_attachment=True))
    rc5.time =  end_time - start_time
    return send_file(path, as_attachment=True)

@app_blueprint.route('/rc5_crypt_file_time', methods=['GET'])
def rc5_crypt_file_time():
    global rc5
    return jsonify(rc5.time)

@app_blueprint.route('/rc5_decode_text', methods=['POST'])
def rc5_decrypt_text():
    global rc5
    try:
        user_key = str(request.json.get('key'))
        text = str(request.json.get('text'))
    except (ValueError, TypeError):
        return errors.bad_request
    md5 = MD5()
    start_time = time.time()
    hash = md5.hash_text_md5(user_key)
    key = md5.hash_text_md5(hash)
    key = (key + hash).encode('utf-8')
    if len(text) != 0: 
        try: 
            data = base64.b64decode(text)
        except:
            return errors.bad_request       
    elif rc5.enc != None: data = rc5.enc
    else: return jsonify(str(''))
    rc5.set_key(key)
    res = rc5.rc5_decode_data(data)
    end_time = time.time()
    rc5.time = end_time - start_time
    return jsonify({
        'decrypted_text': str(res),
        'decryption_time': rc5.time
    })

@app_blueprint.route('/rc5_decode_file', methods=['POST'])
def rc5_decrypt_file():
    global rc5
    try:
        user_key = str(request.form.get('key'))
        file = request.files['selected_file']    
        if file.filename != '':
            # unique_filename = str(uuid.uuid4())
            original_filename = secure_filename(file.filename)
            file.save(original_filename)
    except (ValueError, TypeError):
        return errors.bad_request

    with open(original_filename, 'rb') as file:
        file_data = file.read()
    md5 = MD5()
    start_time = time.time()
    hash = md5.hash_text_md5(user_key)
    key = md5.hash_text_md5(hash)
    key = (key + hash).encode('utf-8')
    rc5 = RC5(key)
    res = rc5.rc5_decode_data(file_data)
    file_extension = os.path.splitext(original_filename)[-1]
    with open("uncode_" + original_filename[5:], 'wb') as file2:
        file2.write(res)
    end_time = time.time()
    rc5.time = end_time - start_time
    response = send_file('uncode_' + original_filename[5:], as_attachment=True)
    os.remove(original_filename)
    return response


### lab 4 

def zip_files(*files):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_archive:
        for file in files:
            zip_archive.write(file)
    zip_buffer.seek(0)
    return zip_buffer.read()

@app_blueprint.route('/rsa_generate_keys', methods=['POST'])
def generate_keys():
    try:
        key_size = int(request.json.get('keySize', 1024))
    except (ValueError, TypeError):
        return errors.bad_request 
    rsa = RivestShamirAdleman(key_size)
    private_key, public_key = rsa.generate_keys()
    with open("private_key.pem", "wb") as file:
        file.write(private_key)
    with open("public_key.pem", "wb") as file1:
        file1.write(public_key)

    response = make_response(zip_files("public_key.pem", "private_key.pem"))
    response.headers["Content-Disposition"] = "attachment; filename=RSA_keys.zip"
    response.headers["Content-Type"] = "application/zip"
    return response

@app_blueprint.route('/rsa_encrypt_text', methods=['POST'])
def rsa_encrypt_text():
    public_key_file = request.files['public_key'] 
    text_encrypt = request.form.get('text_encrypt')
    if not public_key_file or public_key_file.filename == '':
        return errors.bad_request 
    with tempfile.NamedTemporaryFile(delete=False) as temp_key_file:
        public_key_file.save(temp_key_file.name)
        with open(temp_key_file.name, 'rb') as file:
            public_key = file.read()
    rsa = RivestShamirAdleman()
    start_time = time.time()
    encrypted_text = rsa.encrypt_text(text_encrypt, public_key)
    end_time = time.time()
    return jsonify({
        'encrypted_text': encrypted_text,
        'encryption_time': end_time - start_time
    })

@app_blueprint.route('/rsa_encrypt_file', methods=['POST'])
def rsa_encrypt_file():
    public_key_file = request.files['public_key'] 
    file_encrypt = request.files['file_encrypt']
    if not public_key_file or public_key_file.filename == '' or not file_encrypt or file_encrypt.filename == "":
        return errors.bad_request 
    with tempfile.NamedTemporaryFile(delete=False) as temp_key_file:
        public_key_file.save(temp_key_file.name)
        with open(temp_key_file.name, 'rb') as file:
            public_key = file.read()

    with tempfile.NamedTemporaryFile(delete=False) as temp_file_encrypt:
        file_encrypt.save(temp_file_encrypt.name)
        with open(temp_file_encrypt.name, 'rb') as file2:
            data_encrypt = file2.read()
    global rsa
    rsa = RivestShamirAdleman()
    start_time = time.time()
    encrypted_file_data = rsa.encrypt_file(data_encrypt, public_key)
    path = "encrypted_" + file_encrypt.filename
    with open(path, 'wb') as output_file:
        output_file.write(encrypted_file_data)
    end_time = time.time()
    rsa.time = end_time - start_time
    response = send_file(path, as_attachment=True)
    # response.headers['x-encryption-time'] = str(end_time - start_time)
    return response

@app_blueprint.route('/rsa_crypt_file_time', methods=['GET'])
def rsa_crypt_file_time():
    global rsa
    return jsonify(rsa.time)

@app_blueprint.route('/rsa_decrypt_text', methods=['POST'])
def rsa_decrypt_text():
    private_key_file = request.files['private_key'] 
    text_decrypt = request.form.get('text_decrypt')
    if not private_key_file or private_key_file.filename == '':
        return errors.bad_request 
    with tempfile.NamedTemporaryFile(delete=False) as temp_key_file:
        private_key_file.save(temp_key_file.name)
        with open(temp_key_file.name, 'rb') as file:
            private_key = file.read()
    rsa = RivestShamirAdleman()
    start_time = time.time()
    decrypted_text = rsa.decrypt_text(text_decrypt, private_key)
    end_time = time.time()
    return jsonify({
        'decrypted_text': decrypted_text,
        'decryption_time': end_time - start_time
    })

@app_blueprint.route('/rsa_decrypt_file', methods=['POST'])
def rsa_decrypt_file():
    print("start")
    private_key_file = request.files['private_key'] 
    file_decrypt = request.files['file_decrypt']
    if not private_key_file or private_key_file.filename == '' or not file_decrypt or file_decrypt.filename == "":
        return errors.bad_request 
    with tempfile.NamedTemporaryFile(delete=False) as temp_key_file:
        private_key_file.save(temp_key_file.name)
        with open(temp_key_file.name, 'rb') as file:
            private_key = file.read()
    with tempfile.NamedTemporaryFile(delete=False) as temp_file_decrypt:
        file_decrypt.save(temp_file_decrypt.name)
        with open(temp_file_decrypt.name, 'rb') as file2:
            data_decrypt = file2.read()
    global rsa
    rsa = RivestShamirAdleman()
    start_time = time.time()
    decrypted_file_data = rsa.decrypt_file(data_decrypt, private_key)
    path = "decrypted_" + file_decrypt.filename[10:]
    with open(path, 'wb') as output_file:
        output_file.write(decrypted_file_data)
    end_time = time.time()
    rsa.time = end_time - start_time
    return send_file(path, as_attachment=True)

## lab 5

@app_blueprint.route('/dsa_generate_keys', methods=['POST'])
def dsa_generate_keys():
    try:
        key_size = int(request.json.get('keySize', 2048))
    except (ValueError, TypeError):
        return errors.bad_request 
    dsa = DigitalSignatureAlgorithm(key_size)
    private_key, public_key = dsa.generate_keys()
    with open("private_key.pem", "wb") as file:
        file.write(private_key)
    with open("public_key.pem", "wb") as file1:
        file1.write(public_key)

    response = make_response(zip_files("public_key.pem", "private_key.pem"))
    response.headers["Content-Disposition"] = "attachment; filename=DSA_keys.zip"
    response.headers["Content-Type"] = "application/zip"
    return response

@app_blueprint.route('/dsa_sign_text', methods=['POST'])
def dsa_sign_text():
    private_key_file = request.files['private_key'] 
    text_sign = request.form.get('text_sign')
    if not private_key_file or private_key_file.filename == '':
        return errors.bad_request 
    with tempfile.NamedTemporaryFile(delete=False) as temp_key_file:
        private_key_file.save(temp_key_file.name)
        with open(temp_key_file.name, 'rb') as file:
            private_key = file.read()
    dsa = DigitalSignatureAlgorithm()
    signed_text = dsa.make_sign(private_key, text_sign.encode('utf-8'))
    # path = "sign_" + file_sign.filename
    with open("signed_text.txt", "w") as signed_text_out:
        signed_text_out.write(signed_text)
    return send_file("signed_text.txt", as_attachment=True, download_name="signed_text.txt")
    # return jsonify({
    #     'signed_text': signed_text,
    # })

@app_blueprint.route('/dsa_sign_file', methods=['POST'])
def dsa_sign_file():
    private_key_file = request.files['private_key'] 
    file_sign = request.files['file_sign']
    if not private_key_file or private_key_file.filename == '' or not file_sign or file_sign.filename == "":
        return errors.bad_request 
    with tempfile.NamedTemporaryFile(delete=False) as temp_key_file:
        private_key_file.save(temp_key_file.name)
        with open(temp_key_file.name, 'rb') as file:
            private_key = file.read()
    with tempfile.NamedTemporaryFile(delete=False) as temp_file_sign:
        file_sign.save(temp_file_sign.name)
        with open(temp_file_sign.name, 'rb') as file2:
            data_sign = file2.read()
    dsa = DigitalSignatureAlgorithm()
    signed_file = dsa.make_sign(private_key, data_sign)
    with open("signed_file.txt", "w") as signed_file_out:
        signed_file_out.write(signed_file)
    return send_file("signed_file.txt", as_attachment=True, download_name="signed_file.txt")


@app_blueprint.route('/dsa_verify_text', methods=['POST'])
def verify_text():
    public_key_file = request.files['public_key'] 
    signature_file = request.files['signature'] 
    text_sign = request.form.get('text_sign')

    if not public_key_file or public_key_file.filename == '' or not signature_file or signature_file.filename == '':
        return errors.bad_request 
    with tempfile.NamedTemporaryFile(delete=False) as temp_key_file:
        public_key_file.save(temp_key_file.name)
        with open(temp_key_file.name, 'rb') as file:
            public_key = file.read()
    with tempfile.NamedTemporaryFile(delete=False) as temp_signature_file:
        signature_file.save(temp_signature_file.name)
        with open(temp_signature_file.name, 'r') as file:
            signature = file.read()

    dsa = DigitalSignatureAlgorithm()
    signature_data = bytes.fromhex(signature)
    result = dsa.check_sign(public_key, text_sign.encode('utf-8'), signature_data)
    response = {'res': 'Signature is valid!' if result == 1 else 'Signature is invalid!'}
    return jsonify(response)

@app_blueprint.route('/dsa_verify_file', methods=['POST'])
def verify_file():
    public_key_file = request.files['public_key'] 
    signature_file = request.files['signature'] 
    file_sign = request.files['file_sign']

    if not public_key_file or public_key_file.filename == '' or not signature_file or signature_file.filename == '':
        return errors.bad_request 
    with tempfile.NamedTemporaryFile(delete=False) as temp_key_file:
        public_key_file.save(temp_key_file.name)
        with open(temp_key_file.name, 'rb') as file:
            public_key = file.read()
    with tempfile.NamedTemporaryFile(delete=False) as temp_signature_file:
        signature_file.save(temp_signature_file.name)
        with open(temp_signature_file.name, 'r') as file:
            signature = file.read()
    with tempfile.NamedTemporaryFile(delete=False) as temp_file_sign:
        file_sign.save(temp_file_sign.name)
        with open(temp_file_sign.name, 'rb') as file2:
            data_sign = file2.read()

    dsa = DigitalSignatureAlgorithm()
    signature_data = bytes.fromhex(signature)
    result = dsa.check_sign(public_key, data_sign, signature_data)
    response = {'res': 'Signature is valid!' if result == 1 else 'Signature is invalid!'}
    return jsonify(response)