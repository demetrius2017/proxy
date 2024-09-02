import os

USERS_FILE = "user_ids.txt"

def save_user_id(user_id):
    user_id = str(user_id)
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            users = f.read().splitlines()
    else:
        users = []
    
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, 'w') as f:
            f.write('\n'.join(users))

def get_user_ids():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return f.read().splitlines()
    return []

def export_user_ids(output_file="exported_user_ids.txt"):
    user_ids = get_user_ids()
    with open(output_file, 'w') as f:
        f.write('\n'.join(user_ids))
    return output_file