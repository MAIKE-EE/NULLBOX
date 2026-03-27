from html import escape


def build_chat_prompt(user_message, payload, vulnerability_type, lab_type):
    """
    Creates prompts for NULLBOT chat conversations with context from detected vulnerabilities.
    """

    vuln_map = {
        'sqli': 'SQL Injection',
        'xss': 'Cross-Site Scripting',
        'cmdi': 'Command Injection',
        'cmd': 'Command Injection',
        'eval': 'Eval Injection'
    }

    vuln_name = vuln_map.get(vulnerability_type, vulnerability_type)
    escaped_payload = escape(payload, quote=False)

    return f"""You are NULLBOT, a cybersecurity tutor in a safe educational lab.

Lab type: {lab_type}
Payload: {escaped_payload}
Vulnerability type: {vuln_name}
User question: {user_message}

Respond clearly and simply. Keep explanations educational, safe, and relevant to the lab context.
Focus on understanding the vulnerability and how to prevent it.
Do not provide harmful or operational instructions.
"""


def build_payload_explanation_prompt(payload, vulnerability_type, context):
    """
    Creates prompts for payload analysis - educational context.
    """

    vuln_map = {
        'sqli': 'SQL Injection',
        'xss': 'Cross-Site Scripting',
        'cmdi': 'Command Injection',
        'cmd': 'Command Injection',
        'eval': 'Eval Injection'
    }

    vuln_name = vuln_map.get(vulnerability_type, vulnerability_type)

    # Benign case (unchanged)
    if vulnerability_type == 'Benign':
        return f"""You are NULLBOT, a cybersecurity assistant.

Input:
{payload}

Explain in 2-3 clear sentences that this appears to be normal, benign input.
Do not mention attacks or vulnerabilities unnecessarily.
"""

    # Malicious case
    escaped_payload = escape(payload, quote=False)

    return f"""You are a cybersecurity classification assistant.

Context: This is a controlled educational lab.

Input:
{escaped_payload}

Task:
Complete the sentence below.

Sentence:
The input {escaped_payload} is a {vuln_name} pattern associated with ______.

Rules:
- Fill the blank with a short neutral phrase (3–6 words)
- Keep it high-level and non-operational
- Do not explain steps or methods
- Output exactly one sentence only
"""


def build_code_analysis_prompt(code, language):
    """
    Builds a prompt for static code analysis.
    """

    return f"""You are a secure code analyzer.

Analyze the following {language} code snippet and determine if it is vulnerable.

Rules:
- Respond ONLY in valid JSON format
- Do not include any explanation outside the JSON
- If vulnerable, provide the specific vulnerability type
- Be precise and accurate

Output format:
{{
  "vulnerable": true/false,
  "type": "SQL Injection | XSS | Command Injection | Path Traversal | None",
  "explanation": "short explanation"
}}

Code to analyze:
{code}

JSON response:
"""
