from flask import Flask
from flask_cors import CORS
from routes.analyze import analyze_bp
from routes.code_analyzer import code_analyzer_bp
import sys
import os

# Ensure backend folder is in Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def create_app():
    app = Flask(__name__)

    # Enable CORS for frontend-backend communication
    CORS(app)

    # Register blueprints (order matters! code_analyzer_bp first to avoid route conflicts)
    app.register_blueprint(code_analyzer_bp)
    app.register_blueprint(analyze_bp)

    @app.route("/")
    def health_check():
        return {"status": "Backend running"}, 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
