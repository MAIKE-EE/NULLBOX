class ChatManager:
    def __init__(self):
        self.sessions = {}

    def start_session(self, session_id):
        self.sessions[session_id] = [
            {
                "role": "system",
                "content": "You are NULLBOT, a cybersecurity assistant helping users understand attacks."
            }
        ]

    def add_user(self, session_id, msg):
        self.sessions[session_id].append({"role": "user", "content": msg})

    def add_assistant(self, session_id, msg):
        self.sessions[session_id].append({"role": "assistant", "content": msg})

    def get(self, session_id):
        return self.sessions.get(session_id, [])