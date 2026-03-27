from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Ensure backend folder is in Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.detector import Detector
from LLM.chat_manager import ChatManager
from LLM.client import call_llm
from LLM.prompt_builder import build_explanation_prompt
import uuid

# Global instances
detector = Detector()
chat_manager = ChatManager()

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Single endpoint for ALL analysis: single payloads and full code"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    input_code = data.get('code', '')
    if not input_code:
        return jsonify({"error": "No code provided"}), 400

    result = detector.detect(input_code)

    if result.get('is_vulnerable'):
        session_id = str(uuid.uuid4())
        chat_manager.start_session(session_id)

        prompt = build_explanation_prompt(input_code, result.get('vulnerability_type', 'Unknown'))

        chat_manager.add_user(session_id, prompt)
        explanation = call_llm([
            {"role": "system", "content": "You are a cybersecurity tutor. Respond concisely - one short sentence 'This is a type of [attack]'."},
            {"role": "user", "content": prompt}
        ])
        chat_manager.add_assistant(session_id, explanation)

        return jsonify({
            "is_vulnerable": result['is_vulnerable'],
            "vulnerability_type": result['vulnerability_type'],
            "confidence": result['confidence'],
            "message": result['message'],
            "explanation": explanation,
            "session_id": session_id,
            "chat_available": True
        })
    else:
        return jsonify({
            "is_vulnerable": False,
            "vulnerability_type": None,
            "confidence": result['confidence'],
            "message": result['message'],
            "chat_available": False
        })

@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint for follow-up questions"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    session_id = data.get('session_id')
    message = data.get('message')

    if not session_id:
        return jsonify({"error": "No 'session_id' provided"}), 400

    if not message:
        return jsonify({"error": "No 'message' provided"}), 400

    chat_manager.add_user(session_id, message)
    messages = chat_manager.get(session_id)

    if not messages:
        return jsonify({"error": "Session not found"}), 404

    response = call_llm(messages)
    chat_manager.add_assistant(session_id, response)

    return jsonify({
        "response": response,
        "session_id": session_id
    })

@app.route("/")
def health_check():
    return {"status": "Backend running"}, 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
