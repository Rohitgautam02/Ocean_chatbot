# data_pipeline.py
import os

def save_conversation(user_text, bot_reply, filename):
    # Ensure directory exists before writing
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"User: {user_text}\n")
        f.write(f"Bot: {bot_reply}\n\n")


def read_conversation(filename):
    path = os.path.join("chats", filename)
    if not os.path.exists(path):
        return []
    messages = []
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    user, bot = None, None
    for line in lines:
        if line.startswith("User:"):
            user = line.replace("User:", "").strip()
        elif line.startswith("Bot:"):
            bot = line.replace("Bot:", "").strip()
            if user and bot:
                messages.append(("user", user))
                messages.append(("bot", bot))
                user, bot = None, None
    return messages
