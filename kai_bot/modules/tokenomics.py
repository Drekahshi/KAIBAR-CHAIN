"""
KAI Chain Tokenomics Module
============================
Self-contained tokenomics data and report display for the KAI ecosystem.
(Removed dependency on external kai_tokenomics module)
"""

from datetime import datetime

# ─── Token supply data ────────────────────────────────────────────────────────

TOKENS = {
    "KAI": {
        "name": "KAI Governance DAO Token",
        "total_supply": 100_000_000,
        "usd_price": 0.036,
        "circulating_pct": 20.0,
        "airdrop_pct": 20.0,
        "expected_apy": "N/A (governance)",
        "category": "governance",
        "allocations": {
            "Community Airdrop": 20.0,
            "Team & Advisors": 18.0,
            "Treasury / DAO": 25.0,
            "Ecosystem Growth": 22.0,
            "Private Sale": 10.0,
            "Public Sale": 5.0,
        },
    },
    "YT": {
        "name": "YToken Multi-Strategy DeFi Vault",
        "total_supply": 2_100_000_000,
        "usd_price": 0.0081,
        "circulating_pct": 15.0,
        "airdrop_pct": 2.0,
        "expected_apy": "22–38%",
        "category": "vault",
        "allocations": {
            "LP Incentives": 35.0,
            "Vault Rewards": 30.0,
            "Team": 15.0,
            "Treasury": 12.0,
            "Airdrop": 8.0,
        },
    },
    "YBOB": {
        "name": "YBOB Algorithmic Stablecoin",
        "total_supply": 500_000_000,
        "usd_price": 1.00,
        "circulating_pct": 40.0,
        "airdrop_pct": 5.0,
        "expected_apy": "10–15%",
        "category": "stablecoin",
        "allocations": {
            "Stability Reserve": 50.0,
            "Liquidity Mining": 25.0,
            "Airdrop": 10.0,
            "Protocol": 15.0,
        },
    },
    "YGOLD": {
        "name": "YGOLD Multi-Asset Yield Bond Vault",
        "total_supply": 8_400_000_000,
        "usd_price": 0.0495,
        "circulating_pct": 10.0,
        "airdrop_pct": 1.0,
        "expected_apy": "26–55%",
        "category": "bond",
        "allocations": {
            "Bond Yield Pool": 40.0,
            "BTC.HBAR LP": 30.0,
            "Gold Reserve": 20.0,
            "Airdrop": 5.0,
            "Team": 5.0,
        },
    },
    "KAI_CENTS": {
        "name": "KAI CENTS-H Gas Utility Token",
        "total_supply": 1_000_000_000,
        "usd_price": 0.09,
        "circulating_pct": 25.0,
        "airdrop_pct": 10.0,
        "expected_apy": "16–24%",
        "category": "utility",
        "allocations": {
            "Community Airdrop": 30.0,
            "Fee Discounts Pool": 30.0,
            "Staking Rewards": 25.0,
            "Reserve": 15.0,
        },
    },
    "GAMI": {
        "name": "GAMI Social DeFi Mining Token",
        "total_supply": 10_000_000_000,
        "usd_price": 0.0027,
        "circulating_pct": 12.0,
        "airdrop_pct": 5.0,
        "expected_apy": "12–22%",
        "category": "social",
        "allocations": {
            "Mining Rewards": 45.0,
            "Creator Pool": 25.0,
            "Airdrop": 15.0,
            "Team": 10.0,
            "Treasury": 5.0,
        },
    },
}


def _fmt(n: float) -> str:
    if n >= 1_000_000_000: return f"{n/1_000_000_000:.2f}B"
    if n >= 1_000_000:     return f"{n/1_000_000:.2f}M"
    if n >= 1_000:         return f"{n/1_000:.2f}K"
    return f"{n:.2f}"


def print_tokenomics():
    """Full tokenomics dashboard — called by bot CLI."""
    print("\n" + "═" * 76)
    print("  KAI CHAIN — TOKENOMICS REPORT")
    print(f"  Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print("═" * 76)

    total_fdv = sum(t["total_supply"] * t["usd_price"] for t in TOKENS.values())

    # ── Overview table ────────────────────────────────────────────────────────
    print(f"\n  {'Symbol':<12} {'Name':<36} {'Supply':>12}  {'Price':>8}  {'FDV':>10}  APY")
    print("  " + "─" * 72)
    for sym, t in TOKENS.items():
        fdv = t["total_supply"] * t["usd_price"]
        print(
            f"  {sym:<12} {t['name'][:34]:<36} "
            f"{_fmt(t['total_supply']):>12}  "
            f"${t['usd_price']:>7.5f}  "
            f"${_fmt(fdv):>9}  "
            f"{t['expected_apy']}"
        )
    print(f"  {'TOTAL FDV':>64}  ${_fmt(total_fdv):>9}")
    print("  " + "─" * 72)

    # ── Per-token allocation breakdown ────────────────────────────────────────
    for sym, t in TOKENS.items():
        circ   = t["total_supply"] * t["circulating_pct"] / 100
        mc     = circ * t["usd_price"]
        print(f"\n  ── {sym} — {t['name']} ──")
        print(f"  Total Supply : {_fmt(t['total_supply'])}  |  Circulating: {t['circulating_pct']:.0f}%  |  Market Cap: ${_fmt(mc)}")
        print(f"  Category     : {t['category'].upper()}  |  APY: {t['expected_apy']}")
        print(f"  {'Bucket':<30} {'%':>5}  {'Tokens':>14}  Visualization")
        print("  " + "─" * 60)
        for bucket, pct in t["allocations"].items():
            tokens_amt = t["total_supply"] * pct / 100
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            print(f"  {bucket:<30} {pct:>5.1f}%  {_fmt(tokens_amt):>14}  {bar}")

    print("\n" + "═" * 76 + "\n")


# ─── Dual staking yield projections ──────────────────────────────────────────
def print_dual_staking_yields():
    strategies = {
        "YT (BTC.HBAR vault)":        (22, 38),
        "Pension pool boost":          (5, 10),
        "GAMI engagement farming":     (12, 22),
        "KAI_CENTS gas staking":       (16, 24),
        "Governance (KAI) delegation": (3, 6),
    }
    print("\n  ── DUAL STAKING YIELD PROJECTIONS ─────────────────────────")
    low_total, high_total = 0.0, 0.0
    for name, (lo, hi) in strategies.items():
        low_total += lo; high_total += hi
        bar = "█" * int((lo + hi) / 5) + "░" * max(0, 20 - int((lo + hi) / 5))
        print(f"  {name:<32}  {lo:>5.0f}–{hi:<3.0f}%   {bar}")
    print(f"\n  Total Stacked APY: {low_total:.0f}–{high_total:.0f}%\n")


if __name__ == "__main__":
    print_tokenomics()
    print_dual_staking_yields()