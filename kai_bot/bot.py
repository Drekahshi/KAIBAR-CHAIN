import os
import sys
import asyncio

# Setup storage directory first
os.makedirs("storage", exist_ok=True)
if not os.path.exists("storage/wallets.json"):
    with open("storage/wallets.json", "w") as f:
        f.write("[]")

# Import internally
from logger import log_event, log_error
from config import HEDERA_ACCOUNT_ID, HEDERA_PRIVATE_KEY, HEDERA_NETWORK, ANTHROPIC_API_KEY, OPENROUTER_API_KEY
from modules.wallet_registry import register_wallet, list_wallets, remove_wallet
from modules.tokenomics import print_tokenomics
from modules.airdrop_engine import distribute_airdrop
from modules.amm_monitor import print_pool_overview
from modules.vault_monitor import print_vaults_overview
from modules.scheduler import list_scheduled, schedule_transaction
from modules.qr_generator import generate_qr

try:
    from hedera_agent_kit import HederaAgentKit, HederaConversationalAgent
    AGENT_KIT_INSTALLED = True
except ImportError:
    AGENT_KIT_INSTALLED = False

def print_banner():
    print("  ╔══════════════════════════════════════════════════════╗")
    print("  ║          KAI ECOSYSTEM OPERATIONS BOT                ║")
    print("  ║          Powered by Hedera Hashgraph                 ║")
    print("  ╚══════════════════════════════════════════════════════╝\n")

def print_help():
    print("Commands:")
    print("  help          - show this menu")
    print("  tokenomics    - token supply report displays")
    print("  vaults        - vault APY overview displays")
    print("  amm           - AMM pool overview displays")
    print("  wallet        - register a wallet e.g., 'wallet 0.0.12345'")
    print("  wallets       - see all registered wallets")
    print("  airdrop       - distribute to registered wallets")
    print("  schedule      - create a new schedule e.g., 'schedule pension 1000 24'")
    print("  scheduled     - list all scheduled transactions")
    print("  qr            - generate QR code for payment e.g., 'qr 0.0.12345 100'")
    print("  ask [query]   - ask the Hedera AI Agent (Requires setup)")
    print("  exit          - close the application")
    print()

async def interactive_loop():
    print_banner()
    print_help()
    
    # Initialize Agent if possible
    agent = None
    if AGENT_KIT_INSTALLED and HEDERA_ACCOUNT_ID and HEDERA_PRIVATE_KEY:
        try:
            kit = HederaAgentKit(
                account_id=HEDERA_ACCOUNT_ID,
                private_key=HEDERA_PRIVATE_KEY,
                network=HEDERA_NETWORK
            )
            
            if ANTHROPIC_API_KEY:
                agent = HederaConversationalAgent(
                    kit=kit,
                    llm_provider="anthropic",
                    api_key=ANTHROPIC_API_KEY
                )
                log_event("Hedera Agent initialized successfully with Anthropic.")
            elif OPENROUTER_API_KEY:
                os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
                agent = HederaConversationalAgent(
                    kit=kit,
                    llm_provider="openai",
                    api_key=OPENROUTER_API_KEY
                )
                log_event("Hedera Agent initialized successfully with OpenRouter (via OpenAI provider).")
            else:
                log_error("No AI API Key provided (Anthropic or OpenRouter). Agent disabled.")
        except Exception as e:
            log_error(f"Failed to intialize Agent: {e}")
    
    while True:
        try:
            cmd_input = input("  KAI ▶  ").strip()
            if not cmd_input:
                continue
            
            parts = cmd_input.split()
            cmd = parts[0].lower()

            if cmd == "exit":
                print("Exiting...")
                break
            elif cmd == "help":
                print_help()
            elif cmd == "tokenomics":
                print_tokenomics()
            elif cmd == "vaults":
                print_vaults_overview()
            elif cmd == "amm":
                print_pool_overview()
            elif cmd == "wallet":
                if len(parts) >= 2:
                    wallet_id = parts[1]
                    if register_wallet(wallet_id):
                        print(f"Registered {wallet_id}")
                    else:
                        print(f"Wallet {wallet_id} already exists.")
                else:
                    print("Usage: wallet [account_id]")
            elif cmd == "wallets":
                wallets = list_wallets()
                print("\n--- Registered Wallets ---")
                for w in wallets:
                    print(w)
                print(f"Total: {len(wallets)}")
                print("--------------------------\n")
            elif cmd == "airdrop":
                print("Distributing airdrop...")
                amount = 100 # default
                wallets = list_wallets()
                distribute_airdrop(wallets, amount)
            elif cmd == "schedule":
                if len(parts) >= 4:
                    tx_type, amount, delay = parts[1], parts[2], parts[3]
                    schedule_transaction(tx_type, amount, delay)
                else:
                    print("Usage: schedule [type] [amount] [delay_hours]")
            elif cmd == "scheduled":
                list_scheduled()
            elif cmd == "qr":
                if len(parts) >= 3:
                    generate_qr(parts[1], parts[2])
                else:
                    print("Usage: qr [address] [amount]")
            elif cmd == "ask":
                if not agent:
                    print("Agent is not configured. Check your env variables and dependencies.")
                else:
                    question = cmd_input[4:].strip()
                    print(f"\n  Processing: {question}")
                    response = await agent.chat(question)
                    print(f"\n  AI ▶  {response}\n")
            else:
                print(f"Unknown command: {cmd}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            log_error(str(e))
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(interactive_loop())
