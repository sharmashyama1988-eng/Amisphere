import json
import os

HISTORY_FILE = 'history.json'

def get_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def add_search(query):
    history = get_history()
    if query and query not in history:
        history.append(query)
        # Keep last 20 searches to avoid prompt explosion
        if len(history) > 20:
            history = history[-20:]
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f)

def get_ai_context():
    history = get_history()
    if not history:
        return "New user. Ensure responses are helpful and try to learn what they like."
    return f"The user has previously searched for: {', '.join(history)}. Use this information to tailor the search results summary and recommend related concepts, websites, or topics that align with these interests. Format your answer nicely in HTML fragments if possible or just plain text that looks good."
