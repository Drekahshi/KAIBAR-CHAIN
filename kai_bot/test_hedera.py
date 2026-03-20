import os
from hiero import (
    Client,
    AccountId,
    PrivateKey,
    AccountBalanceQuery,
)

from config import HEDERA_ACCOUNT_ID, HEDERA_PRIVATE_KEY, HEDERA_NETWORK

def main():
    if not HEDERA_ACCOUNT_ID or not HEDERA_PRIVATE_KEY:
        print("Missing HEDERA_ACCOUNT_ID or HEDERA_PRIVATE_KEY in environment variables.")
        return

    try:
        # Load credentials from environment
        account_id  = AccountId.from_string(HEDERA_ACCOUNT_ID)
        private_key = PrivateKey.from_string(HEDERA_PRIVATE_KEY)

        # Connect to testnet
        if HEDERA_NETWORK == "mainnet":
            client = Client.for_mainnet()
        else:
            client = Client.for_testnet()

        client.set_operator(account_id, private_key)

        # Query balance
        balance = AccountBalanceQuery().set_account_id(account_id).execute(client)
        print(f"HBAR Balance: {balance.hbars}")
    except Exception as e:
        print(f"Error connecting to Hedera: {e}")

if __name__ == "__main__":
    main()
