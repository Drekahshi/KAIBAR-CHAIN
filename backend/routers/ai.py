import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.gemini_service import query_investment_strategy, analyze_vault_opportunities, get_apy_recommendation
from services.ollama_service import query_local_strategy
from models.agent import AiQueryRequest
import os

logger = logging.getLogger(__name__)
router = APIRouter()

AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")

class ApyRecRequest(BaseModel):
    balance: float = Field(..., ge=0, description="User's portfolio balance in USD")
    risk_profile: str = Field(..., pattern="^(low|medium|high)$", description="User's risk profile")

@router.post("/strategy")
async def strategy(req: AiQueryRequest):
    """Get dynamic, context-aware investment strategy from KAIBAR AI Agent."""
    logger.info(f"AI Strategy request received using provider [{AI_PROVIDER}]")
    try:
        if AI_PROVIDER == "ollama":
            res = await query_local_strategy(req.query, req.portfolio_context)
        else:
            res = await query_investment_strategy(req.query, req.portfolio_context)
        return {"response": res, "provider": AI_PROVIDER}
    except Exception as e:
        logger.error(f"Strategy generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="AI Service currently unavailable.")

@router.post("/analyze-vaults")
async def analyze_vaults(vaults: list):
    """Generate intelligent natural language analysis of active vaults."""
    logger.info(f"Analyzing {len(vaults)} vaults")
    try:
        res = await analyze_vault_opportunities(vaults)
        return {"response": res}
    except Exception as e:
        logger.error(f"Vault analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Unable to process vault analysis.")

@router.post("/apy-recommendation")
async def apy_recommendation(req: ApyRecRequest):
    """Retrieve tailored APY recommendations based on available capital and risk."""
    logger.info(f"Generating APY recommendation for profile: {req.risk_profile}")
    try:
        res = await get_apy_recommendation(req.balance, req.risk_profile)
        return {"response": res}
    except Exception as e:
        logger.error(f"Recommendation generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch APY recommendations.")
