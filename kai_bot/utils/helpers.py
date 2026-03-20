import re

def validate_hedera_id(account_id):
    """Validates Hedera format 0.0.XXXX"""
    pattern = r"^0\.0\.\d+$"
    return bool(re.match(pattern, account_id))

def format_hbar(tinybars):
    """Converts tinybars to HBAR string"""
    return f"{tinybars / 100_000_000:.4f} ℏ"

def format_percentage(value):
    """Formats decimal to percentage"""
    return f"{value * 100:.2f}%"
