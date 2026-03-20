# KAI Bot

**KAI Ecosystem Operations Bot** — a command-line interface for the KAI Chain / Hedera Hashgraph ecosystem.

## Features

- Wallet registry (register, list, remove Hedera accounts)
- Tokenomics report (all 6 KAI tokens: KAI, YT, YBOB, YGOLD, KAI_CENTS, GAMI)
- AMM liquidity pool monitor
- Vault & yield monitor (9 DeFi vaults)
- Airdrop distribution engine
- Transaction scheduler
- QR code payment generator
- M-Pesa STK push (simulation)
- Hedera AI agent (`ask` command)
- Ecosystem dashboard

## Installation

### Method 1 — Run directly (no install needed)
```bash
cd kai_bot
python kai_bot.py
```

### Method 2 — Install as CLI tool
```bash
cd kai_bot
pip install -e .
```
Then run from anywhere:
```bash
kai
```

### With optional extras
```bash
pip install -e ".[ai,qr]"   # AI agent + QR code support
pip install -e ".[all]"     # everything
```

## Configuration

Create a `.env` file in the same directory as `kai_bot.py`:

```env
HEDERA_ACCOUNT_ID=0.0.XXXXX
HEDERA_PRIVATE_KEY=<your-DER-encoded-private-key>
HEDERA_NETWORK=testnet

# Optional — AI agent
OPENROUTER_API_KEY=sk-or-...
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...

# Optional — M-Pesa
MPESA_CONSUMER_KEY=...
MPESA_CONSUMER_SECRET=...
MPESA_SHORTCODE=...
MPESA_PASSKEY=...
MPESA_CALLBACK_URL=https://your-server.com/callback
```

## Commands

| Command | Description |
|---|---|
| `help` | Show all commands |
| `tokenomics` / `tokens` | Full tokenomics report |
| `amm` | AMM pool rates |
| `vaults` | Vault APY overview |
| `dashboard` | Ecosystem summary |
| `wallet <id>` | Register a wallet |
| `wallets` | List registered wallets |
| `remove <id>` | Remove a wallet |
| `airdrop [amount]` | Distribute KAI (default 100) |
| `schedule <type> <amount> <hours>` | Schedule a transaction |
| `scheduled` | List scheduled transactions |
| `qr <address> <amount>` | Generate QR payment code |
| `mpesa <phone> <amount>` | Simulate M-Pesa push |
| `logs [n]` | Print last n log entries |
| `ask <question>` | Query the Hedera AI agent |
| `exit` | Quit |

## Project Structure

```
kai_bot/
├── kai_bot.py          # Main entry point + interactive loop
├── pyproject.toml      # Package config (pip install -e .)
├── README.md
├── .env                # Your credentials (not committed)
├── storage/            # Auto-created at runtime
│   ├── wallets.json
│   ├── logs.txt
│   ├── airdrop_history.json
│   ├── scheduled_transactions.json
│   └── qrcodes/
└── modules/
    ├── airdrop_engine.py
    ├── amm_monitor.py
    ├── tokenomics.py
    ├── vault_monitor.py
    ├── scheduler.py
    ├── wallet_registry.py
    ├── payments.py
    └── qr_generator.py
```
