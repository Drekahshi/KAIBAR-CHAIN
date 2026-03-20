"""
routers/airdrop.py — KAIBAR Airdrop management
Whitelist management for token airdrops. Daily airdrop schedule and eligibility.
"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.wallet_registry import list_wallets, register_wallet, remove_wallet
from modules.airdrop_engine import distribute_airdrop
from modules.tokenomics import TOKENS as TOKENOMICS_DATA

router = APIRouter()

# Airdrop config (token → daily amount per whitelisted wallet)
AIRDROP_CONFIG = {
    "YToken": {"daily_amount": 0.1,  "decimals": 8},
    "YGOLD":  {"daily_amount": 0.05, "decimals": 8},
    "GAMI":   {"daily_amount": 0.2,  "decimals": 8},
    "KAI":    {"daily_amount": 0.15, "decimals": 8},
    "YBOB":   {"daily_amount": 1.0,  "decimals": 2},
}

class WhitelistRequest(BaseModel):
    account_id: str
    email: Optional[str] = None

class AirdropRequest(BaseModel):
    token: str = "all"
    amount: Optional[float] = None
    recipients: Optional[List[str]] = None


@router.get("/whitelist")
async def get_whitelist():
    """Get all whitelisted wallet addresses."""
    wallets = list_wallets()
    return {
        "count":   len(wallets),
        "wallets": wallets,
        "status":  "active",
    }


@router.post("/whitelist")
async def add_to_whitelist(req: WhitelistRequest):
    """Add a Hedera account to the airdrop whitelist."""
    if not req.account_id:
        raise HTTPException(status_code=400, detail="account_id is required")
    if register_wallet(req.account_id):
        return {
            "status":     "registered",
            "account_id": req.account_id,
            "message":    f"Wallet {req.account_id} added to airdrop whitelist.",
        }
    return {
        "status":     "exists",
        "account_id": req.account_id,
        "message":    "Wallet already registered.",
    }


@router.delete("/whitelist/{account_id}")
async def remove_from_whitelist(account_id: str):
    """Remove a wallet from the whitelist."""
    if remove_wallet(account_id):
        return {"status": "removed", "account_id": account_id}
    raise HTTPException(status_code=404, detail="Wallet not found in whitelist")


@router.get("/schedule")
async def get_airdrop_schedule(days: int = 7):
    """Get upcoming airdrop schedule for the next N days."""
    schedule = []
    base = datetime.utcnow()
    for i in range(days):
        date = base + timedelta(days=i)
        schedule.append({
            "date":   date.strftime("%Y-%m-%d"),
            "tokens": {
                token: cfg["daily_amount"]
                for token, cfg in AIRDROP_CONFIG.items()
            },
            "status": "scheduled" if i > 0 else "pending",
        })
    return {
        "schedule":        schedule,
        "days":            days,
        "next_airdrop":    schedule[0]["date"] if schedule else None,
        "eligible_wallets": len(list_wallets()),
    }


@router.get("/eligibility/{account_id}")
async def check_eligibility(account_id: str):
    """Check if given account is eligible for airdrops."""
    wallets = list_wallets()
    eligible = account_id in wallets
    return {
        "account_id":   account_id,
        "eligible":     eligible,
        "daily_tokens": AIRDROP_CONFIG if eligible else {},
        "next_airdrop": datetime.utcnow().strftime("%Y-%m-%d"),
        "message":      "Eligible for all daily token airdrops!" if eligible else "Not whitelisted. POST to /api/airdrop/whitelist to register.",
    }


@router.post("/distribute")
async def run_airdrop(req: AirdropRequest):
    """Execute airdrop to specified recipients or all whitelisted wallets."""
    wallets = req.recipients or list_wallets()
    if not wallets:
        raise HTTPException(status_code=400, detail="No registered wallets found")

    amount = req.amount or 100
    results = []

    if req.token == "all":
        for token, cfg in AIRDROP_CONFIG.items():
            drop_amount = req.amount or cfg["daily_amount"] * len(wallets)
            distribute_airdrop(wallets, drop_amount)
            results.append({
                "token":      token,
                "amount":     drop_amount,
                "recipients": len(wallets),
                "status":     "distributed",
            })
    else:
        if req.token not in AIRDROP_CONFIG:
            raise HTTPException(status_code=400, detail=f"Unknown token: {req.token}")
        distribute_airdrop(wallets, amount)
        results.append({
            "token":      req.token,
            "amount":     amount,
            "recipients": len(wallets),
            "status":     "distributed",
        })

    return {
        "status":    "success",
        "timestamp": datetime.utcnow().isoformat(),
        "results":   results,
        "agent":     "Wallet Agent (HCS-10)",
    }


@router.get("/stats")
async def airdrop_stats():
    """Latest airdrop ecosystem stats."""
    wallets = list_wallets()
    total_distributed = {
        token: round(cfg["daily_amount"] * len(wallets) * 30, 4)  # 30 days estimate
        for token, cfg in AIRDROP_CONFIG.items()
    }
    return {
        "whitelisted_wallets": len(wallets),
        "tokens_in_airdrop":   len(AIRDROP_CONFIG),
        "daily_distribution":  {t: cfg["daily_amount"] for t, cfg in AIRDROP_CONFIG.items()},
        "estimated_30d_total": total_distributed,
        "network":             "Hedera Testnet",
        "agent":               "Wallet Agent (HCS-10)",
    }
