# Backend/routes/analyze.py

from flask import Blueprint, request, jsonify
from core.detector import Detector
from core.explainer import generate_explanation
from LLM.chat_manager import ChatManager
from LLM.client import call_llm
from LLM.prompt_builder import build_code_analysis_prompt, build_payload_explanation_prompt

import uuid

analyze_bp = Blueprint('analyze', __name__)

detector = Detector()
chat_manager = ChatManager()

@analyze_bp.route('/analyze_code', methods=['POST'])
def analyze_code():
    """
    Direct LLM analysis for code snippets.
    Bypasses detector and sends directly to LLM for analysis.
    Returns: {"analysis": "LLM response", "session_id": "..."}
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    # Support both 'code' and 'payload' fields for flexibility
    code = data.get('code', '') or data.get('payload', '')
    if not code:
        return jsonify({"error": "No code provided"}), 400

    language = data.get('language', 'python')

    # Start a chat session for this code analysis
    session_id = str(uuid.uuid4())
    chat_manager.start_session(session_id)

    # Build the code analysis prompt
    prompt = build_code_analysis_prompt(code, language)

    # Add prompt to chat history
    chat_manager.add_user(session_id, prompt)

    # Get analysis from LLM
    analysis = call_llm([
        {"role": "system", "content": "You are NULLBOT analyzing code for security vulnerabilities."},
        {"role": "user", "content": prompt}
    ])

    # Add assistant response to session
    chat_manager.add_assistant(session_id, analysis)

    # Return the LLM analysis directly
    return jsonify({
        "analysis": analysis,
        "session_id": session_id,
        "chat_available": True
    }), 200

@analyze_bp.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    # Support both 'code' and 'payload' fields for flexibility
    code = data.get('code', '') or data.get('payload', '')
    if not code:
        return jsonify({"error": "No code provided"}), 400

    # Get lab type to filter vulnerabilities
    lab_type = data.get('lab_type', '')

    # Detect vulnerabilities using the detector
    result = detector.detect(code)

    # Filter results based on lab type
    is_vulnerable = result['is_vulnerable']
    vulnerability_type = result['vulnerability_type']

    # Apply lab-specific filtering
    if lab_type == 'login':
        # LOGIN LAB should only show SQL injection
        if vulnerability_type != 'sqli':
            is_vulnerable = False
            vulnerability_type = 'Benign'
    elif lab_type == 'comment':
        # COMMENT LAB should only show XSS
        if vulnerability_type != 'xss':
            is_vulnerable = False
            vulnerability_type = 'Benign'

    # Generate explanation - use LLM for malicious payloads, static for benign
    if is_vulnerable:
        # Use LLM to generate dynamic explanation for detected attack
        prompt = build_payload_explanation_prompt(code, vulnerability_type, lab_type)
        explanation_msg = call_llm([
            {"role": "system", "content": "You are NULLBOT, a cybersecurity assistant. Explain vulnerabilities clearly."},
            {"role": "user", "content": prompt}
        ])
    else:
        # Use static explanation for benign inputs
        explanation_msg = generate_explanation('Benign', lab_type, code)

    # If vulnerable (after filtering), create a session for potential chat
    session_id = None
    if is_vulnerable:
        session_id = str(uuid.uuid4())
        chat_manager.start_session(session_id)

    # Return detection results with filtering applied
    return jsonify({
        "is_vulnerable": is_vulnerable,
        "vulnerability_type": vulnerability_type,
        "confidence": result['confidence'],
        "message": explanation_msg,
        "explanation": explanation_msg,
        "session_id": session_id,
        "chat_available": is_vulnerable
    }), 200

@analyze_bp.route("/ping_analyze", methods=["POST"])
def ping_analyze():
    """
    Endpoint for ping command injection classification.
    Accepts: {hostname: "..."}
    Returns ML classification and LLM explanation for malicious payloads.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    hostname = data.get('hostname', '')
    if not hostname:
        return jsonify({"error": "No hostname provided"}), 400

    result = detector.detect(hostname)

    # Generate explanation - use LLM for malicious payloads
    if result['is_vulnerable']:
        # Use LLM to generate dynamic explanation for detected attack
        prompt = build_payload_explanation_prompt(hostname, result['vulnerability_type'], "ping")
        explanation_msg = call_llm([
            {"role": "system", "content": "You are NULLBOT, a cybersecurity assistant. Explain vulnerabilities clearly."},
            {"role": "user", "content": prompt}
        ])
    else:
        # Use static explanation for benign inputs
        explanation_msg = generate_explanation("Benign", "ping", hostname)

    # Create session for chat if vulnerable
    session_id = None
    if result['is_vulnerable']:
        session_id = str(uuid.uuid4())
        chat_manager.start_session(session_id)

    return jsonify({
        "is_vulnerable": result['is_vulnerable'],
        "vulnerability_type": result['vulnerability_type'],
        "confidence": result['confidence'],
        "message": explanation_msg,
        "explanation": explanation_msg,
        "session_id": session_id,
        "chat_available": result['is_vulnerable']
    }), 200

@analyze_bp.route('/chat', methods=['POST'])
def chat():
    """
    Continue chat conversation with LLM
    Request body: {
        "session_id": "...",
        "message": "user's follow-up question",
        "payload": "...",
        "vulnerability_type": "...",
        "lab_type": "..."
    }
    """
    print("=== CHAT REQUEST RECEIVED ===")
    data = request.get_json()
    if not data:
        print("ERROR: No JSON data provided")
        return jsonify({"error": "No JSON data provided"}), 400

    session_id = data.get('session_id')
    message = data.get('message')
    payload = data.get('payload', '')
    vulnerability_type = data.get('vulnerability_type', 'Benign')
    lab_type = data.get('lab_type', '')

    print(f"DEBUG: session_id={session_id}")
    print(f"DEBUG: message={message}")
    print(f"DEBUG: payload={payload}")
    print(f"DEBUG: vulnerability_type={vulnerability_type}")
    print(f"DEBUG: lab_type={lab_type}")

    if not session_id:
        print("ERROR: No session_id")
        return jsonify({"error": "No 'session_id' provided"}), 400

    if not message:
        print("ERROR: No message")
        return jsonify({"error": "No 'message' provided"}), 400

    # Build chat prompt with context
    from LLM.prompt_builder import build_chat_prompt
    prompt = build_chat_prompt(message, payload, vulnerability_type, lab_type)
    print(f"DEBUG: Built prompt: {prompt[:100]}...")

    # Add user message to session
    chat_manager.add_user(session_id, prompt)
    print(f"DEBUG: Added user message to session")

    # Get conversation history
    messages = chat_manager.get(session_id)
    print(f"DEBUG: Retrieved {len(messages)} messages from session")

    if not messages:
        print("ERROR: Session not found")
        return jsonify({"error": "Session not found or expired"}), 404

    # Call LLM with full conversation history
    print("DEBUG: Calling LLM...")
    response = call_llm(messages)
    print(f"DEBUG: LLM returned: {response[:100]}...")

    # Add assistant response to session
    chat_manager.add_assistant(session_id, response)
    print("DEBUG: Added assistant response to session")

    result = {
        "response": response,
        "session_id": session_id
    }
    print(f"DEBUG: Returning: {result}")
    print("=== CHAT REQUEST COMPLETE ===")

    return jsonify(result)
