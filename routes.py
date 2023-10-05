from flask import Blueprint, jsonify, request, send_file
from LinearCongruentialGenerator import LinearCongruentialGenerator
from config import ConfigDataLinearCongurentialGenerator
from resp_errors import errors

app_blueprint = Blueprint('app_routes', __name__)

generator = None

@app_blueprint.route('/generate_pseudo_random_sequence', methods=['POST'])
def generate_pseudo_random_sequence():
    global generator 
    try:
        n = int(request.json.get('n'))
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
        generator.write_to_file()  
        path = 'linear_congruential_generated_sequence.txt'
        return send_file(path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": {"code": 500, "message": f"Error writing to file: {str(e)}"}})
