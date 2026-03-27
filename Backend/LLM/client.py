import requests
from .config import OLLAMA_URL, MODEL_NAME


def call_llm(messages):
    """
    Call Ollama LLM API and ensure complete response.
    Prevents truncation by using num_predict and continuation logic.
    """
    data = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {
            "num_predict": 2048  # Ensure enough tokens for complete response
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=data, timeout=30)
        result = response.json()

        # Validate response format
        if "message" not in result or "content" not in result["message"]:
            return "Error: Invalid response format from LLM"

        content = result["message"]["content"].strip()

        # If response doesn't end with punctuation, it might be truncated
        sentence_endings = (".", "!", "?", '"', ')')
        if not any(content.endswith(punct) for punct in sentence_endings):
            # Try to get continuation
            continuation = _get_continuation(messages, content)
            if continuation:
                return content + " " + continuation

        return content

    except requests.exceptions.Timeout:
        return "Error: LLM request timed out. Please try again."
    except Exception as e:
        return f"LLM Error: {str(e)}"


def _get_continuation(messages, previous_content):
    """Get continuation of truncated response."""
    continuation_messages = messages + [
        {"role": "assistant", "content": previous_content},
        {"role": "user", "content": "Please complete your explanation. Continue from where you left off."}
    ]

    try:
        data = {
            "model": MODEL_NAME,
            "messages": continuation_messages,
            "stream": False,
            "options": {"num_predict": 1024}
        }

        response = requests.post(OLLAMA_URL, json=data, timeout=30)
        result = response.json()

        if "message" in result and "content" in result["message"]:
            return result["message"]["content"].strip()

        return ""

    except:
        return ""
