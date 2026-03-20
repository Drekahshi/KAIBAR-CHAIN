"""
routers/ai.py — KAIBAR AI endpoints
Investment strategies, vault analysis, and portfolio recommendations.
"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.ai_service import ai_query, analyze_vaults, get_strategy_recommendation
from modules.vault_monitor import VAULT_REGISTRY, MarketSimulator
from modules.tokenomics import TOKENS as TOKENOMICS_DATA
from services.vault_strategy import score_vault_risk

router = APIRouter()

class StrategyRequest(BaseModel):
    query: str
    balance: Optional[float] = None
    risk_profile: Optional[str] = "medium"
    portfolio: Optional[dict] = None

class AnalyzeRequest(BaseModel):
    risk_profile: str = "medium"
    capital: float = 1000.0


@router.post("/strategy")
async def get_investment_strategy(req: StrategyRequest):
    """
    Ask KAIBAR AI for investment advice.
    Injects live vault and token data for grounded answers.
    """
    # Build live market context
    sim = MarketSimulator()
    states = sim.tick()
    top_vault = max(VAULT_REGISTRY, key=lambda v: states[v.vault_id].apy_current)
    top_state = states[top_vault.vault_id]

    context = {
        "top_vault": top_vault.name,
        "top_vault_apy": round(top_state.apy_current, 2),
        "total_tvl": sum(s.tvl_usd for s in states.values()),
        "kai_price": TOKENOMICS_DATA.get("KAI", {}).get("usd_price", 0.0010),
        "network": "Hedera Testnet",
    }
    if req.balance:
        context["user_balance"] = req.balance
    if req.portfolio:
        context["user_portfolio"] = req.portfolio

    response = await ai_query(req.query, context)
    return {
        "response": response,
        "context_used": context,
        "agent": "KAIBAR AI",
        "powered_by": "Gemini + Ollama Fallback",
    }


@router.post("/analyze-vaults")
async def analyze_vault_opportunities(req: AnalyzeRequest):
    """AI analysis of current vault landscape with allocation suggestion."""
    sim = MarketSimulator()
    states = sim.tick()
    vaults = [
        {
            "id":   cfg.vault_id,
            "name": cfg.name,
            "apy":  round(states[cfg.vault_id].apy_current, 2),
            "tvl":  round(states[cfg.vault_id].tvl_usd, 2),
            "risk": score_vault_risk(
                states[cfg.vault_id].utilisation_pct,
                states[cfg.vault_id].health_ratio,
                states[cfg.vault_id].apy_current,
            ),
        }
        for cfg in VAULT_REGISTRY
    ]
    analysis = await analyze_vaults(vaults)
    return {
        "analysis": analysis,
        "vaults_analyzed": len(vaults),
        "capital": req.capital,
        "risk_profile": req.risk_profile,
    }


@router.get("/recommend")
async def quick_recommendation(
    balance: float = 500.0,
    risk: str = "medium"
):
    """Quick 3-point investment recommendation for given balance and risk tolerance."""
    recommendation = await get_strategy_recommendation(balance, risk)
    return {
        "recommendation": recommendation,
        "balance": balance,
        "risk_profile": risk,
        "network": "Hedera Testnet",
    }
