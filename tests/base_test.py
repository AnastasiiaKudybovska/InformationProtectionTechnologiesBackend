import os
import unittest
from flask import Flask
from routes import app_blueprint

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.test_app = Flask(__name__)
        self.test_app.register_blueprint(app_blueprint)
        self.client = self.test_app.test_client()

    def tearDown(self):
        pass
