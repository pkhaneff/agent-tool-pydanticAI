import json
import os

def load_chat_history(user_id, file_path="chat_history.json"):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(user_id, [])

def save_chat_history(user_id, new_query, file_path="chat_history.json"):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
    data.setdefault(user_id, []).append(new_query)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)