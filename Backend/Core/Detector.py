#ML MODEL LINE 57

import re
from utils.patterns import (
    SQLI_PATTERNS,
    XSS_PATTERNS,
    CMD_INJECTION_PATTERNS
)


def detect_attack(payload: str) -> dict:
    """
    Detects the type of injection attack using rule-based pattern matching.

    Returns:
        dict: {
            "attack_type": str,
            "matched_pattern": str or None,
            "confidence": str
        }
    """

    payload_lower = payload.lower()

    # 1. SQL Injection Detection
    for pattern in SQLI_PATTERNS:
        if re.search(pattern, payload_lower):
            return {
                "attack_type": "SQL Injection",
                "matched_pattern": pattern,
                "confidence": "Rule-based"
            }

    # 2. XSS Detection
    for pattern in XSS_PATTERNS:
        if re.search(pattern, payload_lower):
            return {
                "attack_type": "Cross-Site Scripting (XSS)",
                "matched_pattern": pattern,
                "confidence": "Rule-based"
            }

    # 3. Command Injection Detection
    for pattern in CMD_INJECTION_PATTERNS:
        if re.search(pattern, payload_lower):
            return {
                "attack_type": "Command Injection",
                "matched_pattern": pattern,
                "confidence": "Rule-based"
            }

    # 4. If nothing matches
    return {
        "attack_type": "Benign / No Injection Detected",
        "matched_pattern": None,
        "confidence": "Rule-based"
    }

