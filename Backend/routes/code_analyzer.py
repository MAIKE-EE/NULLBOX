from flask import Blueprint, request, jsonify
from core.code_analyzer import analyze_static_code

code_analyzer_bp = Blueprint('code_analyzer', __name__)

@code_analyzer_bp.route('/analyze_code', methods=['POST'])
def code_analysis():
    """API endpoint for static code analysis"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({'error': 'No code provided'}), 400
        
        # Validate language
        if language not in ['python', 'javascript']:
            return jsonify({'error': 'Unsupported language. Use "python" or "javascript"'}), 400
        
        # Analyze the code
        vulnerabilities = analyze_static_code(code, language)
        
        return jsonify({
            'vulnerabilities': vulnerabilities,
            'language': language,
            'total_vulnerabilities': len(vulnerabilities)
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500