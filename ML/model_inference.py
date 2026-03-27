# ML/model_inference.py

import joblib
import os
import sys

# Get the project root (assuming this file is in ML/ and project root is one level up)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MODEL_PATH = os.path.join(PROJECT_ROOT, "ML", "models", "random_forest_pipeline.joblib")


try:
    from ML.preprocess import preprocess_payload
except ImportError:
    from preprocess import preprocess_payload

class CodeVulnerabilityPredictor:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = DEFAULT_MODEL_PATH
        self.model_path = model_path
        self.pipeline = None
        self.classes = ["Benign", "SQL Injection", "XSS", "Command Injection"]
        self.load_model()

    def load_model(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at {self.model_path}. Please train first.")
        self.pipeline = joblib.load(self.model_path)
        print("Model loaded successfully.")

    def predict(self, code_snippet):
        cleaned = preprocess_payload(code_snippet)
        proba = self.pipeline.predict_proba([cleaned])[0]
        class_idx = int(proba.argmax())
        confidence = proba[class_idx]
        return class_idx, self.classes[class_idx], confidence

    def predict_proba(self, code_snippet):
        cleaned = preprocess_payload(code_snippet)
        proba = self.pipeline.predict_proba([cleaned])[0]
        return {self.classes[i]: proba[i] for i in range(len(self.classes))}