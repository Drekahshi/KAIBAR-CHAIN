import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_chat(message):
    print(f"\nTESTING: {message}")
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"message": message},
            timeout=10
        )
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    test_chat("show me vaults")
    test_chat("check tokenomics")
    test_chat("deposit 500 KAI to YT_VAULT")
    test_chat("airdrop 50")
    test_chat("list registered wallets")
