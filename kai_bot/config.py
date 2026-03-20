import os
from dotenv import load_dotenv

load_dotenv()

# Hedera Credentials
HEDERA_ACCOUNT_ID = os.getenv("HEDERA_ACCOUNT_ID")
HEDERA_PRIVATE_KEY = os.getenv("HEDERA_PRIVATE_KEY")
HEDERA_NETWORK = os.getenv("HEDERA_NETWORK", "testnet")

# AI API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Ollama (local LLM) — set AI_PROVIDER=ollama in .env to activate
AI_PROVIDER = os.getenv("AI_PROVIDER", "").lower()  # "ollama" | "openrouter" | etc.
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# M-Pesa API Keys
MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE")
MPESA_PASSKEY = os.getenv("MPESA_PASSKEY")
MPESA_CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL")

# Validation
def validate_config():
    if not HEDERA_ACCOUNT_ID or not HEDERA_PRIVATE_KEY:
        print("Warning: Hedera credentials (HEDERA_ACCOUNT_ID, HEDERA_PRIVATE_KEY) are missing.")
