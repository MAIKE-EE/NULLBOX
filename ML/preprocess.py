# ML/preprocess.py
import re
from urllib.parse import unquote

def preprocess_payload(payload: str) -> str:
    """
    Clean and normalize payload for consistent feature extraction.
    Steps:
    1. URL decode (e.g., %27 -> ')
    2. Lowercase
    3. Normalize special characters (e.g., multiple spaces, tabs)
    4. Remove excess whitespace
    """
    if not isinstance(payload, str):
        payload = str(payload)
    # URL decode
    try:
        payload = unquote(payload)
    except Exception:
        pass
    # Lowercase
    payload = payload.lower()
    # Replace multiple spaces/tabs with single space
    payload = re.sub(r'\s+', ' ', payload)
    # Remove leading/trailing spaces
    payload = payload.strip()
    return payload