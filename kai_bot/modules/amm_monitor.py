"""
KAI Chain AMM Monitor & Token Converter
========================================
Automated Market Maker simulation for the KAI ecosystem on Hedera Hashgraph.

Base rate (from whitepaper): 1 tHBAR = 0.09 YT

Supported tokens:
  HBAR      - Hedera native (testnet tHBAR)
  YT        - YToken Multi-Strategy DeFi Vault
  YBOB      - Algorithmic Stablecoin (1:1 USD peg)
  YGOLD     - Multi-Asset Yield Bond Vault
  GAMI      - Social DeFi Mining Token
  KAI       - Governance DAO Token
  KAI_CENTS - Gas + Prediction Utility Token

AMM formula: Constant Product  x * y = k  (Uniswap v2 style)
Fee: 0.3% per swap (redistributed to LP providers)
"""

import math
import time
import json
import csv
import random
import logging
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional


# ─────────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────────
LOG_DIR = Path("storage/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "amm_monitor.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("KAI_AMM")


# ─────────────────────────────────────────────
#  TOKEN REGISTRY  (from KAI Whitepaper)
#  Base: 1 tHBAR = 0.09 YT  →  1 YT = 11.111 tHBAR
#  All prices derived from this anchor rate
# ─────────────────────────────────────────────
HBAR_USD = 0.09          # testnet tHBAR price in USD

TOKEN_REGISTRY = {
    "HBAR": {
        "name":     "Hedera HBAR (testnet)",
        "usd":      HBAR_USD,
        "decimals": 8,
    },
    "YT": {
        "name":     "YToken Multi-Strategy DeFi Vault",
        "usd":      HBAR_USD * 0.09,   # 1 HBAR = 0.09 YT  →  1 YT ≈ $0.0081
        "decimals": 8,
    },
    "YBOB": {
        "name":     "YBOB Algorithmic Stablecoin",
        "usd":      1.00,               # pegged 1:1 USD
        "decimals": 6,
    },
    "YGOLD": {
        "name":     "YGOLD Multi-Asset Yield Bond Vault",
        "usd":      HBAR_USD * 0.55,    # 1 YGOLD ≈ 0.55 HBAR equivalent
        "decimals": 8,
    },
    "GAMI": {
        "name":     "GAMI Social DeFi Mining Token",
        "usd":      HBAR_USD * 0.03,    # micro-cap social token
        "decimals": 8,
    },
    "KAI": {
        "name":     "KAI Governance DAO Token",
        "usd":      HBAR_USD * 0.40,    # governance premium
        "decimals": 8,
    },
    "KAI_CENTS": {
        "name":     "KAI CENTS-H Gas Utility Token",
        "usd":      HBAR_USD * 1.00,    # soft-pegged 1:1 HBAR
        "decimals": 4,
    },
}


# ─────────────────────────────────────────────
#  DATA CLASSES
# ─────────────────────────────────────────────
@dataclass
class Pool:
    """Constant-product AMM pool  (x * y = k)."""
    token_a:    str
    token_b:    str
    reserve_a:  float
    reserve_b:  float
    fee_rate:   float = 0.003          # 0.3%
    total_fees_a: float = 0.0
    total_fees_b: float = 0.0
    swap_count:   int   = 0

    @property
    def k(self) -> float:
        return self.reserve_a * self.reserve_b

    @property
    def price_a_in_b(self) -> float:
        """How many token_b per 1 token_a."""
        return self.reserve_b / self.reserve_a

    @property
    def price_b_in_a(self) -> float:
        """How many token_a per 1 token_b."""
        return self.reserve_a / self.reserve_b

    @property
    def tvl_usd(self) -> float:
        usd_a = TOKEN_REGISTRY[self.token_a]["usd"]
        usd_b = TOKEN_REGISTRY[self.token_b]["usd"]
        return self.reserve_a * usd_a + self.reserve_b * usd_b

    def label(self) -> str:
        return f"{self.token_a}/{self.token_b}"


@dataclass
class SwapResult:
    pool:           str
    token_in:       str
    token_out:      str
    amount_in:      float
    amount_out:     float
    fee_charged:    float
    price_impact:   float          # percentage
    rate:           float          # amount_out per 1 token_in
    tx_hash:        str
    timestamp:      str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status:         str = "success"


# ─────────────────────────────────────────────
#  AMM CORE ENGINE
# ─────────────────────────────────────────────
class AMMPool:
    """
    Constant-product AMM (x * y = k).
    Supports any KAI ecosystem token pair.
    """

    def __init__(self, pool: Pool):
        self.pool = pool

    def get_amount_out(self, token_in: str, amount_in: float) -> float:
        """
        Calculate output using x*y=k with fee.
        amount_in_with_fee = amount_in * (1 - fee_rate)
        amount_out = reserve_out - k / (reserve_in + amount_in_with_fee)
        """
        p = self.pool
        if token_in == p.token_a:
            reserve_in, reserve_out = p.reserve_a, p.reserve_b
        elif token_in == p.token_b:
            reserve_in, reserve_out = p.reserve_b, p.reserve_a
        else:
            raise ValueError(f"Token {token_in} not in pool {p.label()}")

        amount_in_with_fee = amount_in * (1 - p.fee_rate)
        amount_out = reserve_out - (p.k / (reserve_in + amount_in_with_fee))
        return max(0.0, amount_out)

    def get_price_impact(self, token_in: str, amount_in: float) -> float:
        """Price impact as a percentage."""
        p = self.pool
        if token_in == p.token_a:
            spot = p.reserve_b / p.reserve_a
        else:
            spot = p.reserve_a / p.reserve_b

        amount_out  = self.get_amount_out(token_in, amount_in)
        exec_price  = amount_out / amount_in if amount_in > 0 else 0
        impact      = abs(exec_price - spot) / spot * 100
        return round(impact, 4)

    def execute_swap(self, token_in: str, amount_in: float) -> SwapResult:
        """
        Execute a swap, update reserves, collect fee.
        Returns a SwapResult record.
        """
        p           = self.pool
        fee         = amount_in * p.fee_rate
        amount_out  = self.get_amount_out(token_in, amount_in)
        impact      = self.get_price_impact(token_in, amount_in)

        if token_in == p.token_a:
            token_out = p.token_b
            p.reserve_a  += amount_in
            p.reserve_b  -= amount_out
            p.total_fees_a += fee
        else:
            token_out = p.token_a
            p.reserve_b  += amount_in
            p.reserve_a  -= amount_out
            p.total_fees_b += fee

        p.swap_count += 1
        rate    = amount_out / amount_in if amount_in > 0 else 0
        tx_hash = "0x" + hex(random.getrandbits(128))[2:].upper().zfill(32)

        result = SwapResult(
            pool         = p.label(),
            token_in     = token_in,
            token_out    = token_out,
            amount_in    = round(amount_in, 8),
            amount_out   = round(amount_out, 8),
            fee_charged  = round(fee, 8),
            price_impact = impact,
            rate         = round(rate, 8),
            tx_hash      = tx_hash,
        )

        logger.info(
            f"SWAP  {amount_in:.4f} {token_in} → {amount_out:.4f} {token_out}  "
            f"fee={fee:.4f}  impact={impact:.3f}%  tx={tx_hash[:14]}…"
        )
        return result


# ─────────────────────────────────────────────
#  MULTI-HOP ROUTER
# ─────────────────────────────────────────────
class AMMRouter:
    """
    Routes swaps across multiple pools.
    Finds best path for any token → token conversion
    using HBAR as the hub (HBAR is the base pair for all pools).
    """

    def __init__(self, pools: dict[str, AMMPool]):
        self.pools = pools          # key: "TOKENA/TOKENB"

    def _find_pool(self, token_a: str, token_b: str) -> Optional[AMMPool]:
        key1 = f"{token_a}/{token_b}"
        key2 = f"{token_b}/{token_a}"
        return self.pools.get(key1) or self.pools.get(key2)

    def get_quote(self, token_in: str, token_out: str, amount_in: float) -> dict:
        """
        Get a swap quote.  Direct if pool exists, else route via HBAR.
        Returns dict with amount_out, rate, impact, path.
        """
        # Direct pool
        pool = self._find_pool(token_in, token_out)
        if pool:
            out    = pool.get_amount_out(token_in, amount_in)
            impact = pool.get_price_impact(token_in, amount_in)
            return {
                "path":       [token_in, token_out],
                "amount_out": round(out, 8),
                "rate":       round(out / amount_in, 8) if amount_in > 0 else 0,
                "impact":     impact,
                "fee_total":  round(amount_in * pool.pool.fee_rate, 8),
                "hops":       1,
            }

        # 2-hop via HBAR
        if token_in != "HBAR" and token_out != "HBAR":
            pool1 = self._find_pool(token_in, "HBAR")
            pool2 = self._find_pool("HBAR", token_out)
            if pool1 and pool2:
                mid        = pool1.get_amount_out(token_in, amount_in)
                final      = pool2.get_amount_out("HBAR", mid)
                impact1    = pool1.get_price_impact(token_in, amount_in)
                impact2    = pool2.get_price_impact("HBAR", mid)
                fee1       = amount_in * pool1.pool.fee_rate
                fee2       = mid * pool2.pool.fee_rate
                return {
                    "path":       [token_in, "HBAR", token_out],
                    "amount_out": round(final, 8),
                    "rate":       round(final / amount_in, 8) if amount_in > 0 else 0,
                    "impact":     round(impact1 + impact2, 4),
                    "fee_total":  round(fee1 + fee2 * (TOKEN_REGISTRY[token_in]["usd"] / HBAR_USD), 8),
                    "hops":       2,
                }

        return {"error": f"No route found for {token_in} → {token_out}"}

    def execute(self, token_in: str, token_out: str, amount_in: float) -> list[SwapResult]:
        """Execute best-path swap, returns list of SwapResult (1 or 2 hops)."""
        quote = self.get_quote(token_in, token_out, amount_in)
        if "error" in quote:
            raise ValueError(quote["error"])

        results = []
        path    = quote["path"]

        if len(path) == 2:
            pool = self._find_pool(path[0], path[1])
            results.append(pool.execute_swap(path[0], amount_in))

        elif len(path) == 3:
            pool1  = self._find_pool(path[0], path[1])
            r1     = pool1.execute_swap(path[0], amount_in)
            results.append(r1)
            pool2  = self._find_pool(path[1], path[2])
            r2     = pool2.execute_swap(path[1], r1.amount_out)
            results.append(r2)

        return results


# ─────────────────────────────────────────────
#  TRANSACTION LOGGER
# ─────────────────────────────────────────────
class SwapLogger:
    def __init__(self):
        ts            = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.csv_path = LOG_DIR / f"swaps_{ts}.csv"
        self._records: list[dict] = []

        with open(self.csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "timestamp","pool","token_in","token_out",
                "amount_in","amount_out","fee_charged",
                "price_impact","rate","tx_hash","status"
            ])
            writer.writeheader()

    def log(self, result: SwapResult):
        row = asdict(result)
        self._records.append(row)
        with open(self.csv_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(row.keys()))
            writer.writerow(row)

    def summary(self) -> dict:
        total_vol_usd = sum(
            r["amount_in"] * TOKEN_REGISTRY.get(r["token_in"], {}).get("usd", 0)
            for r in self._records
        )
        return {
            "total_swaps":   len(self._records),
            "total_vol_usd": round(total_vol_usd, 2),
            "log_file":      str(self.csv_path),
        }


# ─────────────────────────────────────────────
#  AMM MONITOR  (full system)
# ─────────────────────────────────────────────
class KAIAMMMonitor:
    """
    Full KAI AMM system:
    - Initialises all liquidity pools
    - Provides quote + swap interface
    - Prints live monitor dashboard
    - Logs all transactions
    """

    def __init__(self):
        self.pools  = self._init_pools()
        self.router = AMMRouter(self.pools)
        self.logger = SwapLogger()
        logger.info("KAI AMM Monitor initialised with %d pools.", len(self.pools))

    # ── Pool Initialisation ───────────────────
    def _init_pools(self) -> dict[str, AMMPool]:
        """
        Seed all pools using the whitepaper anchor rate:
        1 tHBAR = 0.09 YT
        All other reserves derived from USD equivalence.
        """
        raw_pools = [
            # (token_a, token_b, reserve_a, reserve_b)
            # HBAR/YT:  ratio = 1:0.09  → reserve parity in USD
            ("HBAR", "YT",        5_000_000,   5_000_000 * 0.09),
            ("HBAR", "YBOB",      3_000_000,   3_000_000 * HBAR_USD),     # YBOB is $1
            ("HBAR", "YGOLD",     2_500_000,   2_500_000 * (HBAR_USD / (HBAR_USD * 0.55))),
            ("HBAR", "GAMI",      1_500_000,   1_500_000 * (HBAR_USD / (HBAR_USD * 0.03))),
            ("HBAR", "KAI",       1_200_000,   1_200_000 * (HBAR_USD / (HBAR_USD * 0.40))),
            ("HBAR", "KAI_CENTS", 800_000,     800_000),                   # 1:1 with HBAR
            ("YT",   "YBOB",      10_000_000,  10_000_000 * (HBAR_USD * 0.09)),
            ("YGOLD","YBOB",      800_000,     800_000 * (HBAR_USD * 0.55)),
        ]

        pools = {}
        for ta, tb, ra, rb in raw_pools:
            pool = Pool(token_a=ta, token_b=tb, reserve_a=ra, reserve_b=rb)
            amm  = AMMPool(pool)
            pools[f"{ta}/{tb}"] = amm

        return pools

    # ── Public API ────────────────────────────
    def quote(self, token_in: str, token_out: str, amount: float) -> dict:
        """Get swap quote without executing."""
        q = self.router.get_quote(token_in, token_out, amount)
        if "error" not in q:
            q["amount_in"]  = amount
            q["token_in"]   = token_in
            q["token_out"]  = token_out
        return q

    def swap(self, token_in: str, token_out: str, amount: float) -> list[SwapResult]:
        """Execute a swap and log it."""
        results = self.router.execute(token_in, token_out, amount)
        for r in results:
            self.logger.log(r)
        return results

    def convert(self, token_in: str, token_out: str, amount: float) -> float:
        """Simple conversion: return output amount."""
        q = self.quote(token_in, token_out, amount)
        if "error" in q:
            raise ValueError(q["error"])
        return q["amount_out"]

    # ── Display ───────────────────────────────
    def print_rates(self):
        """Print all conversion rates from HBAR."""
        print("\n" + "─"*60)
        print("  KAI AMM — Live Rates (base: 1 tHBAR)")
        print("─"*60)
        print(f"  {'Token':<12} {'Rate (per HBAR)':>18}  {'USD Value':>12}  {'Pool TVL':>12}")
        print("  " + "─"*55)
        for sym, meta in TOKEN_REGISTRY.items():
            if sym == "HBAR":
                continue
            try:
                rate = self.convert("HBAR", sym, 1.0)
                tvl_key = f"HBAR/{sym}"
                pool_obj = self.pools.get(tvl_key) or self.pools.get(f"{sym}/HBAR")
                tvl = f"${pool_obj.pool.tvl_usd:,.0f}" if pool_obj else "—"
                print(f"  {sym:<12} {rate:>18.6f}  ${meta['usd']:>11.6f}  {tvl:>12}")
            except Exception:
                print(f"  {sym:<12} {'—':>18}")
        print("─"*60)

    def print_pool_stats(self):
        """Print all pool statistics."""
        print("\n" + "─"*60)
        print("  KAI AMM — Pool Statistics")
        print("─"*60)
        print(f"  {'Pool':<16} {'Reserve A':>14}  {'Reserve B':>14}  {'TVL (USD)':>12}  {'Swaps':>6}")
        print("  " + "─"*60)
        total_tvl = 0
        for key, amm in self.pools.items():
            p = amm.pool
            total_tvl += p.tvl_usd
            print(
                f"  {key:<16} "
                f"{p.reserve_a:>14,.2f}  "
                f"{p.reserve_b:>14,.2f}  "
                f"${p.tvl_usd:>11,.2f}  "
                f"{p.swap_count:>6}"
            )
        print(f"  {'TOTAL':<48} ${total_tvl:>11,.2f}")
        print("─"*60)

    def print_quote(self, token_in: str, token_out: str, amount: float):
        """Pretty-print a conversion quote."""
        q = self.quote(token_in, token_out, amount)
        print(f"\n  Quote: {amount} {token_in} → {token_out}")
        print(f"  {'─'*40}")
        if "error" in q:
            print(f"  Error: {q['error']}")
            return
        path_str = " → ".join(q["path"])
        print(f"  Path:         {path_str}  ({q['hops']} hop{'s' if q['hops']>1 else ''})")
        print(f"  You receive:  {q['amount_out']:.6f} {token_out}")
        print(f"  Rate:         1 {token_in} = {q['rate']:.6f} {token_out}")
        print(f"  Price impact: {q['impact']:.3f}%")
        print(f"  Fee (0.3%):   {q['fee_total']:.6f} {token_in}")
        in_usd  = amount * TOKEN_REGISTRY[token_in]["usd"]
        out_usd = q["amount_out"] * TOKEN_REGISTRY[token_out]["usd"]
        print(f"  USD in/out:   ${in_usd:.4f} / ${out_usd:.4f}")

    def print_conversion_table(self, amount: float = 1.0):
        """Full N×N conversion matrix for all tokens."""
        tokens = list(TOKEN_REGISTRY.keys())
        col_w  = 13

        print(f"\n  Conversion table — {amount} of each token")
        print("─" * (12 + col_w * len(tokens)))

        header = f"  {'FROM \\ TO':<12}" + "".join(f"{t:>{col_w}}" for t in tokens)
        print(header)
        print("─" * (12 + col_w * len(tokens)))

        for t_in in tokens:
            row = f"  {t_in:<12}"
            for t_out in tokens:
                if t_in == t_out:
                    row += f"{'—':>{col_w}}"
                else:
                    try:
                        val = self.convert(t_in, t_out, amount)
                        row += f"{val:>{col_w}.4f}"
                    except Exception:
                        row += f"{'N/A':>{col_w}}"
            print(row)
        print("─" * (12 + col_w * len(tokens)))

    def simulate_market(self, n: int = 10, verbose: bool = True):
        """Simulate random market swaps to generate realistic pool activity."""
        pairs = [
            ("HBAR", "YT"), ("HBAR", "YBOB"), ("HBAR", "YGOLD"),
            ("HBAR", "GAMI"), ("HBAR", "KAI"), ("YT", "YBOB"),
        ]
        if verbose:
            print(f"\n  Simulating {n} random market swaps…")
        for i in range(n):
            from_t, to_t = random.choice(pairs)
            if random.random() > 0.5:
                from_t, to_t = to_t, from_t
            amount = round(random.uniform(10, 5000), 2)
            try:
                results = self.swap(from_t, to_t, amount)
                if verbose:
                    r = results[-1]
                    print(
                        f"  [{i+1:02d}] {r.amount_in:.2f} {r.token_in} → "
                        f"{r.amount_out:.4f} {r.token_out}  "
                        f"impact={r.price_impact:.3f}%"
                    )
            except Exception as e:
                if verbose:
                    print(f"  [{i+1:02d}] Error: {e}")
            time.sleep(0.05)

    def summary(self) -> dict:
        total_tvl   = sum(amm.pool.tvl_usd for amm in self.pools.values())
        total_swaps = sum(amm.pool.swap_count for amm in self.pools.values())
        return {
            "pools":        len(self.pools),
            "total_tvl_usd": round(total_tvl, 2),
            "total_swaps":  total_swaps,
            **self.logger.summary(),
        }