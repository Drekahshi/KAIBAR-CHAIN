import logging
import numpy as np
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def calculate_optimal_allocation(
    vaults: List[Dict[str, Any]],
    risk_tolerance: str = "medium",
    total_capital: float = 1000.0
) -> List[Dict[str, Any]]:
    """
    Markowitz-inspired allocation across KAIBA vaults.
    Calculates risk-adjusted returns to determine capital weights per vault.
    
    Args:
        vaults: List of vault dictionaries with 'apy' and 'risk' keys.
        risk_tolerance: User's risk profile (low, medium, high).
        total_capital: Total USD to allocate.
        
    Returns:
        List of vaults enriched with 'allocation_pct' and 'allocation_amount'.
    """
    if not vaults:
        logger.warning("No vaults provided for allocation.")
        return []
    
    logger.debug(f"Calculating allocation across {len(vaults)} vaults for risk: {risk_tolerance}")

    apys = np.array([float(v.get("apy", 0)) for v in vaults])
    risk_scores = []
    
    # Map risk strings to numerical scores
    for v in vaults:
        r = str(v.get("risk", "medium")).lower()
        if r == "low":
            risk_scores.append(0.2)
        elif r == "medium":
            risk_scores.append(0.5)
        else:
            risk_scores.append(0.8)
            
    risk_scores = np.array(risk_scores)

    # Assign weight depending on user's selected risk tolerance
    risk_weight = 0.5
    if risk_tolerance == "low":
        risk_weight = 0.8
    elif risk_tolerance == "high":
        risk_weight = 0.2

    max_apy = float(max(apys)) if len(apys) > 0 and max(apys) > 0 else 1.0
    
    # Formula interpolates yield with risk penalty
    scores = apys * (1 - risk_weight) + (1 - risk_scores) * risk_weight * max_apy
    total_score = float(scores.sum())
    
    if total_score > 0:
        weights = scores / total_score
    else:
        weights = np.ones(len(vaults)) / len(vaults)

    allocations = [
        {
            **vault,
            "allocation_pct": float(round(w * 100, 2)),
            "allocation_amount": float(round(w * total_capital, 2))
        }
        for vault, w in zip(vaults, weights)
    ]
    
    logger.info("Allocation successfully calculated.")
    return allocations

def compute_apy_projection(
    principal: float,
    apy_pct: float,
    duration_days: int,
    compound_frequency: int = 365
) -> Dict[str, Any]:
    """
    Compute compounded projected returns for a vault position over time.
    """
    logger.debug(f"Projecting yield for {principal} at {apy_pct}% over {duration_days} days.")
    rate = apy_pct / 100.0
    n = compound_frequency
    t = duration_days / 365.0
    amount = float(principal * (1 + rate / n) ** (n * t))
    
    return {
        "principal": float(principal),
        "apy_pct": float(apy_pct),
        "duration_days": int(duration_days),
        "projected_value": round(amount, 6),
        "yield_earned": round(amount - principal, 6),
        "daily_yield": round((amount - principal) / duration_days, 6) if duration_days > 0 else 0.0
    }
