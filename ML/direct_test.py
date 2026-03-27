# ML/direct_test.py
import sys
import os

# Add project root to path so we can import ML.model_inference
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from ML.model_inference import CodeVulnerabilityPredictor

predictor = CodeVulnerabilityPredictor()

payloads = [
    "SELECT * FROM users WHERE username='admin' --",
    "<script>alert('XSS')</script>",
    "ping -c 4 127.0.0.1; rm -rf /",
    "Hello, world!"
]

for p in payloads:
    idx, name, conf = predictor.predict(p)
    proba = predictor.predict_proba(p)
    print(f"Payload: {p}")
    print(f"  -> {name} (confidence: {conf:.2f})")
    print(f"  Probabilities: {proba}")
    print()