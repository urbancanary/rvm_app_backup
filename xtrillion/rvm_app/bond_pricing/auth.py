import os
import json
from pathlib import Path

CONFIG_FILE = 'user_config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return None

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def login(username, password):
    config = load_config()
    if config and config['username'] == username and config['password'] == password:
        return True
    return False

def signup(username, password):
    config = {'username': username, 'password': password, 'is_admin': False}
    save_config(config)

def change_password(username, old_password, new_password):
    if login(username, old_password):
        config = load_config()
        config['password'] = new_password
        save_config(config)
        return True
    return False

def delete_config():
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)

def is_admin():
    config = load_config()
    return config and config.get('is_admin', False)
