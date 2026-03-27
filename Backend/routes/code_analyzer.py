from flask import Blueprint, request, jsonify
from LLM.chat_manager import ChatManager
from LLM.client import call_llm
from LLM.prompt_builder import build_code_analysis_prompt
from core.code_analyzer import analyze_static_code
from utils.code_patterns import get_vulnerability_patterns
import uuid
import json
import re

code_analyzer_bp = Blueprint('code_analyzer', __name__)
chat_manager = ChatManager()

@code_analyzer_bp.route('/analyze_code', methods=['POST'])
def code_analysis():
    """API endpoint for AI-powered code safety analysis"""
    DEBUG_MODE = True  # Set to True to see which path is taken
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

        # Start a chat session for code analysis
        session_id = str(uuid.uuid4())
        chat_manager.start_session(session_id)

        # Build the code analysis prompt
        prompt = build_code_analysis_prompt(code, language)

        # Add to chat history
        chat_manager.add_user(session_id, prompt)

        # Get analysis from LLM
        analysis = call_llm([{"role": "system", "content": "You are cybersecurity tutor analyzing code."}, {"role": "user", "content": prompt}])

        # Add assistant response to session
        chat_manager.add_assistant(session_id, analysis)

        # Parse LLM response (try JSON first, then fallback to rule-based)
        parsed_result = _parse_llm_response(analysis, code, language)

        return jsonify({
            'session_id': session_id,
            'analysis': analysis,
            'vulnerable': parsed_result['vulnerable'],
            'type': parsed_result['type'],
            'explanation': parsed_result['explanation'],
            'vulnerabilities': parsed_result['vulnerabilities']
        }), 200

    except Exception as e:
        print(f"[DEBUG] Error in code_analysis: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


def _parse_llm_response(analysis_text, code, language):
    """
    Parse LLM response - try JSON first, then fallback to rule-based detection
    """
    # Try to parse as JSON first
    json_result = _try_parse_json_response(analysis_text)
    if json_result:
        print(f"[DEBUG] Successfully parsed LLM JSON: {json_result}")
        return json_result

    # JSON parsing failed - use rule-based fallback
    print(f"[DEBUG] JSON parsing failed, using fallback detection")
    return _rule_based_fallback(code, language)


def _try_parse_json_response(analysis_text):
    """
    Try to extract and parse JSON from LLM response
    """
    try:
        # Clean up response - sometimes LLM adds markdown code blocks
        cleaned = analysis_text.strip()
        if cleaned.startswith('```json'):
            cleaned = cleaned.replace('```json', '', 1)
        if cleaned.startswith('```'):
            cleaned = cleaned.replace('```', '', 1)
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        # Parse JSON
        data = json.loads(cleaned)

        # Validate required fields
        if 'vulnerable' not in data:
            print(f"[DEBUG] JSON missing 'vulnerable' field")
            return None

        # Normalize type field
        vuln_type = data.get('type', 'None')
        if vuln_type is None:
            vuln_type = 'None'

        # Return normalized format
        return {
            'vulnerable': bool(data['vulnerable']),
            'type': vuln_type,
            'explanation': data.get('explanation', 'No explanation provided'),
            'vulnerabilities': _convert_to_vulnerability_list(data, cleaned)
        }

    except json.JSONDecodeError as e:
        print(f"[DEBUG] JSON parsing error: {e}")
        return None
    except Exception as e:
        print(f"[DEBUG] Unexpected error parsing JSON: {e}")
        return None


def _rule_based_fallback(code, language):
    """
    Fallback to rule-based pattern matching when LLM fails
    """
    try:
        # Use the existing pattern matching from code_analyzer module
        print(f"[DEBUG FALLBACK] Analyzing {language} code with pattern matching")
        print(f"[DEBUG FALLBACK] Code length: {len(code)}")
        vulnerabilities = analyze_static_code(code, language)

        if vulnerabilities:
            vuln_types = set(v.get('explanation', 'Unknown') for v in vulnerabilities)
            type_map = {
                'SQL': 'SQL Injection',
                'XSS': 'Cross-Site Scripting (XSS)',
                'Cross-Site Scripting': 'Cross-Site Scripting (XSS)',
                'Cross-Site': 'Cross-Site Scripting (XSS)',
                'Command': 'Command Injection',
                'Eval': 'Eval Injection',
                'Path': 'Path Traversal'
            }

            # Determine primary vulnerability type
            vuln_type = 'Potential Vulnerability'
            for explanation in vuln_types:
                for keyword, mapped_type in type_map.items():
                    if keyword in explanation:
                        vuln_type = mapped_type
                        break
                if vuln_type != 'Potential Vulnerability':
                    break

            return {
                'vulnerable': True,
                'type': vuln_type,
                'explanation': f'Rule-based detection found {len(vulnerabilities)} potential issue(s)',
                'vulnerabilities': vulnerabilities
            }
        else:
            return {
                'vulnerable': False,
                'type': 'None',
                'explanation': 'No vulnerabilities detected',
                'vulnerabilities': []
            }

    except Exception as e:
        print(f"[DEBUG] Fallback error: {e}")
        # If everything fails, return safe default (but this should rarely happen)
        return {
            'vulnerable': False,
            'type': 'None',
            'explanation': 'Analysis error - unable to determine vulnerability status',
            'vulnerabilities': []
        }


def _convert_to_vulnerability_list(parsed_data, code):
    """
    Convert parsed JSON to vulnerability list format expected by frontend
    """
    vulnerable = parsed_data.get('vulnerable', False)
    type_str = parsed_data.get('type', 'None')

    if not vulnerable or type_str == 'None':
        return []

    # Create vulnerability entry based on type
    vuln_map = {
        'SQL Injection': 'SQL injection patterns detected in query construction',
        'Cross-Site Scripting (XSS)': 'XSS vulnerability in user input handling',
        'Command Injection': 'Command injection vulnerability in system call',
        'Path Traversal': 'Path traversal vulnerability in file operations',
        'Eval Injection': 'Unsafe eval() usage with user input'
    }

    return [{
        'line': 1,  # Default to line 1 since LLM doesn't provide line numbers
        'mistake': 'Direct user input usage',
        'explanation': vuln_map.get(type_str, f'{type_str} vulnerability'),
        'solution': 'Review code for security best practices',
        'example': parsed_data.get('explanation', 'No specific solution provided')
    }]
