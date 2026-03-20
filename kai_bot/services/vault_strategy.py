"""
vault_strategy.py
──────────────────────────────────────────────────────────────────
Vault analytics & allocation engine for KAIBAR backend.
Provides APY projections, risk scoring, and optimal allocations.
"""
from __future__ import annotations
import math
import numpy as np
from typing import List, Dict, Optional

# ─────────────────────────────────────────────
# APY PROJECTION
# ─────────────────────────────────────────────

def compute_apy_projection(
    principal: float,
    apy_pct: float,
    duration_days: int,
    compound_frequency: int = 365
) -> Dict:
    """Compound interest projection for a vault position."""
    rate = apy_pct / 100
    n = compound_frequency
    t = duration_days / 365
    final_amount = principal * (1 + rate / n) ** (n * t)
    yield_earned = final_amount - principal
    return {
        "principal": round(principal, 6),
        "apy_pct": apy_pct,
        "duration_days": duration_days,
        "projected_value": round(final_amount, 6),
        "yield_earned": round(yield_earned, 6),
        "daily_yield": round(yield_earned / max(duration_days, 1), 6),
        "roi_pct": round((yield_earned / max(principal, 0.0001)) * 100, 4),
    }


# ─────────────────────────────────────────────
# OPTIMAL ALLOCATION (Markowitz-inspired)
# ─────────────────────────────────────────────

def calculate_optimal_allocation(
    vaults: List[Dict],
    risk_tolerance: str = "medium",
    total_capital: float = 1000.0
) -> List[Dict]:
    """
    Risk-adjusted portfolio allocation across KAIBAR vaults.
    risk_tolerance: 'low' | 'medium' | 'high'
    """
    if not vaults:
        return []

    apys = np.array([float(v.get("apy", 10.0)) for v in vaults])
    risk_map = {"low": 0.2, "medium": 0.5, "high": 0.8}
    risk_scores = np.array([
        risk_map.get(str(v.get("risk", "medium")).lower(), 0.5)
        for v in vaults
    ])

    # Higher tolerance → weight APY more; lower → weight safety more
    risk_weight = {"low": 0.75, "medium": 0.5, "high": 0.25}.get(risk_tolerance, 0.5)
    max_apy = float(max(apys)) if len(apys) > 0 else 1.0

    scores = apys * (1 - risk_weight) + (1 - risk_scores) * risk_weight * max_apy
    weights = scores / max(scores.sum(), 1e-9)

    return [
        {
            **v,
            "allocation_pct": round(float(w) * 100, 2),
            "allocation_amount": round(float(w) * total_capital, 2),
        }
        for v, w in zip(vaults, weights)
    ]


# ─────────────────────────────────────────────
# VAULT RISK SCORE
# ─────────────────────────────────────────────

def score_vault_risk(utilization_pct: float, health_ratio: float, apy: float) -> str:
    """Returns 'low' | 'medium' | 'high' risk label."""
    risk_pts = 0
    if utilization_pct > 85:
        risk_pts += 2
    elif utilization_pct > 70:
        risk_pts += 1

    if health_ratio < 1.2:
        risk_pts += 2
    elif health_ratio < 1.4:
        risk_pts += 1

    if apy > 40:
        risk_pts += 1

    if risk_pts >= 4:
        return "high"
    elif risk_pts >= 2:
        return "medium"
    return "low"


# ─────────────────────────────────────────────
# PENSION CALC
# ─────────────────────────────────────────────

def compute_pension(principal: float, years: int) -> Dict:
    """Long-term pension returns with year-bonus APY."""
    base_apy = 15.0 + years  # e.g. 5yr → 20% APY
    base_apy = min(base_apy, 60)
    result = compute_apy_projection(principal, base_apy, years * 365)
    result["lockup_years"] = years
    result["effective_apy"] = base_apy
    return result


# ─────────────────────────────────────────────
# INSURANCE PREMIUM CALC
# ─────────────────────────────────────────────

def compute_insurance(stake_amount: float, coverage_multiplier: float = 2.0, apy: float = 12.0) -> Dict:
    """Coverage and premium from staking."""
    coverage = stake_amount * coverage_multiplier
    annual_premium = (stake_amount * apy) / 100
    return {
        "stake_amount": stake_amount,
        "coverage_amount": round(coverage, 4),
        "annual_premium_from_yield": round(annual_premium, 4),
        "effective_coverage_multiplier": coverage_multiplier,
        "premium_apy_used": apy,
    }


# ─────────────────────────────────────────────
# FLASH LOAN ESTIMATE
# ─────────────────────────────────────────────

def estimate_flash_loan(amount: float, fee_pct: float = 0.05) -> Dict:
    """Flash loan fee estimate."""
    fee = amount * (fee_pct / 100)
    return {
        "requested_amount": amount,
        "fee_pct": fee_pct,
        "fee_amount": round(fee, 6),
        "repayment_required": round(amount + fee, 6),
        "network": "Hedera Testnet",
        "finality_seconds": "3-6",
    }
