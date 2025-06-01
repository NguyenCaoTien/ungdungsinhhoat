import json
import os

USER_FILE = "datarac/NgDung.json"

def load_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)



def load_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


def register_user(username, password, role="user"):
    users = load_users()
    if any(u["username"] == username for u in users):
        return False, "Tên người dùng đã tồn tại"
    new_user = {
        "username": username,
        "password": password,
        "role": role
    }
    users.append(new_user)
    save_users(users)
    return True, "Đăng ký thành công"

def login_user(username, password):
    users = load_users()
    for u in users:
        if u["username"] == username and u["password"] == password:
            return True, u["role"]
    return False, None
def ensure_admin_exists():
    users = load_users()
    if not any(u["username"] == "admin" for u in users):
        admin_user = {
            "username": "admin",
            "password": "admin123",
            "role": "admin"
        }
        users.append(admin_user)
        save_users(users)

