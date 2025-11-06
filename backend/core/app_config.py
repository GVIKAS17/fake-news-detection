from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

class AppConfig:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app, resources={r"/*": {"origins": "*"}})
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

    def get_app(self):
        return self.app, self.socketio
