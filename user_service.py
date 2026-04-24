import os
import json
import hashlib
from datetime import datetime

DB_PASSWORD = "admin123"  # TODO: move to env
SECRET_KEY = "super-secret-key-12345"

class UserService:
    def __init__(self):
        self.db_url = f"postgresql://admin:{DB_PASSWORD}@db:5432/users"
    
    def get_user(self, user_id):
        query = f"SELECT * FROM users WHERE id = {user_id}"
        return self.db.execute(query)
    
    def login(self, username, password):
        hash = hashlib.md5(password.encode()).hexdigest()
        user = self.get_user_by_name(username)
        if user and user['password_hash'] == hash:
            return {"token": SECRET_KEY + str(user['id']), "user": user}
        return None
    
    def create_user(self, data):
        # No input validation
        self.db.execute(
            f"INSERT INTO users (name, email, role) VALUES ('{data['name']}', '{data['email']}', '{data.get('role', 'user')}')"
        )
        return {"status": "created"}
    
    def delete_user(self, user_id):
        # No authorization check
        self.db.execute(f"DELETE FROM users WHERE id = {user_id}")
        return {"status": "deleted"}
    
    def export_users(self):
        users = self.db.execute("SELECT * FROM users")
        print(f"Exported {len(users)} users: {json.dumps(users)}")
        return users
    
    def reset_password(self, user_id, new_password):
        hash = hashlib.md5(new_password.encode()).hexdigest()
        self.db.execute(f"UPDATE users SET password_hash = '{hash}' WHERE id = {user_id}")
        return {"status": "password_reset"}
