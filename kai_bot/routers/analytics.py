"""
routers/analytics.py — KAI Ecosystem analytics + AMM
Provides AMM pool stats, swap quotes, arbitrage detection, and ecosystem dashboard.
"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.amm_monitor import KAIAMMMonitor
from modules.tokenomics import TOKENS as TOKENOMICS_DATA
from modules.vault_monitor import VAULT_REGISTRY, MarketSimulator
from services.amm_engine import KAIBAMMEngine, KAIBAR_AMM_POOLS, get_all_pool_stats

router = APIRouter()

class SwapQuoteRequest(BaseModel):
    pool_id: str
    amount_in: float
    a_to_b: bool = True

class RebalanceRequest(BaseModel):
    pool_id: str
    target_price: float

class ArbitrageRequest(BaseModel):
    pool_id: str
    external_price: float
    threshold: float = 0.005


@router.get("/pools")
async def get_pools():
    """All AMM pools with live stats."""
    return get_all_pool_stats()


@router.get("/legacy-amm")
async def get_legacy_amm():
    """Original KAI AMM monitor pools (for backward compatibility)."""
    mon = KAIAMMMonitor()
    pools = []
    for p_id, p_obj in mon.pools.items():
        p = p_obj.pool
        pools.append({
            "id":        p_id,
            "name":      p.name,
            "liquidity": round(p.liquidity_usd, 2),
            "apy":       round(p.apy, 2),
            "volume_24h": round(p.volume_24h_usd, 2),
            "fee_pct":   round(p.fee_pct * 100, 3),
        })
    return pools


@router.post("/swap/quote")
async def get_swap_quote(req: SwapQuoteRequest):
    """Get AMM swap output quote for a given pool."""
    cfg = KAIBAR_AMM_POOLS.get(req.pool_id)
    if not cfg:
        raise HTTPException(status_code=404, detail=f"Pool '{req.pool_id}' not found")
    engine = KAIBAMMEngine(cfg["reserve_a"], cfg["reserve_b"], cfg["fee_pct"])
    amount_out = engine.get_amount_out(req.amount_in, req.a_to_b)
    price_impact = abs(amount_out / (req.amount_in * engine.get_price() + 1e-9) - 1) * 100
    return {
        "pool_id":       req.pool_id,
        "pair":          cfg["pair"],
        "amount_in":     req.amount_in,
        "amount_out":    round(amount_out, 8),
        "price":         round(engine.get_price(), 8),
        "price_impact_pct": round(price_impact, 4),
        "fee_pct":       cfg["fee_pct"],
    }


@router.post("/arbitrage/detect")
async def detect_arbitrage(req: ArbitrageRequest):
    """Detect arbitrage opportunity in an AMM pool vs external price."""
    cfg = KAIBAR_AMM_POOLS.get(req.pool_id)
    if not cfg:
        raise HTTPException(status_code=404, detail=f"Pool '{req.pool_id}' not found")
    engine = KAIBAMMEngine(cfg["reserve_a"], cfg["reserve_b"], cfg["fee_pct"])
    return engine.detect_arbitrage(req.external_price, req.threshold)


@router.post("/rebalance")
async def get_rebalance_recommendation(req: RebalanceRequest):
    """Compute new reserve targets to reach a target price."""
    cfg = KAIBAR_AMM_POOLS.get(req.pool_id)
    if not cfg:
        raise HTTPException(status_code=404, detail=f"Pool '{req.pool_id}' not found")
    engine = KAIBAMMEngine(cfg["reserve_a"], cfg["reserve_b"], cfg["fee_pct"])
    return engine.rebalance_recommendation(req.target_price)


@router.get("/tokenomics")
async def get_tokenomics():
    """Full tokenomics data for all KAI ecosystem tokens."""
    return TOKENOMICS_DATA


@router.get("/ecosystem-summary")
async def get_ecosystem_summary():
    """High-level ecosystem stats for dashboard."""
    sim = MarketSimulator()
    states = sim.tick()
    total_tvl  = sum(s.tvl_usd for s in states.values())
    total_yield = sum(s.yield_harvested for s in states.values())
    top_apy_vault = max(states.items(), key=lambda x: x[1].apy_current)
    pool_stats = get_all_pool_stats()
    total_pool_tvl = sum(p["tvl_usd"] for p in pool_stats)

    return {
        "total_tvl_usd":    round(total_tvl + total_pool_tvl, 2),
        "vault_tvl_usd":    round(total_tvl, 2),
        "pool_tvl_usd":     round(total_pool_tvl, 2),
        "yield_harvested":  round(total_yield, 4),
        "active_vaults":    len(VAULT_REGISTRY),
        "active_pools":     len(pool_stats),
        "top_apy_vault":    top_apy_vault[0],
        "top_apy_pct":      round(top_apy_vault[1].apy_current, 2),
        "network":          "Hedera Testnet",
        "network_status":   "Operational",
        "hbar_usd":         0.09,
        "kai_price":        TOKENOMICS_DATA.get("KAI", {}).get("usd_price", 0.00042),
    }
