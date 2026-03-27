OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.1:8b"

# Model parameters to prevent truncation and control response length
MODEL_PARAMS = {
    "num_predict": 1024,  # Maximum tokens to generate
    "temperature": 0.7,   # Balanced creativity vs consistency
    "top_p": 0.9,         # Nucleus sampling
    "repeat_penalty": 1.1 # Prevent repetition
}
