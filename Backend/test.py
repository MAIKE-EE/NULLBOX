# Backend/test.py
import sys
import os

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from ML.model_inference import CodeVulnerabilityPredictor

# Now test
predictor = CodeVulnerabilityPredictor()

test_payloads = [
    "SELECT * FROM users WHERE username='admin' --",
    "<script>alert('XSS')</script>",
    "ping -c 4 127.0.0.1; rm -rf /",
    "Hello, world!"
]

for p in test_payloads:
    idx, name, conf = predictor.predict(p)
    print(f"Payload: {p}\n -> {name} (confidence: {conf:.2f})\n")