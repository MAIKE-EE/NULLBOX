import sys
import os

# Fix Python path FIRST - before any imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS
from routes.analyze import analyze_bp
from routes.code_analyzer import code_analyzer_bp
from routes.login_lab import login_lab_bp


def create_app():
    app = Flask(__name__)

    # Required for session management
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

    # Enable CORS for all routes and origins (development only)
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Register blueprints (order matters! code_analyzer_bp first to avoid route conflicts)
    app.register_blueprint(code_analyzer_bp)
    app.register_blueprint(analyze_bp)
    app.register_blueprint(login_lab_bp)

    @app.route("/")
    def health_check():
        return {"status": "Backend running"}, 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
