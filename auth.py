import os
import json
import hashlib
from datetime import datetime

USERS_FILE = os.path.join(os.path.dirname(__file__), "data", "users.json")
HISTORY_DIR = os.path.join(os.path.dirname(__file__), "data", "history")

def _hash_password(password: str) -> str:
    """Hash password using SHA-256 with a salt."""
    salt = "med_ai_diag_secure_salt_2026"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def init_db():
    """Initialize user storage and default demo patient."""
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    os.makedirs(HISTORY_DIR, exist_ok=True)

    if not os.path.exists(USERS_FILE):
        default_users = {
            "john.doe@example.com": {
                "patient_id": "PT-89421",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "password_hash": _hash_password("Password123!"),
                "age": 42,
                "gender": "Male",
                "blood_group": "O+",
                "phone": "+1 (555) 234-5678",
                "allergies": "Penicillin",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "sarah.connor@example.com": {
                "patient_id": "PT-77219",
                "name": "Sarah Connor",
                "email": "sarah.connor@example.com",
                "password_hash": _hash_password("Demo1234!"),
                "age": 35,
                "gender": "Female",
                "blood_group": "A+",
                "phone": "+1 (555) 987-6543",
                "allergies": "None known",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_users, f, indent=4)

def load_users():
    init_db()
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

def authenticate_user(email, password):
    users = load_users()
    email_clean = email.strip().lower()
    if email_clean in users:
        if users[email_clean]["password_hash"] == _hash_password(password):
            user_data = dict(users[email_clean])
            del user_data["password_hash"]
            return True, user_data
    return False, None

def register_user(name, email, password, age, gender, blood_group, phone="", allergies="None"):
    users = load_users()
    email_clean = email.strip().lower()
    if email_clean in users:
        return False, "An account with this email already exists."

    import random
    patient_id = f"PT-{random.randint(10000, 99999)}"

    users[email_clean] = {
        "patient_id": patient_id,
        "name": name.strip(),
        "email": email_clean,
        "password_hash": _hash_password(password),
        "age": int(age),
        "gender": gender,
        "blood_group": blood_group,
        "phone": phone.strip(),
        "allergies": allergies.strip() if allergies else "None",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_users(users)
    return True, f"Patient account created successfully! Patient ID: {patient_id}"

def save_patient_record(patient_id, record):
    """Save diagnosis record to patient's history."""
    init_db()
    file_path = os.path.join(HISTORY_DIR, f"{patient_id}.json")
    history = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []
    
    record["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history.insert(0, record)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

def get_patient_history(patient_id):
    """Retrieve history of diagnoses for patient."""
    file_path = os.path.join(HISTORY_DIR, f"{patient_id}.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []
