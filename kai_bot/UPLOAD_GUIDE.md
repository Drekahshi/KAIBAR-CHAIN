# KAI Ecosystem Bot — Antigravity IDE Upload & Installation Guide

---

## PART 1 — UPLOAD FILE ORDER

Upload files in this exact sequence so all imports resolve correctly
before the entry point runs.

### Round 1 — Root Config Files (upload first)
```
requirements.txt
.env.example
config.py
logger.py
```

### Round 2 — Utilities
```
utils/__init__.py
utils/helpers.py
```

### Round 3 — Modules (any order within this group)
```
modules/__init__.py
modules/wallet_registry.py
modules/tokenomics.py
modules/airdrop_engine.py
modules/amm_monitor.py
modules/vault_monitor.py
modules/scheduler.py
modules/qr_generator.py
modules/payments.py
```

### Round 4 — Storage
```
storage/wallets.json
```

### Round 5 — Entry Point (upload last)
```
bot.py
```

### Reference Files (optional, upload anytime)
```
SKILL.md
project.json
```

---

## PART 2 — ENVIRONMENT VARIABLES

In the Antigravity IDE environment panel, set these variables before
running the bot. Never paste private keys into code files.

| Variable               | Value                         | Required |
|------------------------|-------------------------------|----------|
| HEDERA_ACCOUNT_ID      | Your account e.g. 0.0.XXXXX  | Yes      |
| HEDERA_PRIVATE_KEY     | Your DER-encoded private key  | Yes      |
| HEDERA_NETWORK         | testnet  or  mainnet          | Yes      |
| ANTHROPIC_API_KEY      | Claude API key (agent kit)    | Optional |
| OPENAI_API_KEY         | OpenAI key (agent kit)        | Optional |
| GROQ_API_KEY           | Groq key for Llama (agent kit)| Optional |
| MPESA_CONSUMER_KEY     | Safaricom Daraja key          | Optional |
| MPESA_CONSUMER_SECRET  | Safaricom Daraja secret       | Optional |
| MPESA_SHORTCODE        | Your M-Pesa shortcode         | Optional |
| MPESA_PASSKEY          | Your M-Pesa passkey           | Optional |
| MPESA_CALLBACK_URL     | Your callback endpoint        | Optional |

> M-Pesa and AI agent variables are optional for the MVP.
> The bot runs in simulation mode without them.

---

## PART 3 — INSTALL BASE DEPENDENCIES

Open the Antigravity IDE terminal and run:

```bash
pip install -r requirements.txt
```

The base requirements.txt covers:

```
python-dotenv>=1.0.0
requests>=2.31.0
qrcode[pil]>=7.4.2
Pillow>=10.0.0
```

---

## PART 4 — INSTALL HEDERA SDK (hiero-sdk-python)

The official Hedera Python SDK is now maintained under the name
**hiero-sdk-python**. This is the package that lets your bot read
balances, transfer tokens, and submit transactions on Hedera Hashgraph.

### Install

```bash
pip install hiero-sdk-python
```

Current stable version: **0.2.1**

### What it gives you

| Feature                      | Class / Method                          |
|------------------------------|-----------------------------------------|
| Connect to network           | `Client.for_testnet()`                  |
| Query HBAR balance           | `AccountBalanceQuery`                   |
| Transfer HBAR                | `TransferTransaction`                   |
| Transfer HTS tokens          | `TransferTransaction` with token ID     |
| Create HTS token             | `TokenCreateTransaction`                |
| Mint tokens                  | `TokenMintTransaction`                  |
| Associate token to account   | `TokenAssociateTransaction`             |
| Schedule a transaction       | `ScheduleCreateTransaction`             |
| Query mirror node            | REST calls to mirror node REST API      |

### Basic connection test

Create a file `test_hedera.py` in your IDE and run it to confirm
the SDK is working:

```python
import os
from hiero import (
    Client,
    AccountId,
    PrivateKey,
    AccountBalanceQuery,
)

# Load credentials from environment
account_id  = AccountId.from_string(os.getenv("HEDERA_ACCOUNT_ID"))
private_key = PrivateKey.from_string(os.getenv("HEDERA_PRIVATE_KEY"))

# Connect to testnet
client = Client.for_testnet()
client.set_operator(account_id, private_key)

# Query balance
balance = AccountBalanceQuery().set_account_id(account_id).execute(client)
print(f"HBAR Balance: {balance.hbars}")
```

Run it:
```bash
python test_hedera.py
```

Expected output:
```
HBAR Balance: 100 ℏ
```

### HBAR Transfer example

```python
from hiero import TransferTransaction, Hbar

tx = (
    TransferTransaction()
    .add_hbar_transfer(sender_account_id, Hbar.from_tinybars(-100))
    .add_hbar_transfer(recipient_account_id, Hbar.from_tinybars(100))
    .execute(client)
)
receipt = tx.get_receipt(client)
print(f"Transfer status: {receipt.status}")
```

### HTS Token Transfer example

```python
from hiero import TransferTransaction, TokenId

token_id = TokenId.from_string("0.0.YOUR_TOKEN_ID")

tx = (
    TransferTransaction()
    .add_token_transfer(token_id, sender_id, -10)
    .add_token_transfer(token_id, recipient_id, 10)
    .execute(client)
)
receipt = tx.get_receipt(client)
print(f"Token transfer: {receipt.status}")
```

### Scheduled Transaction example (for pensions / trusts)

```python
from hiero import (
    ScheduleCreateTransaction,
    TransferTransaction,
    Hbar,
)

# Build the inner transaction
inner_tx = (
    TransferTransaction()
    .add_hbar_transfer(sender_id, Hbar.from_tinybars(-500))
    .add_hbar_transfer(beneficiary_id, Hbar.from_tinybars(500))
)

# Wrap it in a schedule
schedule_tx = (
    ScheduleCreateTransaction()
    .set_scheduled_transaction(inner_tx)
    .set_schedule_memo("Monthly pension payout")
    .execute(client)
)
receipt = schedule_tx.get_receipt(client)
print(f"Schedule ID: {receipt.schedule_id}")
```

---

## PART 5 — INSTALL HEDERA AGENT KIT (Python)

The **hedera-agent-kit** Python package connects your bot to an AI
reasoning layer (LangChain + LangGraph) so it can understand natural
language commands and execute Hedera actions automatically.

It bundles: LangChain, LangGraph, hiero-sdk-python, MCP server support,
and model connectors for Claude (Anthropic), OpenAI, and Groq.

### Install

```bash
pip install hedera-agent-kit
```

Current stable version: **3.2.0**

> This installs a full AI + blockchain stack (~60 packages).
> Allow 2-3 minutes for the complete install on first run.

### Full dependency stack installed automatically

```
hiero-sdk-python==0.1.9      ← Hedera blockchain SDK
langchain==1.2.0              ← AI agent orchestration
langchain-anthropic==1.3.0   ← Claude / Anthropic support
langchain-openai==1.1.6      ← OpenAI / GPT support
langchain-groq==1.1.1        ← Groq / Llama support
langgraph>=1.0.2              ← Agent state machine + memory
mcp==1.25.0                  ← Model Context Protocol server
web3==7.14.0                 ← EVM / smart contract layer
pydantic>=2.12.3             ← Data validation
aiohttp>=3.13.1              ← Async HTTP client
cryptography==44.0.0         ← Key management + signing
grpcio==1.76.0               ← gRPC transport
protobuf==6.33.1             ← Protocol Buffers
```

### Basic agent test

Create `test_agent.py` in your IDE:

```python
import os
import asyncio
from hedera_agent_kit import HederaAgentKit, HederaConversationalAgent

async def main():

    # Initialize the kit with your Hedera credentials
    kit = HederaAgentKit(
        account_id  = os.getenv("HEDERA_ACCOUNT_ID"),
        private_key = os.getenv("HEDERA_PRIVATE_KEY"),
        network     = os.getenv("HEDERA_NETWORK", "testnet"),
    )

    # Create a conversational agent backed by Claude
    agent = HederaConversationalAgent(
        kit          = kit,
        llm_provider = "anthropic",
        api_key      = os.getenv("ANTHROPIC_API_KEY"),
    )

    # Ask it a natural language question
    response = await agent.chat("What is my HBAR balance?")
    print(response)

asyncio.run(main())
```

Run it:
```bash
python test_agent.py
```

Expected output:
```
Your current HBAR balance is 100 ℏ on the Hedera Testnet.
```

### Switching AI model providers

```python
# Use Claude (Anthropic)
agent = HederaConversationalAgent(
    kit=kit,
    llm_provider="anthropic",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

# Use GPT-4 (OpenAI)
agent = HederaConversationalAgent(
    kit=kit,
    llm_provider="openai",
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Use Llama via Groq (free tier available)
agent = HederaConversationalAgent(
    kit=kit,
    llm_provider="groq",
    api_key=os.getenv("GROQ_API_KEY"),
)
```

### Natural language commands the agent understands

Once connected, users can type these directly into your KAI bot:

```
"What is my HBAR balance?"
"Transfer 10 HBAR to 0.0.99999"
"Create a new token called KAI with supply 21 billion"
"Mint 1000 KAI tokens to my account"
"Schedule a pension payment of 500 HBAR to 0.0.88888 in 30 days"
"Show vault APY performance"
"Check the HBAR/USDC liquidity pool"
"Create a trust fund wallet for 0.0.77777"
```

### Connecting the agent to your KAI bot

Add this block to `bot.py` so users can type free-text AI commands
using the `ask` prefix:

```python
# ── Add at the top of bot.py ──────────────────────────────────────
import asyncio
from hedera_agent_kit import HederaAgentKit, HederaConversationalAgent

# ── Initialize once in the run() function ────────────────────────
kit = HederaAgentKit(
    account_id  = os.getenv("HEDERA_ACCOUNT_ID"),
    private_key = os.getenv("HEDERA_PRIVATE_KEY"),
    network     = os.getenv("HEDERA_NETWORK", "testnet"),
)


# ── Add this in the command loop BEFORE the unknown command block ─
elif cmd.startswith("ask "):
    question = cmd[4:].strip()
    print(f"\n  Processing: {question}")
    response = asyncio.run(agent.chat(question))
    print(f"\n  AI ▶  {response}\n")
```

Users then type:
```
KAI ▶  ask What is my current vault yield?
KAI ▶  ask Transfer 50 HBAR to 0.0.55555
KAI ▶  ask Schedule a trust payout of 200 HBAR in 7 days
```

---

## PART 6 — UPDATED requirements.txt

After installing both SDKs, your full `requirements.txt` should be:

```
# Base bot dependencies
python-dotenv>=1.0.0
requests>=2.31.0
qrcode[pil]>=7.4.2
Pillow>=10.0.0

# Hedera Blockchain SDK
hiero-sdk-python>=0.2.1

# Hedera AI Agent Kit
# (includes LangChain, LangGraph, MCP, web3, cryptography)
hedera-agent-kit>=3.2.0
```

Install all at once:
```bash
pip install -r requirements.txt
```

---

## PART 7 — RUN THE BOT

```bash
python bot.py
```

You should see:

```
  ╔══════════════════════════════════════════════════════╗
  ║          KAI ECOSYSTEM OPERATIONS BOT               ║
  ║          Powered by Hedera Hashgraph                 ║
  ╚══════════════════════════════════════════════════════╝

  KAI ▶
```

---

## PART 8 — VERIFY EVERYTHING WORKS

### Step 1 — Test base bot commands
```
help          → command menu loads
tokenomics    → token supply report displays
vaults        → vault APY overview displays
amm           → pool overview displays
wallet        → register 0.0.12345
wallets       → see it listed
airdrop       → confirm + distribute
schedule      → type: pension, amount: 1000, delay: 24
scheduled     → see it listed
qr            → address: 0.0.12345, amount: 100
dashboard     → full ecosystem overview
logs          → all events logged
```

### Step 2 — Test Hedera SDK
```bash
python test_hedera.py
```
Expected: HBAR balance printed without errors.

### Step 3 — Test AI Agent Kit
```bash
python test_agent.py
```
Expected: Natural language balance response from the AI.

### Step 4 — Test agent inside bot
```
KAI ▶  ask What is my HBAR balance?
```
Expected: AI queries Hedera and responds in plain English.

---

## PART 9 — FOLDER STRUCTURE (FINAL)

```
kai_bot/
│
├── bot.py                       ← ENTRY POINT
├── config.py                    ← settings + env loader
├── logger.py                    ← append-only log writer
├── requirements.txt             ← all pip dependencies
├── .env.example                 ← copy to .env, fill credentials
├── project.json                 ← Antigravity IDE manifest
├── SKILL.md                     ← developer architecture guide
├── UPLOAD_GUIDE.md              ← this file
├── test_hedera.py               ← SDK connection test
├── test_agent.py                ← Agent kit test
│
├── modules/
│   ├── __init__.py
│   ├── wallet_registry.py       ← wallet add/list/remove
│   ├── tokenomics.py            ← supply analytics
│   ├── airdrop_engine.py        ← daily token distribution
│   ├── amm_monitor.py           ← AMM pool health
│   ├── vault_monitor.py         ← vault APY tracking
│   ├── scheduler.py             ← pension/trust/insurance
│   ├── qr_generator.py          ← QR payment codes
│   └── payments.py              ← M-Pesa + x402
│
├── utils/
│   ├── __init__.py
│   └── helpers.py               ← shared validation + formatting
│
└── storage/
    ├── wallets.json             ← registered wallet addresses
    ├── airdrop_history.json     ← auto-created on first airdrop
    ├── scheduled_transactions.json ← auto-created on first schedule
    └── logs.txt                 ← auto-created on first run
```

---

## PART 10 — TROUBLESHOOTING

| Problem                                  | Fix                                                          |
|------------------------------------------|--------------------------------------------------------------|
| `ModuleNotFoundError: hiero`             | `pip install hiero-sdk-python`                               |
| `ModuleNotFoundError: hedera_agent_kit`  | `pip install hedera-agent-kit`                               |
| `ModuleNotFoundError: langchain`         | `pip install hedera-agent-kit` (includes it)                 |
| Agent kit install takes long             | Normal — ~60 packages, wait 3 minutes                        |
| `HEDERA_ACCOUNT_ID not set`              | Add env vars in Antigravity IDE environment panel            |
| `Invalid private key format`             | Use DER hex format from portal.hedera.com, not PEM           |
| `ModuleNotFoundError: qrcode`            | `pip install qrcode pillow`                                  |
| `ModuleNotFoundError: dotenv`            | `pip install python-dotenv`                                  |
| M-Pesa returns simulation mode           | Add MPESA_* env vars in IDE settings                         |
| Agent says "API key not found"           | Set ANTHROPIC_API_KEY or OPENAI_API_KEY in env panel         |
| `storage/` path error                    | Create the `storage/` folder manually in the IDE             |
| gRPC error on connect                    | Check HEDERA_NETWORK is set to `testnet` or `mainnet`        |
| Agent times out                          | Check internet access is enabled in Antigravity IDE settings |

---

## PART 11 — WHERE TO GET CREDENTIALS

| Credential          | Where to get it                                           |
|---------------------|-----------------------------------------------------------|
|  i will give you Hedera Account ID   | portal.hedera.com → create testnet account (free)         |
| Hedera Private Key  | portal.hedera.com → shown on        |
|   |  section                  |
| Openrouter API Key      | platform.openrouter.com → API Keys section                    |
|          |
| M-Pesa Keys         | developer.safaricom.co.ke → create a Daraja app           |