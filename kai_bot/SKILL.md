---
description: Developer Architecture Guide for KAI Ecosystem Bot
---

# KAI Ecosystem Bot Architecture

This Document outlines the architecture for the KAI Ecosystem Bot. 
Follow UPLOAD_GUIDE.md to run and interact with the bot.

## Main Scripts
- `bot.py`: Primary entry point. Handles the REPL interface and command routing.
- `logger.py`: Global append-only logger writing to `storage/logs.txt`.
- `config.py`: Configuration and environment definitions.

## Modules (`/modules`)
Isolated business logic functionality:
- `wallet_registry.py`: Manage local JSON store of wallet IDs.
- `tokenomics.py`: Display token supplies.
- `airdrop_engine.py`: Emulate distribution to wallets.
- `amm_monitor.py` & `vault_monitor.py`: Example analytics queries.
- `scheduler.py`: Example scheduled transactions logic.
- `qr_generator.py`: Example generating Hedera payment URIs.
- `payments.py`: Additional custom payment protocols (x402).

## Next steps
Review `bot.py` interactive loop. Add `.env` config, and use `python bot.py` to test.
