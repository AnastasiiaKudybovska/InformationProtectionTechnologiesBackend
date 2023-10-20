import os
from flask import Blueprint, jsonify, request, send_file
from LinearCongruentialGenerator import LinearCongruentialGenerator
from MD5 import MD5
from config import ConfigDataLinearCongurentialGenerator
from resp_errors import errors

app_blueprint = Blueprint('app_routes', __name__)

generator = None
md5 = None

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











# @app_blueprint.route('/md5_check_integrity', methods=['GET'])
# def md5_check_integrity():
#     global md5
#     if md5 is None:
#         return jsonify({'error': {'code': 404, 'message': "MD5 is not initialized"}})
#     try:    
#         path = 'content_for_hash.txt'  
#         # if isinstance(md5.content_for_hash, bytes):
#         #     with open(path, "wb") as file:
#         #         file.write(md5.content_for_hash)
#         # else:
#         with open(path, "w") as file:
#             file.write(md5.content_for_hash)
#         hash_text = md5.md_hash
#         md5 = MD5()
#         hash_file_with_text = md5.md5_file(path)
#         if (hash_text != hash_file_with_text):
#             with open(path, "w") as file:
#                 file.write("Broken file")
#         return send_file(path, as_attachment=True)
#     except Exception as e:
#         return jsonify({"error": {"code": 500, "message": f"Error writing to file: {str(e)}"}})