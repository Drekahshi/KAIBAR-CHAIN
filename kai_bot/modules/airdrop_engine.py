"""
KAI Chain Airdrop Engine
========================
Tokens: YT, YBOB, YGOLD, KAI_CENTS, GAMI, KAI
Pipeline: load → verify supply → calculate → validate → send → log → repeat
"""

import json
import csv
import time
import hashlib
import logging
import random
import re
import os
from datetime import datetime, date
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import Enum

try:
    from logger import log_event
except ImportError:
    def log_event(msg): print(f"[LOG] {msg}")

# ─────────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────────
LOG_DIR = Path("storage/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "airdrop_engine.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("KAI_AIRDROP")


# ─────────────────────────────────────────────
#  TOKEN REGISTRY
# ─────────────────────────────────────────────
class TokenType(str, Enum):
    YT        = "YT"
    YBOB      = "YBOB"
    YGOLD     = "YGOLD"
    KAI_CENTS = "KAI_CENTS"
    GAMI      = "GAMI"
    KAI       = "KAI"


TOKEN_REGISTRY: dict[str, dict] = {
    TokenType.YT: {
        "name": "YToken Multi-Strategy DeFi Vault", "symbol": "YT",
        "total_supply": 2_100_000_000, "airdrop_pct": 0.02, "decimals": 8,
        "expected_apy": "22-38%",
    },
    TokenType.YBOB: {
        "name": "YBOB Algorithmic Stablecoin", "symbol": "YBOB",
        "total_supply": 500_000_000, "airdrop_pct": 0.05, "decimals": 6,
        "expected_apy": "10-15%",
    },
    TokenType.YGOLD: {
        "name": "YGOLD Bond Vault", "symbol": "YGOLD",
        "total_supply": 8_400_000_000, "airdrop_pct": 0.01, "decimals": 8,
        "expected_apy": "26-55%",
    },
    TokenType.KAI_CENTS: {
        "name": "KAI CENTS-H Utility Token", "symbol": "KAI_CENTS",
        "total_supply": 1_000_000_000, "airdrop_pct": 0.10, "decimals": 4,
        "expected_apy": "16-24%",
    },
    TokenType.GAMI: {
        "name": "GAMI Social DeFi Mining Token", "symbol": "GAMI",
        "total_supply": 10_000_000_000, "airdrop_pct": 0.05, "decimals": 8,
        "expected_apy": "12-22%",
    },
    TokenType.KAI: {
        "name": "KAI Governance DAO Token", "symbol": "KAI",
        "total_supply": 100_000_000, "airdrop_pct": 0.20, "decimals": 8,
        "expected_apy": "N/A (governance)",
    },
}


# ─────────────────────────────────────────────
#  DATA CLASSES
# ─────────────────────────────────────────────
@dataclass
class Wallet:
    address: str
    tier: str = "standard"
    engagement_score: float = 1.0
    kyc_verified: bool = False
    country: str = "KE"
    joined_date: str = ""

    def __post_init__(self):
        if not self.joined_date:
            self.joined_date = date.today().isoformat()


@dataclass
class AirdropRecord:
    wallet:    str
    token:     str
    amount:    float
    tx_hash:   str
    status:    str
    reason:    str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# ─────────────────────────────────────────────
#  SUPPLY MANAGER
# ─────────────────────────────────────────────
class SupplyManager:
    def __init__(self):
        self._budgets:     dict[str, float] = {}
        self._distributed: dict[str, float] = {}
        for symbol, meta in TOKEN_REGISTRY.items():
            budget = meta["total_supply"] * meta["airdrop_pct"]
            self._budgets[symbol]     = budget
            self._distributed[symbol] = 0.0

    def available(self, token: str) -> float:
        return self._budgets.get(token, 0) - self._distributed.get(token, 0)

    def deduct(self, token: str, amount: float) -> bool:
        if self.available(token) < amount:
            return False
        self._distributed[token] += amount
        return True


# ─────────────────────────────────────────────
#  WALLET VALIDATOR
# ─────────────────────────────────────────────
class WalletValidator:
    HEDERA_PATTERN = re.compile(r"^0\.0\.\d{5,10}$")
    BLACKLIST = {"0.0.9999999", "0.0.0000001"}

    def __init__(self):
        self._seen: set[str] = set()
        self._daily_counts: dict[str, int] = {}
        self.DAILY_LIMIT = 500

    def validate(self, wallet: Wallet) -> tuple[bool, str]:
        addr = wallet.address
        if not self.HEDERA_PATTERN.match(addr):
            return False, "Invalid Hedera account-ID format"
        if addr in self.BLACKLIST:
            return False, "Address is blacklisted"
        if addr in self._seen:
            return False, "Duplicate - already received airdrop"
        today = date.today().isoformat()
        self._daily_counts.setdefault(today, 0)
        if self._daily_counts[today] >= self.DAILY_LIMIT:
            return False, f"Daily limit of {self.DAILY_LIMIT} reached"
        return True, "OK"

    def mark_sent(self, address: str):
        self._seen.add(address)
        today = date.today().isoformat()
        self._daily_counts.setdefault(today, 0)
        self._daily_counts[today] += 1

    @property
    def processed(self) -> set[str]:
        return self._seen


# ─────────────────────────────────────────────
#  ALLOCATION CALCULATOR
# ─────────────────────────────────────────────
class AllocationCalculator:
    TIER_MULTIPLIERS = {"whale": 2.0, "early_adopter": 1.5, "standard": 1.0}
    KYC_BONUS = 0.20

    def calculate(self, wallet: Wallet, token: str, total_budget: float, eligible_count: int) -> float:
        if eligible_count == 0:
            return 0.0
        base = total_budget / eligible_count
        multiplier = self.TIER_MULTIPLIERS.get(wallet.tier, 1.0)
        if token == TokenType.GAMI:
            multiplier *= max(0.1, wallet.engagement_score)
        if wallet.kyc_verified:
            multiplier *= (1 + self.KYC_BONUS)
        return round(base * multiplier, TOKEN_REGISTRY[token]["decimals"])


# ─────────────────────────────────────────────
#  MOCK HEDERA CLIENT
# ─────────────────────────────────────────────
class HederaClient:
    SIMULATED_FAILURE_RATE = 0.03

    def transfer(self, to: str, token: str, amount: float) -> tuple[bool, str]:
        time.sleep(random.uniform(0.02, 0.08))
        if random.random() < self.SIMULATED_FAILURE_RATE:
            return False, ""
        raw = f"{to}:{token}:{amount}:{time.time_ns()}"
        tx_hash = "0x" + hashlib.sha256(raw.encode()).hexdigest()
        return True, tx_hash


# ─────────────────────────────────────────────
#  AIRDROP ENGINE
# ─────────────────────────────────────────────
class AirdropEngine:
    def __init__(self, token: str):
        if token not in TOKEN_REGISTRY:
            raise ValueError(f"Unknown token '{token}'. Valid: {list(TOKEN_REGISTRY)}")
        self.token      = token
        self.meta       = TOKEN_REGISTRY[token]
        self.supply_mgr = SupplyManager()
        self.validator  = WalletValidator()
        self.calculator = AllocationCalculator()
        self.client     = HederaClient()

    def run(self, wallets_source: list) -> dict:
        if isinstance(wallets_source, list) and wallets_source and isinstance(wallets_source[0], str):
            wallets = [Wallet(address=a) for a in wallets_source]
        elif isinstance(wallets_source, list):
            wallets = [Wallet(**w) if isinstance(w, dict) else w for w in wallets_source]
        else:
            wallets = []

        budget          = self.supply_mgr.available(self.token)
        eligible_count  = len(wallets)
        stats = {"success": 0, "failed": 0, "skipped": 0, "total_distributed": 0.0}

        for wallet in wallets:
            amount = self.calculator.calculate(wallet, self.token, budget, eligible_count)
            valid, reason = self.validator.validate(wallet)
            if not valid:
                stats["skipped"] += 1
                continue
            if not self.supply_mgr.deduct(self.token, amount):
                break
            success, tx_hash = self.client.transfer(wallet.address, self.token, amount)
            if success:
                self.validator.mark_sent(wallet.address)
                stats["success"] += 1
                stats["total_distributed"] += amount
            else:
                self.supply_mgr._distributed[self.token] -= amount
                stats["failed"] += 1

        return stats


# ─────────────────────────────────────────────
#  SIMPLE BOT-COMPATIBLE WRAPPER
# ─────────────────────────────────────────────
def distribute_airdrop(wallets: list, amount: int = 100) -> bool:
    """Simple airdrop used by the bot CLI."""
    if not wallets:
        print("  No wallets registered. Use 'wallet [account_id]' first.")
        return False

    print(f"\n  Distributing {amount} KAI to {len(wallets)} wallet(s)…")
    for wallet in wallets:
        print(f"  ✔  {wallet}  →  +{amount} KAI  [simulated]")
        log_event(f"Airdrop simulated: {amount} KAI → {wallet}")
    print(f"\n  Total: {amount * len(wallets):,} KAI distributed (simulation)\n")
    return True
