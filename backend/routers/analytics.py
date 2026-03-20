import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from services.amm_engine import KAIBAAMMEngine

logger = logging.getLogger(__name__)
router = APIRouter()

class AmmRequest(BaseModel):
    reserve_a: float = Field(..., ge=0, description="Pool reserve for Token A")
    reserve_b: float = Field(..., ge=0, description="Pool reserve for Token B")
    fee_pct: float = Field(0.003, ge=0, le=1.0, description="Swap fee percentage (default 0.3%)")

class SwapQuoteRequest(AmmRequest):
    amount_in: float = Field(..., gt=0, description="Amount of tokens to swap in")
    a_to_b: bool = Field(..., description="True if swapping A to B; False for B to A")

class ArbitrageRequest(AmmRequest):
    external_price: float = Field(..., ge=0, description="External Oracle/Market Price")
    threshold: float = Field(0.005, ge=0, description="Percentage deviation to trigger arb detection")

class RebalanceRequest(AmmRequest):
    target_price: float = Field(..., gt=0, description="Ideal price ratio to rebalance towards")

@router.post("/amm/quote")
async def amm_quote(req: SwapQuoteRequest):
    """Fast, off-chain CPMM quote simulation to prepare for Hedera executing swaps."""
    logger.debug(f"AMM Quote request: amount {req.amount_in}, direction A->B: {req.a_to_b}")
    try:
        engine = KAIBAAMMEngine(req.reserve_a, req.reserve_b, req.fee_pct)
        amount_out = engine.get_amount_out(req.amount_in, req.a_to_b)
        price = engine.get_price()
        return {
            "amount_out": round(amount_out, 6),
            "execution_price": round(price, 6)
        }
    except Exception as e:
        logger.error(f"AMM calculation error: {e}")
        raise HTTPException(status_code=400, detail="Invalid reserves or inputs.")

@router.post("/amm/arbitrage")
async def amm_arbitrage(req: ArbitrageRequest):
    """Identifies Hedera AMM arbitrage opportunities vs external endpoints."""
    logger.info(f"Checking arbitrage at target {req.external_price}")
    try:
        engine = KAIBAAMMEngine(req.reserve_a, req.reserve_b, req.fee_pct)
        return engine.detect_arbitrage(req.external_price, req.threshold)
    except Exception as e:
        logger.error(f"Arbitrage calculation error: {e}")
        raise HTTPException(status_code=500, detail="Arbitrage logic failed.")

@router.post("/amm/rebalance")
async def amm_rebalance(req: RebalanceRequest):
    """Generates a rebalance action plan to realign AMM pool ratios."""
    logger.info("Executing Rebalance evaluation for agents.")
    try:
        engine = KAIBAAMMEngine(req.reserve_a, req.reserve_b, req.fee_pct)
        return engine.rebalance_recommendation(req.target_price)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
