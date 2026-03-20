import json
import os
from datetime import datetime, timedelta
from logger import log_event

SCHEDULE_FILE = "storage/scheduled_transactions.json"

def get_schedules():
    if not os.path.exists(SCHEDULE_FILE):
        return []
    with open(SCHEDULE_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_schedules(schedules):
    with open(SCHEDULE_FILE, 'w') as f:
        json.dump(schedules, f, indent=4)

def schedule_transaction(tx_type, amount, delay_hours):
    """
    Simulates scheduling a transaction.
    """
    schedules = get_schedules()
    execute_time = datetime.now() + timedelta(hours=int(delay_hours))
    
    new_schedule = {
        "id": len(schedules) + 1,
        "type": tx_type,
        "amount": amount,
        "execute_at": execute_time.isoformat(),
        "status": "pending"
    }
    
    schedules.append(new_schedule)
    save_schedules(schedules)
    log_event(f"Scheduled transaction: {tx_type} for {amount} in {delay_hours} hours.")
    print(f"Transaction scheduled successfully! ID: {new_schedule['id']}, Executes at: {execute_time.strftime('%Y-%m-%d %H:%M:%S')}")

def list_scheduled():
    schedules = get_schedules()
    print("\n--- Scheduled Transactions ---")
    if not schedules:
        print("No pending transactions.")
    else:
        for s in schedules:
            print(f"ID {s['id']}: {s['type']} - {s['amount']} | Execute at: {s['execute_at']} | Status: {s['status']}")
    print("------------------------------\n")
