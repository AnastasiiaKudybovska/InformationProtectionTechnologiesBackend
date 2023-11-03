import base64
from distutils.file_util import write_file
import os
import uuid
from werkzeug.utils import secure_filename
from flask import Blueprint, jsonify, make_response, request, send_file
from LinearCongruentialGenerator import LinearCongruentialGenerator
from MD5 import MD5
from RC5 import RC5
from config import ConfigDataLinearCongurentialGenerator
from resp_errors import errors

app_blueprint = Blueprint('app_routes', __name__)

generator = None
md5 = None
rc5 = None

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
    hash = md5.hash_text_md5(user_key)
    key = md5.hash_text_md5(hash)
    key = (key + hash).encode('utf-8')

    rc5 = RC5(key)
    data = text.encode('utf-8')
    res = rc5.rc5_encode_data(data)
    rc5.enc = res
    # print(rc5.enc)
    res_base64 = base64.b64encode(res).decode('utf-8')
    return jsonify(res_base64)


@app_blueprint.route('/rc5_encode_file', methods=['POST'])
def rc5_encrypt_file():
    global rc5
    try:
        user_key = str(request.form.get('key'))
        file = request.files['selected_file']    
        if file.filename != '':
            original_filename = secure_filename(file.filename)
            file.save(original_filename)  # Зберегти файл з оригінальним іменем
    except (ValueError, TypeError):
        return errors.bad_request

    with open(original_filename, 'rb') as file:
        file_data = file.read()

    md5 = MD5()
    hash = md5.hash_text_md5(user_key)
    key = md5.hash_text_md5(hash)
    key = (key + hash).encode('utf-8')
    rc5 = RC5(key)
    res = rc5.rc5_encode_data(file_data)
    

    with open("code_" + original_filename, 'wb') as file2:
        file2.write(res)

    path = "code_" + original_filename

    os.remove(original_filename)
    print(send_file(path, as_attachment=True))

    return send_file(path, as_attachment=True)





@app_blueprint.route('/rc5_decode_text', methods=['POST'])
def rc5_decrypt_text():
    global rc5
    try:
        user_key = str(request.json.get('key'))
        text = str(request.json.get('text'))
    except (ValueError, TypeError):
        return errors.bad_request
    md5 = MD5()
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
    return jsonify(str(res))

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
    hash = md5.hash_text_md5(user_key)
    key = md5.hash_text_md5(hash)
    key = (key + hash).encode('utf-8')
    rc5 = RC5(key)
    res = rc5.rc5_decode_data(file_data)
    file_extension = os.path.splitext(original_filename)[-1]
    with open("uncode_" + original_filename[5:], 'wb') as file2:
        file2.write(res)
    response = send_file('uncode_' + original_filename[5:], as_attachment=True)

    os.remove(original_filename)
    return response

