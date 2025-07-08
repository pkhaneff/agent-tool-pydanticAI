import json
import os

def load_user_context(user_id, file_path="user_context.json"):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(user_id, {})

def save_user_context(user_id, context, file_path="user_context.json"):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
    data[user_id] = context
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2) 