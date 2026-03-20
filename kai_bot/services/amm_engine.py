"""
amm_engine.py
──────────────────────────────────────────────────────────────────
KAIBAR AMM Engine — constant product formula (x * y = k)
Python handles off-chain calculations; JS executes on-chain.
"""
from __future__ import annotations
import math


class KAIBAMMEngine:
    """
    Constant product AMM (x * y = k) with KAIBAR fee structure.
    """
    def __init__(self, reserve_a: float, reserve_b: float, fee_pct: float = 0.003):
        self.reserve_a = reserve_a
        self.reserve_b = reserve_b
        self.fee_pct = fee_pct
        self.k = reserve_a * reserve_b

    def get_amount_out(self, amount_in: float, a_to_b: bool) -> float:
        """Constant product swap with fee deduction."""
        reserve_in  = self.reserve_a if a_to_b else self.reserve_b
        reserve_out = self.reserve_b if a_to_b else self.reserve_a
        amount_in_with_fee = amount_in * (1 - self.fee_pct)
        return (amount_in_with_fee * reserve_out) / (reserve_in + amount_in_with_fee)

    def get_price(self) -> float:
        """Current spot price (B per A)."""
        return self.reserve_b / self.reserve_a if self.reserve_a > 0 else 0

    def add_liquidity(self, amount_a: float, amount_b: float):
        """Add liquidity to the pool."""
        self.reserve_a += amount_a
        self.reserve_b += amount_b
        self.k = self.reserve_a * self.reserve_b

    def detect_arbitrage(self, external_price: float, threshold: float = 0.005) -> dict:
        """Detect arbitrage opportunity vs external price feed."""
        internal_price = self.get_price()
        if internal_price == 0:
            return {"arbitrage_detected": False}
        deviation = abs(internal_price - external_price) / external_price
        if deviation > threshold:
            direction = "BUY_A" if internal_price < external_price else "SELL_A"
            arb_profit_estimate = abs(internal_price - external_price) * self.reserve_a * 0.01
            return {
                "arbitrage_detected": True,
                "direction": direction,
                "internal_price": round(internal_price, 8),
                "external_price": external_price,
                "deviation_pct": round(deviation * 100, 4),
                "estimated_profit_usd": round(arb_profit_estimate, 4),
            }
        return {"arbitrage_detected": False, "deviation_pct": round(deviation * 100, 4)}

    def rebalance_recommendation(self, target_price: float) -> dict:
        """Compute optimal reserve targets to reach a target price."""
        current_price = self.get_price()
        if current_price == 0 or target_price <= 0:
            return {"action": "none"}
        new_reserve_a = math.sqrt(self.k / target_price)
        new_reserve_b = math.sqrt(self.k * target_price)
        return {
            "action": "rebalance",
            "current_reserve_a":  round(self.reserve_a, 6),
            "current_reserve_b":  round(self.reserve_b, 6),
            "target_reserve_a":   round(new_reserve_a, 6),
            "target_reserve_b":   round(new_reserve_b, 6),
            "current_price":      round(current_price, 8),
            "target_price":       round(target_price, 8),
            "price_ratio":        round(target_price / current_price, 4),
        }

    def get_state(self) -> dict:
        return {
            "reserve_a":    round(self.reserve_a, 6),
            "reserve_b":    round(self.reserve_b, 6),
            "k":            round(self.k, 6),
            "price":        round(self.get_price(), 8),
            "fee_pct":      self.fee_pct,
        }


# ── Pre-built KAIBAR pools (simulated) ──────────────────────────

KAIBAR_AMM_POOLS: dict[str, dict] = {
    "HBAR_YTOKEN": {
        "pair":       "HBAR/YToken",
        "reserve_a":  2_500_000,
        "reserve_b":  12_000_000,
        "fee_pct":    0.003,
        "apy":        22.1,
        "protocol":   "KAIBAR AMM",
    },
    "HBAR_GAMI": {
        "pair":       "HBAR/GAMI",
        "reserve_a":  800_000,
        "reserve_b":  3_200_000,
        "fee_pct":    0.003,
        "apy":        19.5,
        "protocol":   "KAIBAR AMM",
    },
    "YTOKEN_YBOB": {
        "pair":       "YToken/YBOB",
        "reserve_a":  500_000,
        "reserve_b":  5_000_000,
        "fee_pct":    0.001,
        "apy":        12.0,
        "protocol":   "KAIBAR AMM",
    },
    "HBAR_YGOLD": {
        "pair":       "HBAR/YGOLD",
        "reserve_a":  1_200_000,
        "reserve_b":  600_000,
        "fee_pct":    0.002,
        "apy":        18.9,
        "protocol":   "KAIBAR AMM",
    },
}


def get_all_pool_stats() -> list[dict]:
    """Return enriched pool stats for the API."""
    results = []
    for pool_id, cfg in KAIBAR_AMM_POOLS.items():
        engine = KAIBAMMEngine(cfg["reserve_a"], cfg["reserve_b"], cfg["fee_pct"])
        state  = engine.get_state()
        results.append({
            "pool_id":     pool_id,
            "pair":        cfg["pair"],
            "protocol":    cfg["protocol"],
            "reserve_a":   state["reserve_a"],
            "reserve_b":   state["reserve_b"],
            "price":       state["price"],
            "fee_pct":     state["fee_pct"],
            "apy":         cfg["apy"],
            "tvl_usd":     round((cfg["reserve_a"] + cfg["reserve_b"] * state["price"]) * 0.09, 2),
        })
    return results
