"""
routers/hedera.py — Hedera network endpoints
Account info, transactions, scheduled transfers (HSS), and HCS operations.
"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.hedera_service import hedera

router = APIRouter()

class ScheduledTransferRequest(BaseModel):
    from_account: str
    to_account: str
    amount_hbar: float
    memo: str = ""
    contract_type: str = "trust"       # trust | pension | insurance
    execute_at_seconds: Optional[int] = None

class AccountRequest(BaseModel):
    account_id: str


@router.get("/account/{account_id}")
async def get_account(account_id: str):
    """
    Fetch Hedera account info from mirror node.
    Returns balance, tokens, and creation time.
    """
    return await hedera.get_account_info(account_id)


@router.get("/transactions/{account_id}")
async def get_transactions(account_id: str, limit: int = 10):
    """Get recent transactions for a Hedera account."""
    txs = await hedera.get_transactions(account_id, limit)
    return {"account_id": account_id, "transactions": txs, "count": len(txs)}


@router.post("/schedule/transfer")
async def create_scheduled_transfer(req: ScheduledTransferRequest):
    """
    Create a Hedera Scheduled Service (HSS) transfer.
    Used for Trust releases, Pension payouts, and Insurance claims.
    """
    if req.amount_hbar <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    memo = req.memo or f"KAIBAR {req.contract_type.capitalize()} — {req.from_account} → {req.to_account}"
    result = await hedera.create_scheduled_transfer(
        req.from_account,
        req.to_account,
        req.amount_hbar,
        memo,
        req.execute_at_seconds,
    )
    result["contract_type"] = req.contract_type
    return result


@router.post("/hcs/message")
async def submit_hcs(
    topic_id: str,
    agent_id: str,
    operation: str,
    payload: dict,
):
    """Submit an HCS-10 protocol message to a topic."""
    from datetime import datetime
    message = {
        "p":         "hcs-10",
        "op":        operation,
        "agent_id":  agent_id,
        "payload":   payload,
        "timestamp": datetime.utcnow().isoformat(),
    }
    return await hedera.submit_hcs_message(topic_id, message)


@router.get("/network/status")
async def network_status():
    """Check Hedera testnet connectivity."""
    import httpx
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            res = await client.get("https://testnet.mirrornode.hedera.com/api/v1/network/supply")
            if res.status_code == 200:
                data = res.json()
                return {
                    "status":        "online",
                    "network":       "testnet",
                    "total_supply":  data.get("total_supply"),
                    "released_supply": data.get("released_supply"),
                    "timestamp":     data.get("timestamp"),
                }
    except Exception:
        pass
    return {
        "status":  "unreachable",
        "network": "testnet",
        "message": "Mirror node unreachable — running in simulated mode",
    }
