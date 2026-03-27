import sys
import os
import re

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

from ML.model_inference import CodeVulnerabilityPredictor

class Detector:
    def __init__(self):
        self.predictor = CodeVulnerabilityPredictor()
        # Simple regex patterns for command injection (fallback)
        self.cmd_patterns = [
            r'\|\s*\w+',           # pipe followed by command
            r';\s*\w+',            # semicolon
            r'&\s*\w+',            # ampersand
            r'\$\s*\(',            # $(command)
            r'`[^`]+`',            # backticks
            r'ping\s+-c',          # ping command
            r'rm\s+-rf',           # dangerous deletion
            r'wget\s+',            # wget
            r'curl\s+',            # curl
        ]
        self.cmd_re = re.compile('|'.join(self.cmd_patterns), re.IGNORECASE)

    def detect(self, code):
        # First, try ML prediction
        class_idx, class_name, confidence = self.predictor.predict(code)
        is_vuln = (class_idx != 0)

        # In detector.py, inside detect() method, after ML prediction:

        if class_name == "Command Injection" and confidence < 0.6:
         # Low confidence, treat as benign
          class_name = "Benign"
          is_vuln = False

        # Fallback for command injection
        if self.cmd_re.search(code):
            class_name = "Command Injection"
            is_vuln = True
            confidence = max(confidence, 0.85)  # assign a high confidence

        return {
            "is_vulnerable": is_vuln,
            "vulnerability_type": class_name if is_vuln else None,
            "confidence": confidence,
            "message": self._generate_explanation(class_name, confidence)
        }

    def _generate_explanation(self, vuln_type, confidence):
        if vuln_type == "Benign":
            return "No known vulnerability patterns detected."
        elif vuln_type == "SQL Injection":
            return "This payload appears to contain SQL injection patterns. It could manipulate database queries."
        elif vuln_type == "XSS":
            return "This payload appears to contain Cross‑Site Scripting (XSS) patterns. It could execute malicious scripts in a victim's browser."
        elif vuln_type == "Command Injection":
            return "This payload appears to contain command injection patterns. It could execute arbitrary system commands."
        else:
            return "Potential security risk detected."

# Optional: wrapper function for backward compatibility
_detector_instance = Detector()
def detect_attack(code):
    return _detector_instance.detect(code)