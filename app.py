from flask import Flask
from routes import app_blueprint  
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# app.register_blueprint(app_blueprint, url_prefix='/app_routes')
app.register_blueprint(app_blueprint)
if __name__ == '__main__':
    app.run(debug=True)
