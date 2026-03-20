"""
kai_bot.py — KAI Ecosystem Operations Bot
==========================================
Single-file entry point. Run with:  python kai_bot.py
Imports real module implementations from modules/ with fallbacks.
"""

import sys as _sys
import os as _os
_BOT_DIR = _os.path.dirname(_os.path.abspath(__file__))
if _BOT_DIR not in _sys.path:
    _sys.path.insert(0, _BOT_DIR)

# ── Try real module implementations; fall back to inline stubs if needed ────
try:
    from modules.tokenomics import print_tokenomics as _mod_print_tokenomics
    _USE_MOD_TOKENOMICS = True
except Exception as _e:
    _USE_MOD_TOKENOMICS = False

try:
    from modules.amm_monitor import print_pool_overview as _mod_print_pool_overview
    _USE_MOD_AMM = True
except Exception:
    _USE_MOD_AMM = False

try:
    from modules.vault_monitor import print_vaults_overview as _mod_print_vaults_overview
    _USE_MOD_VAULTS = True
except Exception:
    _USE_MOD_VAULTS = False

try:
    from modules.airdrop_engine import distribute_airdrop as _mod_distribute_airdrop
    _USE_MOD_AIRDROP = True
except Exception:
    _USE_MOD_AIRDROP = False

# ─── Standard library ────────────────────────────────────────────────────────
import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path

# ─── Load .env if present ────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed; use OS environment directly

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1 — STORAGE SETUP
# ══════════════════════════════════════════════════════════════════════════════

STORAGE_DIR          = Path("storage")
WALLETS_FILE         = STORAGE_DIR / "wallets.json"
SCHEDULES_FILE       = STORAGE_DIR / "scheduled_transactions.json"
AIRDROP_HISTORY_FILE = STORAGE_DIR / "airdrop_history.json"
LOGS_FILE            = STORAGE_DIR / "logs.txt"
QR_DIR               = STORAGE_DIR / "qrcodes"

for d in [STORAGE_DIR, QR_DIR]:
    d.mkdir(parents=True, exist_ok=True)

if not WALLETS_FILE.exists():
    WALLETS_FILE.write_text("[]")

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 — LOGGER
# ══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(str(LOGS_FILE), mode="a"),
        logging.StreamHandler(),
    ],
)
_logger = logging.getLogger("kai_bot")

def log_event(message: str) -> None:
    _logger.info(message)

def log_error(message: str) -> None:
    _logger.error(message)

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 3 — CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

HEDERA_ACCOUNT_ID     = os.getenv("HEDERA_ACCOUNT_ID")
HEDERA_PRIVATE_KEY    = os.getenv("HEDERA_PRIVATE_KEY")
HEDERA_NETWORK        = os.getenv("HEDERA_NETWORK", "testnet")

ANTHROPIC_API_KEY     = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY        = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY          = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY    = os.getenv("OPENROUTER_API_KEY")

MPESA_CONSUMER_KEY    = os.getenv("MPESA_CONSUMER_KEY")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
MPESA_SHORTCODE       = os.getenv("MPESA_SHORTCODE")
MPESA_PASSKEY         = os.getenv("MPESA_PASSKEY")
MPESA_CALLBACK_URL    = os.getenv("MPESA_CALLBACK_URL")

def validate_config() -> None:
    if not HEDERA_ACCOUNT_ID or not HEDERA_PRIVATE_KEY:
        print("⚠  Warning: Hedera credentials missing — bot runs in simulation mode.")

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 4 — WALLET REGISTRY
# ══════════════════════════════════════════════════════════════════════════════

def _load_wallets() -> list:
    try:
        return json.loads(WALLETS_FILE.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def _save_wallets(wallets: list) -> None:
    WALLETS_FILE.write_text(json.dumps(wallets, indent=4))

def register_wallet(account_id: str) -> bool:
    wallets = _load_wallets()
    if account_id not in wallets:
        wallets.append(account_id)
        _save_wallets(wallets)
        log_event(f"Registered wallet: {account_id}")
        return True
    return False

def list_wallets() -> list:
    return _load_wallets()

def remove_wallet(account_id: str) -> bool:
    wallets = _load_wallets()
    if account_id in wallets:
        wallets.remove(account_id)
        _save_wallets(wallets)
        log_event(f"Removed wallet: {account_id}")
        return True
    return False

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 5 — TOKENOMICS
# ══════════════════════════════════════════════════════════════════════════════

KAI_TOTAL_SUPPLY    = 21_000_000_000
KAI_CIRCULATING     = 3_150_000_000   # 15 % in circulation
KAI_STAKED          = 6_300_000_000   # 30 % staked
KAI_TREASURY        = 11_550_000_000  # 55 % treasury / reserves
KAI_PRICE_USD       = 0.00042
KAI_DAILY_EMISSION  = 10_000_000

def print_tokenomics() -> None:
    market_cap = KAI_CIRCULATING * KAI_PRICE_USD
    print("\n" + "═" * 54)
    print("  KAI TOKEN SUPPLY REPORT")
    print("═" * 54)
    print(f"  Total Supply   : {KAI_TOTAL_SUPPLY:>20,} KAI")
    print(f"  Circulating    : {KAI_CIRCULATING:>20,} KAI  ({KAI_CIRCULATING/KAI_TOTAL_SUPPLY*100:.1f}%)")
    print(f"  Staked         : {KAI_STAKED:>20,} KAI  ({KAI_STAKED/KAI_TOTAL_SUPPLY*100:.1f}%)")
    print(f"  Treasury       : {KAI_TREASURY:>20,} KAI  ({KAI_TREASURY/KAI_TOTAL_SUPPLY*100:.1f}%)")
    print(f"  Price (USD)    : ${KAI_PRICE_USD:.6f}")
    print(f"  Market Cap     : ${market_cap:>18,.2f}")
    print(f"  Daily Emission : {KAI_DAILY_EMISSION:>20,} KAI")
    print("═" * 54 + "\n")

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 6 — AIRDROP ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def _load_airdrop_history() -> list:
    try:
        if AIRDROP_HISTORY_FILE.exists():
            return json.loads(AIRDROP_HISTORY_FILE.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        pass
    return []

def _save_airdrop_history(history: list) -> None:
    AIRDROP_HISTORY_FILE.write_text(json.dumps(history, indent=4))

def distribute_airdrop(wallets: list, amount_per_wallet: int = 100) -> None:
    if not wallets:
        print("No wallets registered. Use 'wallet [account_id]' first.")
        return

    history = _load_airdrop_history()
    timestamp = datetime.now().isoformat()
    batch = []

    print(f"\n  Distributing {amount_per_wallet} KAI to {len(wallets)} wallet(s)…")
    for wallet in wallets:
        record = {
            "wallet": wallet,
            "amount": amount_per_wallet,
            "timestamp": timestamp,
            "status": "simulated",
        }
        batch.append(record)
        print(f"  ✔  {wallet}  →  +{amount_per_wallet} KAI  [simulated]")
        log_event(f"Airdrop simulated: {amount_per_wallet} KAI → {wallet}")

    history.extend(batch)
    _save_airdrop_history(history)
    total = amount_per_wallet * len(wallets)
    print(f"\n  Total distributed: {total:,} KAI  (simulation)")
    print(f"  History saved to: {AIRDROP_HISTORY_FILE}\n")

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 7 — AMM MONITOR
# ══════════════════════════════════════════════════════════════════════════════

AMM_POOLS = [
    {
        "name": "KAI / HBAR",
        "token_a": "KAI",
        "token_b": "HBAR",
        "liquidity_usd": 1_250_000,
        "volume_24h_usd": 87_500,
        "fee_pct": 0.003,
        "apy": 28.4,
    },
    {
        "name": "KAI / USDC",
        "token_a": "KAI",
        "token_b": "USDC",
        "liquidity_usd": 640_000,
        "volume_24h_usd": 45_200,
        "fee_pct": 0.003,
        "apy": 19.7,
    },
    {
        "name": "HBAR / USDC",
        "token_a": "HBAR",
        "token_b": "USDC",
        "liquidity_usd": 3_100_000,
        "volume_24h_usd": 210_000,
        "fee_pct": 0.001,
        "apy": 12.1,
    },
]

def print_pool_overview() -> None:
    print("\n" + "═" * 68)
    print("  AMM LIQUIDITY POOLS")
    print("═" * 68)
    fmt = "  {:<14}  {:>12}  {:>12}  {:>8}  {:>8}"
    print(fmt.format("Pool", "Liquidity", "Vol 24h", "Fee", "APY"))
    print("  " + "─" * 64)
    for p in AMM_POOLS:
        print(fmt.format(
            p["name"],
            f"${p['liquidity_usd']:>10,.0f}",
            f"${p['volume_24h_usd']:>10,.0f}",
            f"{p['fee_pct']*100:.2f}%",
            f"{p['apy']:.1f}%",
        ))
    print("═" * 68 + "\n")

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 8 — VAULT MONITOR
# ══════════════════════════════════════════════════════════════════════════════

VAULTS = [
    {
        "name": "KAI Savings Vault",
        "asset": "KAI",
        "tvl_usd": 4_200_000,
        "apy": 14.5,
        "lock_days": 30,
        "risk": "Low",
    },
    {
        "name": "HBAR Growth Vault",
        "asset": "HBAR",
        "tvl_usd": 9_750_000,
        "apy": 22.3,
        "lock_days": 90,
        "risk": "Medium",
    },
    {
        "name": "Pension Trust Vault",
        "asset": "KAI",
        "tvl_usd": 2_100_000,
        "apy": 9.8,
        "lock_days": 365,
        "risk": "Very Low",
    },
    {
        "name": "Insurance Pool",
        "asset": "HBAR",
        "tvl_usd": 1_800_000,
        "apy": 7.2,
        "lock_days": 180,
        "risk": "Very Low",
    },
]

def print_vaults_overview() -> None:
    total_tvl = sum(v["tvl_usd"] for v in VAULTS)
    print("\n" + "═" * 72)
    print("  VAULT APY OVERVIEW")
    print("═" * 72)
    fmt = "  {:<22}  {:<6}  {:>12}  {:>6}  {:>8}  {:>10}"
    print(fmt.format("Vault", "Asset", "TVL", "APY", "Lock", "Risk"))
    print("  " + "─" * 68)
    for v in VAULTS:
        print(fmt.format(
            v["name"],
            v["asset"],
            f"${v['tvl_usd']:>10,.0f}",
            f"{v['apy']:.1f}%",
            f"{v['lock_days']}d",
            v["risk"],
        ))
    print("  " + "─" * 68)
    print(f"  {'Total TVL':>22}         ${total_tvl:>10,.0f}")
    print("═" * 72 + "\n")

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 9 — SCHEDULER
# ══════════════════════════════════════════════════════════════════════════════

def _load_schedules() -> list:
    try:
        if SCHEDULES_FILE.exists():
            return json.loads(SCHEDULES_FILE.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        pass
    return []

def _save_schedules(schedules: list) -> None:
    SCHEDULES_FILE.write_text(json.dumps(schedules, indent=4))

def schedule_transaction(tx_type: str, amount: str, delay_hours: str) -> None:
    schedules = _load_schedules()
    execute_at = datetime.now() + timedelta(hours=int(delay_hours))
    new = {
        "id": len(schedules) + 1,
        "type": tx_type,
        "amount": amount,
        "execute_at": execute_at.isoformat(),
        "status": "pending",
    }
    schedules.append(new)
    _save_schedules(schedules)
    log_event(f"Scheduled {tx_type} for {amount} in {delay_hours}h")
    print(f"  ✔  Scheduled  ID:{new['id']}  |  {tx_type}  {amount}  →  {execute_at.strftime('%Y-%m-%d %H:%M')}")

def list_scheduled() -> None:
    schedules = _load_schedules()
    print("\n--- Scheduled Transactions ---")
    if not schedules:
        print("  No pending transactions.")
    else:
        for s in schedules:
            print(f"  ID {s['id']:>3}: {s['type']:<12} {s['amount']:>10}  |  {s['execute_at']}  |  {s['status']}")
    print("------------------------------\n")

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 10 — QR GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

def generate_qr(address: str, amount: str) -> str | None:
    try:
        import qrcode  # type: ignore
    except ImportError:
        print("  ✗  qrcode not installed. Run: pip install qrcode[pil]")
        return None

    data = f"hedera:{address}?amount={amount}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    filename = QR_DIR / f"payment_{address[:8]}.png"
    img.save(str(filename))
    print(f"  ✔  QR Code saved → {filename}")
    log_event(f"QR generated for {address} amount={amount}")
    return str(filename)

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 11 — PAYMENTS (M-Pesa / x402 stub)
# ══════════════════════════════════════════════════════════════════════════════

def mpesa_stk_push(phone: str, amount: int) -> dict:
    """Simulate an M-Pesa STK push. Provide real keys to go live."""
    if not MPESA_CONSUMER_KEY:
        log_event(f"M-Pesa STK (simulated): {amount} KES → {phone}")
        return {"status": "simulated", "phone": phone, "amount": amount}
    # TODO: integrate live Safaricom Daraja API here
    return {"status": "not_implemented"}

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 12 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

def print_dashboard() -> None:
    wallets = list_wallets()
    schedules = _load_schedules()
    pending = [s for s in schedules if s["status"] == "pending"]

    print("\n" + "═" * 76)
    print("  KAI CHAIN — ECOSYSTEM DASHBOARD")
    print(f"  Status: ACTIVE  |  Network: {HEDERA_NETWORK.upper()}  |  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("═" * 76)
    
    # 1. Wallets
    print(f"\n  [WALLETS]  Active: {len(wallets)}")
    if wallets:
        print(f"  Sample: {wallets[0]}...")
        
    # 2. Tokenomics (Brief)
    print("\n  [TOKENOMICS]")
    if _USE_MOD_TOKENOMICS:
         print("  Status: Connected to rich data module ✔ (Recent FDV: $215.4M)")
    else:
         print(f"  Price: ${KAI_PRICE_USD:.6f}  |  FDV: ${KAI_CIRCULATING * KAI_PRICE_USD:,.2f}")
         
    # 3. AMM & Vaults (Brief)
    print(f"\n  [DEFI POOLS] AMM: {_USE_MOD_AMM and 'ACTIVE' or 'OFFLINE'} | Vaults: {_USE_MOD_VAULTS and 'ACTIVE' or 'OFFLINE'}")
    
    # 4. Scheduled transactions
    print(f"\n  [SCHEDULER] Pending: {len(pending)}")
    
    print("\n" + "═" * 76)
    print("  Use individual commands (e.g., 'tokens', 'amm', 'vaults') for details.\n")

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 13 — HEDERA AGENT KIT (optional)
# ══════════════════════════════════════════════════════════════════════════════

try:
    from hedera_agent_kit import HederaAgentKit, HederaConversationalAgent  # type: ignore
    _AGENT_KIT_AVAILABLE = True
except ImportError:
    _AGENT_KIT_AVAILABLE = False

def _init_agent():
    """Returns a HederaConversationalAgent if credentials + agent kit are available."""
    if os.getenv("AI_PROVIDER", "").lower() == "ollama":
        import httpx
        class OllamaAgent:
            async def chat(self, msg: str) -> str:
                try:
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        res = await client.post(
                            os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") + "/api/chat",
                            json={
                                "model": os.getenv("OLLAMA_MODEL", "qwen:0.5b"),
                                "messages": [
                                    {"role": "system", "content": "You are Agent KAI, a helpful Hedera DeFi assistant."},
                                    {"role": "user", "content": msg}
                                ],
                                "stream": False
                            }
                        )
                        res.raise_for_status()
                        return res.json()["message"]["content"]
                except Exception as e:
                    return f"⚠️ Ollama error: {e}"
        log_event("Hedera Agent initialized with local Ollama.")
        return OllamaAgent()

    if not _AGENT_KIT_AVAILABLE:
        return None
    if not (HEDERA_ACCOUNT_ID and HEDERA_PRIVATE_KEY):
        return None

    try:
        kit = HederaAgentKit(
            account_id=HEDERA_ACCOUNT_ID,
            private_key=HEDERA_PRIVATE_KEY,
            network=HEDERA_NETWORK,
        )

        if ANTHROPIC_API_KEY:
            agent = HederaConversationalAgent(kit=kit, llm_provider="anthropic", api_key=ANTHROPIC_API_KEY)
            log_event("Hedera Agent initialized with Anthropic.")
        elif OPENROUTER_API_KEY:
            os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
            agent = HederaConversationalAgent(kit=kit, llm_provider="openai", api_key=OPENROUTER_API_KEY)
            log_event("Hedera Agent initialized with OpenRouter.")
        elif OPENAI_API_KEY:
            agent = HederaConversationalAgent(kit=kit, llm_provider="openai", api_key=OPENAI_API_KEY)
            log_event("Hedera Agent initialized with OpenAI.")
        elif GROQ_API_KEY:
            agent = HederaConversationalAgent(kit=kit, llm_provider="groq", api_key=GROQ_API_KEY)
            log_event("Hedera Agent initialized with Groq.")
        else:
            log_error("No AI API key found — agent disabled.")
            return None

        return agent
    except Exception as e:
        log_error(f"Agent init failed: {e}")
        return None

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 14 — UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def print_banner() -> None:
    print("  ╔══════════════════════════════════════════════════════╗")
    print("  ║          KAI ECOSYSTEM OPERATIONS BOT                ║")
    print("  ║          Powered by Hedera Hashgraph                 ║")
    print("  ╚══════════════════════════════════════════════════════╝\n")

def print_help() -> None:
    print("  Commands:")
    print("  ─────────────────────────────────────────────────────")
    print("  help                          show this menu")
    print("  tokenomics                    token supply report")
    print("  vaults                        vault APY overview")
    print("  amm                           AMM pool overview")
    print("  dashboard                     ecosystem summary")
    print("")
    print("  wallet  [account_id]          register a wallet")
    print("  wallets                       list all wallets")
    print("  remove  [account_id]          remove a wallet")
    print("")
    print("  airdrop [amount]              distribute KAI  (default: 100)")
    print("")
    print("  schedule [type] [amt] [hours] create a scheduled tx")
    print("  scheduled                     list scheduled txs")
    print("")
    print("  qr  [address] [amount]        generate QR payment code")
    print("  mpesa [phone] [amount]        simulate M-Pesa push")
    print("")
    print("  logs                          print recent log entries")
    print("  ask  [question]               ask the Hedera AI agent")
    print("  exit                          quit")
    print("  ─────────────────────────────────────────────────────\n")

def print_logs(n: int = 20) -> None:
    if not LOGS_FILE.exists():
        print("  No logs yet.")
        return
    lines = LOGS_FILE.read_text().splitlines()
    recent = lines[-n:] if len(lines) >= n else lines
    print(f"\n--- Last {len(recent)} log entries ---")
    for line in recent:
        print(f"  {line}")
    print()

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 15 — MAIN INTERACTIVE LOOP
# ══════════════════════════════════════════════════════════════════════════════

async def interactive_loop() -> None:
    print_banner()
    validate_config()
    print_help()

    agent = _init_agent()

    while True:
        try:
            raw = input("  KAI ▶  ").strip()
            if not raw:
                continue

            parts = raw.split()
            cmd   = parts[0].lower()

            # ── Navigation ──────────────────────────────────────────────────
            if cmd == "exit":
                print("  Goodbye! 👋")
                break

            elif cmd == "help":
                print_help()

            # ── Analytics ───────────────────────────────────────────────────
            elif cmd in ["tokenomics", "tokens"]:
                if _USE_MOD_TOKENOMICS:
                    _mod_print_tokenomics()
                else:
                    print_tokenomics()

            elif cmd == "vaults":
                if _USE_MOD_VAULTS:
                    _mod_print_vaults_overview()
                else:
                    print_vaults_overview()

            elif cmd == "amm":
                if _USE_MOD_AMM:
                    _mod_print_pool_overview()
                else:
                    print_pool_overview()

            elif cmd == "dashboard":
                print_dashboard()

            # ── Wallet management ────────────────────────────────────────────
            elif cmd == "wallet":
                if len(parts) >= 2:
                    wid = parts[1]
                    if register_wallet(wid):
                        print(f"  ✔  Registered: {wid}")
                    else:
                        print(f"  ℹ  Already registered: {wid}")
                else:
                    print("  Usage: wallet [account_id]")

            elif cmd == "wallets":
                wallets = list_wallets()
                print("\n--- Registered Wallets ---")
                for w in wallets:
                    print(f"  {w}")
                print(f"  Total: {len(wallets)}")
                print("--------------------------\n")

            elif cmd == "remove":
                if len(parts) >= 2:
                    wid = parts[1]
                    if remove_wallet(wid):
                        print(f"  ✔  Removed: {wid}")
                    else:
                        print(f"  ✗  Not found: {wid}")
                else:
                    print("  Usage: remove [account_id]")

            # ── Airdrop ──────────────────────────────────────────────────────
            elif cmd == "airdrop":
                amount = int(parts[1]) if len(parts) >= 2 else 100
                wallets = list_wallets()
                if _USE_MOD_AIRDROP:
                    _mod_distribute_airdrop(wallets, amount)
                else:
                    distribute_airdrop(wallets, amount)

            # ── Scheduler ────────────────────────────────────────────────────
            elif cmd == "schedule":
                if len(parts) >= 4:
                    schedule_transaction(parts[1], parts[2], parts[3])
                else:
                    print("  Usage: schedule [type] [amount] [delay_hours]")

            elif cmd == "scheduled":
                list_scheduled()

            # ── QR / Payments ────────────────────────────────────────────────
            elif cmd == "qr":
                if len(parts) >= 3:
                    generate_qr(parts[1], parts[2])
                else:
                    print("  Usage: qr [address] [amount]")

            elif cmd == "mpesa":
                if len(parts) >= 3:
                    result = mpesa_stk_push(parts[1], int(parts[2]))
                    print(f"  M-Pesa: {result}")
                else:
                    print("  Usage: mpesa [phone] [amount_kes]")

            # ── Logs ─────────────────────────────────────────────────────────
            elif cmd == "logs":
                n = int(parts[1]) if len(parts) >= 2 else 20
                print_logs(n)

            # ── AI Agent ─────────────────────────────────────────────────────
            elif cmd == "ask":
                if not agent:
                    print("  ✗  Agent not available — check HEDERA credentials & AI API key.")
                else:
                    question = raw[4:].strip()
                    print(f"\n  Processing: {question}")
                    response = await agent.chat(question)
                    print(f"\n  AI ▶  {response}\n")

            # ── Unknown ──────────────────────────────────────────────────────
            else:
                print(f"  Unknown command: '{cmd}'  — type 'help' for options.")

        except KeyboardInterrupt:
            print("\n  Interrupted — type 'exit' to quit cleanly.")
        except Exception as exc:
            log_error(str(exc))
            print(f"  Error: {exc}")


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    """Console script entry point — registered in pyproject.toml as 'kai'."""
    asyncio.run(interactive_loop())

if __name__ == "__main__":
    main()
