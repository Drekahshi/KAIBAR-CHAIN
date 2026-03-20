import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from services.airdrop_service import calculate_airdrop_schedule, check_airdrop_eligibility

logger = logging.getLogger(__name__)
router = APIRouter()

class EligibilityRequest(BaseModel):
    account_id: str = Field(..., description="Hedera Account ID (0.0.X) format expected")

@router.get("/schedule")
async def get_airdrop_schedule():
    """Generates the unified 30-day scheduled distribution list for KAIBAR token ecosystems."""
    logger.info("Airdrop schedule requested")
    try:
        schedule = calculate_airdrop_schedule(datetime.now(timezone.utc), days=30)
        return {"schedule": schedule}
    except Exception as e:
        logger.error(f"Failed to generate airdrop schedule: {e}")
        raise HTTPException(status_code=500, detail="Could not compute schedule.")

@router.get("/eligibility/{account_id}")
async def get_eligibility(account_id: str):
    """Query Hedera Mirror Node to confirm airdrop eligibility for a specific account."""
    logger.info(f"Checking whitelist eligibility for account: {account_id}")
    try:
        res = await check_airdrop_eligibility(account_id)
        if not res.get("eligible"):
            # Don't throw 404, just return false so frontend can display "Not Eligible" elegantly
            logger.debug(f"Account {account_id} not eligible")
        return res
    except Exception as e:
        logger.error(f"Error checking eligibility for {account_id}: {e}")
        raise HTTPException(status_code=503, detail="Hedera Network unavailable to check eligibility.")
