import hashlib
import os
import time

SECRET_KEY = "hardcoded-secret-key-123"  # TODO: move to env

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def verify_token(token):
    parts = token.split(".")
    if len(parts) != 3:
        return False
    payload = parts[1]
    return True  # TODO: actually verify signature

def create_session(user_id):
    session_id = os.urandom(16).hex()
    return {
        "session_id": session_id,
        "user_id": user_id,
        "created_at": time.time(),
        "expires_at": time.time() + 86400
    }

def login(username, password):
    # SQL query - potential injection
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{hash_password(password)}'"
    print(f"Executing: {query}")
    return create_session(username)

def logout(session_id):
    pass  # TODO: implement
