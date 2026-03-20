import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import httpx
import os

logger = logging.getLogger(__name__)

HEDERA_MIRROR = os.getenv("HEDERA_MIRROR_NODE", "https://testnet.mirrornode.hedera.com")

AIRDROP_CONFIG = {
    "YTOKEN": {"id": os.getenv("YTOKEN_ID", "0.0.12345"), "daily_amount": 0.1, "decimals": 8},
    "YGOLD": {"id": os.getenv("YGOLD_ID", "0.0.12346"), "daily_amount": 0.05, "decimals": 8},
    "GAMI": {"id": os.getenv("GAMI_ID", "0.0.12347"), "daily_amount": 0.2, "decimals": 8},
    "KAIBAR": {"id": os.getenv("KAIBAR_ID", "0.0.12348"), "daily_amount": 0.15, "decimals": 8},
    "KYBOB": {"id": os.getenv("KYBOB_ID", "0.0.12349"), "daily_amount": 1.0, "decimals": 2},
}

def calculate_airdrop_schedule(start_date: datetime, days: int = 30) -> List[Dict[str, Any]]:
    """
    Generates deterministic airdrop schedules for the next N days.
    Useful for Smart Contract Trust/Pension daily automated releases.
    """
    logger.debug(f"Calculating airdrop schedule for {days} days starting {start_date}")
    schedule = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        schedule.append({
            "date": date.isoformat(),
            "tokens": {
                token: config["daily_amount"]
                for token, config in AIRDROP_CONFIG.items()
            },
            "status": "scheduled" if i > 0 else "pending"
        })
    return schedule

async def check_airdrop_eligibility(account_id: str) -> Dict[str, Any]:
    """
    Checks if a Hedera account exists and has a positive HBAR balance natively before airdrop.
    """
    if not account_id:
        return {"eligible": False, "account_id": None, "reason": "No account ID provided."}
        
    logger.info(f"Checking eligibility over Mirror Node for account: {account_id}")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(f"{HEDERA_MIRROR}/api/v1/accounts/{account_id}")
            
            if res.status_code == 200:
                account = res.json()
                balance = account.get("balance", {}).get("balance", 0)
                # Ensure they have at least >0 TINYBARS for gas/fee payments
                if balance > 0:
                    return {
                        "eligible": True,
                        "account_id": account_id,
                        "balance_hbar": round(balance / 1e8, 4),
                        "tokens": account.get("balance", {}).get("tokens", [])
                    }
                else:
                    return {
                        "eligible": False, 
                        "account_id": account_id,
                        "reason": "Account HBAR balance is zero. Cannot pay HTS association fees."
                    }
            else:
                logger.warning(f"Mirror node returned {res.status_code} for account {account_id}")
                return {"eligible": False, "account_id": account_id, "reason": f"Mirror Node error {res.status_code}"}
                
    except httpx.RequestError as e:
        logger.error(f"Network error checking eligibility: {e}")
        return {"eligible": False, "account_id": account_id, "reason": "Network unavailable."}
    except Exception as e:
        logger.error(f"Unknown error in eligibility check: {e}")
        return {"eligible": False, "account_id": account_id, "reason": "Internal logic error."}
