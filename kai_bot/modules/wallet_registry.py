import json
import os
from logger import log_event

STORAGE_FILE = "storage/wallets.json"

def load_wallets():
    if not os.path.exists(STORAGE_FILE):
        return []
    with open(STORAGE_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_wallets(wallets):
    with open(STORAGE_FILE, 'w') as f:
        json.dump(wallets, f, indent=4)

def register_wallet(account_id):
    wallets = load_wallets()
    if account_id not in wallets:
        wallets.append(account_id)
        save_wallets(wallets)
        log_event(f"Registered wallet: {account_id}")
        return True
    return False

def list_wallets():
    return load_wallets()

def remove_wallet(account_id):
    wallets = load_wallets()
    if account_id in wallets:
        wallets.remove(account_id)
        save_wallets(wallets)
        log_event(f"Removed wallet: {account_id}")
        return True
    return False
