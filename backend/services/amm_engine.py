import math
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class KAIBAAMMEngine:
    """
    Constant product AMM (x * y = k) engine with KAIBA fee structure.
    Calculates off-chain mathematics for Hedera Smart Contract Arbitrage Execution.
    """
    def __init__(self, reserve_a: float, reserve_b: float, fee_pct: float = 0.003):
        if reserve_a < 0 or reserve_b < 0:
            raise ValueError("Reserves cannot be negative.")
        if not (0 <= fee_pct <= 1):
            raise ValueError("Fee percentage must be between 0 and 1.")
            
        self.reserve_a = float(reserve_a)
        self.reserve_b = float(reserve_b)
        self.fee_pct = float(fee_pct)
        self.k = self.reserve_a * self.reserve_b
        
        logger.debug(f"AMM Engine instantly initialized with reserves A: {reserve_a}, B: {reserve_b}, Fee: {fee_pct}")

    def get_amount_out(self, amount_in: float, a_to_b: bool) -> float:
        """Determines expected swap output accounting for fees."""
        if amount_in <= 0:
            return 0.0
            
        reserve_in = self.reserve_a if a_to_b else self.reserve_b
        reserve_out = self.reserve_b if a_to_b else self.reserve_a
        
        amount_in_with_fee = amount_in * (1.0 - self.fee_pct)
        numerator = amount_in_with_fee * reserve_out
        denominator = reserve_in + amount_in_with_fee
        
        return numerator / denominator if denominator > 0 else 0.0

    def get_price(self) -> float:
        """Price of Token A expressed in Token B (B / A)"""
        return self.reserve_b / self.reserve_a if self.reserve_a > 0 else 0.0

    def add_liquidity(self, amount_a: float, amount_b: float):
        """Mock behavior to simulate adding liquidity"""
        self.reserve_a += amount_a
        self.reserve_b += amount_b
        self.k = self.reserve_a * self.reserve_b
        logger.debug(f"Liquidity added: {amount_a} A, {amount_b} B. K = {self.k}")

    def detect_arbitrage(self, external_price: float, threshold: float = 0.005) -> Dict[str, Any]:
        """Detect divergence between internal AMM price against an external oracle."""
        internal_price = self.get_price()
        if external_price <= 0:
            logger.warning("Invalid external oracle price received for arbitrage check.")
            return {"arbitrage_detected": False}
            
        deviation = abs(internal_price - external_price) / external_price
        
        # If deviation passes threshold, signal the Agent Feed
        if deviation > threshold:
            direction = "BUY_A" if internal_price < external_price else "SELL_A"
            logger.info(f"Arbitrage opportunity detected! Deviation: {deviation*100:.2f}%. Direction: {direction}")
            return {
                "arbitrage_detected": True,
                "direction": direction,
                "internal_price": internal_price,
                "external_price": external_price,
                "deviation_pct": round(deviation * 100, 4)
            }
        return {"arbitrage_detected": False}

    def rebalance_recommendation(self, target_price: float) -> Dict[str, Any]:
        """Calculates precise reserves required to shift the pool to a new target price."""
        current_price = self.get_price()
        if current_price <= 0 or target_price <= 0:
            return {"action": "none"}
            
        ratio = target_price / current_price
        new_reserve_a = math.sqrt(self.k / target_price)
        new_reserve_b = math.sqrt(self.k * target_price)
        
        logger.info(f"Rebalance computed. Adjusting reserves to match target price {target_price}")
        return {
            "action": "rebalance",
            "current_reserve_a": self.reserve_a,
            "current_reserve_b": self.reserve_b,
            "target_reserve_a": round(new_reserve_a, 6),
            "target_reserve_b": round(new_reserve_b, 6),
            "price_ratio": round(ratio, 4)
        }
