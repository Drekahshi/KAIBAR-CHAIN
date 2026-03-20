"""
kai_vault_monitor.py
═══════════════════════════════════════════════════════════════
KAI Chain — Vault & Pool Monitor
Hedera Hashgraph Testnet | BTC.HBAR DeFi Infrastructure

Monitors all KAI ecosystem vaults and liquidity pools:
  • YT Vault         BTC.HBAR Multi-Strategy DeFi Vault   22–38% APY
  • YGOLD Vault      Multi-Asset Yield Bond Vault          26–55% APY
  • KAI MMF          Money Market Fund (Savings + Invest)  18–55% APY
  • KAI Pension      Long-Term Staking Pool                28–60% APY
  • KAI Insurance    Decentralised Insurance Pool          20–32% APY
  • GAMI Pool        Social DeFi Mining Pool               12–22% APY
  • YBOB Reserve     Stablecoin Backstop Pool              10–15% APY
  • Flash Loan Pool  Instant Liquidity Pool                fee-based

Features:
  ✓ Real-time TVL tracking per vault
  ✓ APY simulation (base + bonus + IL protection)
  ✓ Health ratio monitoring (collateral / debt)
  ✓ Utilisation rate per pool
  ✓ Yield harvested tracker
  ✓ Risk alerts (low liquidity, health breach, peg deviation)
  ✓ Continuous monitoring loop with configurable interval
  ✓ CSV + JSON transaction log
  ✓ Pretty console dashboard
═══════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import csv
import json
import math
import random
import time
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
REFRESH_INTERVAL  = 5        # seconds between monitor ticks
MAX_TICKS         = 0        # 0 = run forever; set > 0 for demo
LOG_DIR           = Path("storage/logs");   LOG_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR           = Path("storage/output"); OUT_DIR.mkdir(parents=True, exist_ok=True)
HBAR_USD          = 0.09     # testnet tHBAR price

# ─────────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "vault_monitor.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("KAI_VAULT")


# ═════════════════════════════════════════════
#  DATA CLASSES
# ═════════════════════════════════════════════

@dataclass
class VaultConfig:
    """Static configuration for a vault/pool."""
    vault_id:          str
    name:              str
    token:             str           # primary token symbol
    paired_token:      str           # e.g. HBAR, USDC
    category:          str           # vault | bond | mmf | pension | insurance | social | stable | flash
    apy_min:           float         # whitepaper lower bound
    apy_max:           float         # whitepaper upper bound
    target_util:       float = 80.0  # target utilisation %
    min_health:        float = 1.10  # minimum health ratio before alert
    collateral_ratio:  float = 1.40  # overcollateralisation ratio (140%)
    fee_rate:          float = 0.003 # 0.3% swap fee
    lock_period_days:  int   = 0     # 0 = no lock
    description:       str   = ""


@dataclass
class VaultState:
    """Live runtime state of a vault."""
    vault_id:          str
    tvl_usd:           float
    total_deposits:    float          # in primary token units
    total_borrows:     float          # for lending pools
    collateral_usd:    float
    yield_harvested:   float          # USD accumulated this session
    apy_current:       float          # simulated live APY
    utilisation_pct:   float          # borrows / deposits * 100
    health_ratio:      float          # collateral / borrows
    peg_price:         float = 1.0    # for stablecoins; 1.0 = perfect peg
    last_harvest:      str   = ""
    alerts:            list[str] = field(default_factory=list)
    tick:              int   = 0


@dataclass
class HarvestEvent:
    """A recorded yield harvest."""
    vault_id:    str
    token:       str
    amount_usd:  float
    apy_at_time: float
    tx_hash:     str
    timestamp:   str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class AlertEvent:
    """A recorded risk alert."""
    vault_id:    str
    level:       str    # INFO | WARNING | CRITICAL
    message:     str
    value:       float
    timestamp:   str = field(default_factory=lambda: datetime.utcnow().isoformat())


# ═════════════════════════════════════════════
#  VAULT REGISTRY  — all KAI pools
# ═════════════════════════════════════════════

VAULT_REGISTRY: list[VaultConfig] = [
    VaultConfig(
        vault_id         = "YT_VAULT",
        name             = "YToken BTC.HBAR Vault",
        token            = "YT",
        paired_token     = "HBAR",
        category         = "vault",
        apy_min          = 22.0,
        apy_max          = 38.0,
        target_util      = 85.0,
        collateral_ratio = 1.40,
        fee_rate         = 0.003,
        description      = "Core inflation-resistant strategy: BTC.HBAR liquidity + HBAR staking",
    ),
    VaultConfig(
        vault_id         = "YGOLD_VAULT",
        name             = "YGOLD Bond Vault",
        token            = "YGOLD",
        paired_token     = "USDC",
        category         = "bond",
        apy_min          = 26.0,
        apy_max          = 55.0,
        target_util      = 75.0,
        collateral_ratio = 1.45,
        fee_rate         = 0.002,
        lock_period_days = 180,
        description      = "Real-world asset backing: infra bonds + BTC.HBAR LP + tokenised gold",
    ),
    VaultConfig(
        vault_id         = "YBOB_STABLE",
        name             = "YBOB Stable Pool",
        token            = "YBOB",
        paired_token     = "USDC",
        category         = "stable",
        apy_min          = 10.0,
        apy_max          = 15.0,
        target_util      = 90.0,
        collateral_ratio = 1.50,
        fee_rate         = 0.001,
        description      = "Algorithmic peg maintenance — USDC lending + BTC.HBAR fee distribution",
    ),
    VaultConfig(
        vault_id         = "CREATOR_ECONOMY",
        name             = "Creator Economy Pool",
        token            = "GAMI",
        paired_token     = "HBAR",
        category         = "social",
        apy_min          = 12.0,
        apy_max          = 22.0,
        target_util      = 75.0,
        collateral_ratio = 1.30,
        fee_rate         = 0.003,
        description      = "Engagement mining & creator staking integration",
    ),
    VaultConfig(
        vault_id         = "SME_FINANCING",
        name             = "SME Financing Pool",
        token            = "BTC.HBAR",
        paired_token     = "USDC",
        category         = "flash",
        apy_min          = 8.0,
        apy_max          = 15.0,
        target_util      = 60.0,
        collateral_ratio = 1.30,
        fee_rate         = 0.001,
        description      = "Tokenized collateral + supply-chain factoring liquidity",
    ),
    VaultConfig(
        vault_id         = "PENSION_POOL",
        name             = "KAI Pension DeFi Pool",
        token            = "YT",
        paired_token     = "HBAR",
        category         = "pension",
        apy_min          = 24.0,
        apy_max          = 54.0,
        target_util      = 70.0,
        collateral_ratio = 1.60,
        fee_rate         = 0.001,
        lock_period_days = 730,
        description      = "Long-term 2–50yr lock — exponential yield bonuses + inheritance trust",
    ),
    VaultConfig(
        vault_id         = "INSURANCE_HEALTH",
        name             = "Comprehensive Health Pool",
        token            = "YToken",
        paired_token     = "USDC",
        category         = "insurance",
        apy_min          = 20.0,
        apy_max          = 28.0,
        target_util      = 60.0,
        min_health       = 1.20,
        collateral_ratio = 1.55,
        fee_rate         = 0.005,
        description      = "Hospitalization, surgery & accident cover powered by yield",
    ),
    VaultConfig(
        vault_id         = "INSURANCE_FARMER",
        name             = "Farmer Protection Pool",
        token            = "YGOLD",
        paired_token     = "HBAR",
        category         = "insurance",
        apy_min          = 22.0,
        apy_max          = 32.0,
        target_util      = 65.0,
        min_health       = 1.15,
        collateral_ratio = 1.45,
        fee_rate         = 0.005,
        description      = "Drought & pest coverage for smallholder agriculture",
    ),
]


# ═════════════════════════════════════════════
#  SIMULATION ENGINE
# (replace internals with real Hedera Mirror Node calls)
# ═════════════════════════════════════════════

class MarketSimulator:
    """
    Simulates live market data for each vault.
    In production swap this out for Hedera Mirror Node REST API
    or SaucerSwap / Bonzo on-chain reads.
    """

    # Seed TVL per vault (USD)  - $100M Year 1 Projections
    SEED_TVL: dict[str, float] = {
        "YT_VAULT":          30_000_000,
        "YGOLD_VAULT":       20_000_000,
        "YBOB_STABLE":       15_000_000,
        "CREATOR_ECONOMY":   10_000_000,
        "SME_FINANCING":     15_000_000,
        "PENSION_POOL":      10_000_000,
        "INSURANCE_HEALTH":  5_000_000,
        "INSURANCE_FARMER":  5_000_000,
    }

    def __init__(self):
        self._states: dict[str, VaultState] = {}
        self._tick = 0
        for cfg in VAULT_REGISTRY:
            tvl     = self.SEED_TVL.get(cfg.vault_id, 1_000_000)
            borrows = tvl * (cfg.target_util / 100) * random.uniform(0.8, 1.0)
            self._states[cfg.vault_id] = VaultState(
                vault_id       = cfg.vault_id,
                tvl_usd        = tvl,
                total_deposits = tvl / HBAR_USD,
                total_borrows  = borrows / HBAR_USD,
                collateral_usd = tvl * cfg.collateral_ratio,
                yield_harvested= 0.0,
                apy_current    = random.uniform(cfg.apy_min, cfg.apy_max),
                utilisation_pct= borrows / tvl * 100,
                health_ratio   = (tvl * cfg.collateral_ratio) / max(borrows, 1),
                peg_price      = 1.0 if cfg.category == "stable" else 0.0,
                last_harvest   = datetime.utcnow().isoformat(),
            )

    def tick(self) -> dict[str, VaultState]:
        """Advance one monitoring tick — simulate small market movements."""
        self._tick += 1
        for cfg in VAULT_REGISTRY:
            s = self._states[cfg.vault_id]
            s.tick = self._tick

            # TVL drift ±0.8% per tick
            tvl_drift   = random.uniform(-0.008, 0.012)
            s.tvl_usd   = max(10_000, s.tvl_usd * (1 + tvl_drift))

            # Utilisation random walk within ±3%
            util_delta  = random.uniform(-3.0, 3.0)
            s.utilisation_pct = max(5.0, min(99.0, s.utilisation_pct + util_delta))

            # APY follows utilisation (higher util → higher APY, bounded by whitepaper range)
            util_factor = s.utilisation_pct / cfg.target_util
            base_apy    = cfg.apy_min + (cfg.apy_max - cfg.apy_min) * min(util_factor, 1.2) * 0.8
            apy_noise   = random.uniform(-1.5, 1.5)
            s.apy_current = max(cfg.apy_min * 0.8, min(cfg.apy_max * 1.1, base_apy + apy_noise))

            # Borrows from utilisation
            borrows_usd = s.tvl_usd * s.utilisation_pct / 100
            s.total_borrows  = borrows_usd / HBAR_USD
            s.total_deposits = s.tvl_usd / HBAR_USD

            # Collateral ratio
            s.collateral_usd = s.tvl_usd * cfg.collateral_ratio * random.uniform(0.98, 1.02)
            s.health_ratio   = s.collateral_usd / max(borrows_usd, 1.0)

            # Stablecoin peg simulation
            if cfg.category == "stable":
                peg_drift = random.uniform(-0.002, 0.002)
                s.peg_price = max(0.97, min(1.03, s.peg_price + peg_drift))

            # Accumulate yield (per tick, annualised → per-second approximation)
            seconds_per_year = 365.25 * 24 * 3600
            yield_per_tick   = s.tvl_usd * (s.apy_current / 100) / (seconds_per_year / REFRESH_INTERVAL)
            s.yield_harvested += yield_per_tick

            # Build alerts
            s.alerts = []
            if s.health_ratio < cfg.min_health:
                s.alerts.append(f"CRITICAL: health ratio {s.health_ratio:.3f} < {cfg.min_health}")
            if s.utilisation_pct > 95:
                s.alerts.append(f"WARNING: utilisation {s.utilisation_pct:.1f}% — liquidity risk")
            if s.utilisation_pct < 20:
                s.alerts.append(f"INFO: low utilisation {s.utilisation_pct:.1f}% — idle capital")
            if cfg.category == "stable" and abs(s.peg_price - 1.0) > 0.01:
                s.alerts.append(f"WARNING: peg deviation {s.peg_price:.4f} (target 1.0000)")
            if s.tvl_usd < 100_000:
                s.alerts.append(f"CRITICAL: TVL critically low ${s.tvl_usd:,.0f}")

        return self._states

    def current(self) -> dict[str, VaultState]:
        return self._states


# ═════════════════════════════════════════════
#  LOGGER
# ═════════════════════════════════════════════

class VaultLogger:
    def __init__(self):
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.harvest_csv = OUT_DIR / f"vault_harvests_{ts}.csv"
        self.alerts_csv  = OUT_DIR / f"vault_alerts_{ts}.csv"
        self.snapshot_json = OUT_DIR / f"vault_snapshot_{ts}.json"
        self._harvests: list[dict] = []
        self._alerts:   list[dict] = []

        for path, fields in [
            (self.harvest_csv, ["timestamp","vault_id","token","amount_usd","apy_at_time","tx_hash"]),
            (self.alerts_csv,  ["timestamp","vault_id","level","message","value"]),
        ]:
            with open(path, "w", newline="") as f:
                csv.DictWriter(f, fieldnames=fields).writeheader()

    def log_harvest(self, e: HarvestEvent):
        row = {"timestamp": e.timestamp, "vault_id": e.vault_id,
               "token": e.token, "amount_usd": round(e.amount_usd, 6),
               "apy_at_time": round(e.apy_at_time, 4), "tx_hash": e.tx_hash}
        self._harvests.append(row)
        with open(self.harvest_csv, "a", newline="") as f:
            csv.DictWriter(f, fieldnames=list(row.keys())).writerow(row)

    def log_alert(self, e: AlertEvent):
        row = {"timestamp": e.timestamp, "vault_id": e.vault_id,
               "level": e.level, "message": e.message, "value": round(e.value, 6)}
        self._alerts.append(row)
        with open(self.alerts_csv, "a", newline="") as f:
            csv.DictWriter(f, fieldnames=list(row.keys())).writerow(row)

    def snapshot(self, states: dict[str, VaultState]):
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "vaults": {
                vid: {
                    "tvl_usd":         round(s.tvl_usd, 2),
                    "apy_current":     round(s.apy_current, 4),
                    "utilisation_pct": round(s.utilisation_pct, 2),
                    "health_ratio":    round(s.health_ratio, 4),
                    "yield_harvested": round(s.yield_harvested, 6),
                    "alerts":          s.alerts,
                }
                for vid, s in states.items()
            }
        }
        with open(self.snapshot_json, "w") as f:
            json.dump(data, f, indent=2)


# ═════════════════════════════════════════════
#  DISPLAY ENGINE
# ═════════════════════════════════════════════

CATEGORY_ICONS = {
    "vault":     "◈",
    "bond":      "◆",
    "mmf":       "◉",
    "pension":   "◎",
    "insurance": "◬",
    "social":    "◐",
    "stable":    "◇",
    "flash":     "◁",
}

LEVEL_COLORS = {"CRITICAL": "!!!", "WARNING": ">>>", "INFO": "---"}


def fmt(n: float, decimals: int = 2) -> str:
    if n >= 1_000_000_000: return f"{n/1_000_000_000:.{decimals}f}B"
    if n >= 1_000_000:     return f"{n/1_000_000:.{decimals}f}M"
    if n >= 1_000:         return f"{n/1_000:.{decimals}f}K"
    return f"{n:.{decimals}f}"


def health_bar(pct: float, width: int = 16) -> str:
    filled = int(round(min(pct, 100) / 100 * width))
    bar    = "█" * filled + "░" * (width - filled)
    if pct > 80:   marker = "▓"
    elif pct > 50: marker = "▒"
    else:          marker = "░"
    return bar


def apy_indicator(apy: float, apy_min: float, apy_max: float) -> str:
    if apy >= apy_max * 0.9: return "▲▲"
    if apy >= (apy_min + apy_max) / 2: return "▲ "
    return "▼ "


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def render_dashboard(
    states:   dict[str, VaultState],
    configs:  dict[str, VaultConfig],
    tick:     int,
    logger:   VaultLogger,
    alert_log: list[AlertEvent],
):
    clear_screen()
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    total_tvl   = sum(s.tvl_usd for s in states.values())
    total_yield = sum(s.yield_harvested for s in states.values())
    total_alerts= sum(len(s.alerts) for s in states.values())

    # ── HEADER ────────────────────────────────────────────────────
    print("═" * 78)
    print("  KAI CHAIN  —  VAULT & POOL MONITOR          Hedera Hashgraph Testnet")
    print(f"  Tick #{tick:<6}  {now}            tHBAR = ${HBAR_USD}")
    print("─" * 78)
    print(
        f"  Total TVL: ${fmt(total_tvl)}   "
        f"Yield harvested: ${fmt(total_yield, 4)}   "
        f"Active alerts: {total_alerts}   "
        f"Pools: {len(states)}"
    )
    print("═" * 78)

    # ── POOL TABLE ─────────────────────────────────────────────────
    print(f"  {'':2} {'Vault':<30} {'TVL':>9}  {'APY':>7}  {'Util%':>6}  {'Health':>7}  {'Yield $':>9}  {'Bar'}")
    print("  " + "─" * 74)

    for cfg in VAULT_REGISTRY:
        s   = states[cfg.vault_id]
        c   = configs[cfg.vault_id]
        icon = CATEGORY_ICONS.get(cfg.category, "•")
        apy_ind = apy_indicator(s.apy_current, cfg.apy_min, cfg.apy_max)

        # Health colour indicator
        if s.health_ratio < cfg.min_health:
            health_str = f"[{s.health_ratio:.2f}]!"
        elif s.health_ratio < cfg.min_health * 1.2:
            health_str = f"[{s.health_ratio:.2f}]~"
        else:
            health_str = f" {s.health_ratio:.2f} "

        alert_flag = " [!]" if s.alerts else "    "

        print(
            f"  {icon} {cfg.vault_id:<28}{alert_flag}"
            f"  ${fmt(s.tvl_usd):>7}"
            f"  {s.apy_current:>5.2f}%{apy_ind}"
            f"  {s.utilisation_pct:>5.1f}%"
            f"  {health_str:>7}"
            f"  ${fmt(s.yield_harvested, 4):>8}"
            f"  {health_bar(s.utilisation_pct)}"
        )

    print("─" * 78)

    # ── CATEGORY LEGEND ────────────────────────────────────────────
    legend = "  " + "   ".join(f"{v}{k}" for k, v in CATEGORY_ICONS.items())
    print(legend)
    print("─" * 78)

    # ── VAULT DETAIL CARDS ─────────────────────────────────────────
    print("\n  VAULT DETAILS")
    print("  " + "─" * 74)
    for cfg in VAULT_REGISTRY:
        s = states[cfg.vault_id]

        peg_info = f"  Peg: {s.peg_price:.4f}" if cfg.category == "stable" else ""
        lock_info = f"  Lock: {cfg.lock_period_days}d" if cfg.lock_period_days else ""

        print(
            f"  {CATEGORY_ICONS[cfg.category]} {cfg.vault_id:<22} "
            f"TVL: ${fmt(s.tvl_usd):<9} "
            f"APY: {s.apy_current:.2f}%  ({cfg.apy_min}–{cfg.apy_max}%)  "
            f"Collat: {cfg.collateral_ratio*100:.0f}%"
            f"{peg_info}{lock_info}"
        )
        print(
            f"    Deposits: {fmt(s.total_deposits):<12} "
            f"Borrows: {fmt(s.total_borrows):<12} "
            f"Util: {s.utilisation_pct:.1f}%  "
            f"Health: {s.health_ratio:.3f}"
        )
        print(f"    {cfg.description}")

        if s.alerts:
            for alert in s.alerts:
                prefix = LEVEL_COLORS.get(alert.split(":")[0], ">>>")
                print(f"    {prefix} {alert}")

        print()

    # ── APY COMPARISON ─────────────────────────────────────────────
    print("  APY COMPARISON (current vs whitepaper range)")
    print("  " + "─" * 74)
    for cfg in VAULT_REGISTRY:
        s = states[cfg.vault_id]
        bar_width = 40
        range_width = cfg.apy_max - cfg.apy_min
        pos = int((s.apy_current - cfg.apy_min) / max(range_width, 1) * bar_width)
        pos = max(0, min(bar_width - 1, pos))
        apy_bar = "░" * pos + "█" + "░" * (bar_width - pos - 1)
        print(
            f"  {cfg.vault_id:<22} "
            f"{cfg.apy_min:>5.0f}% |{apy_bar}| {cfg.apy_max:.0f}%  "
            f"now: {s.apy_current:.2f}%"
        )

    # ── RECENT ALERTS ──────────────────────────────────────────────
    if alert_log:
        recent = alert_log[-6:]
        print("\n  RECENT ALERTS")
        print("  " + "─" * 74)
        for a in reversed(recent):
            prefix = LEVEL_COLORS.get(a.level, ">>>")
            print(f"  {prefix} [{a.timestamp[11:19]}] {a.vault_id:<22} {a.message}")

    # ── FOOTER ─────────────────────────────────────────────────────
    print("\n" + "─" * 78)
    print(f"  Refreshing every {REFRESH_INTERVAL}s  |  Log: {logger.harvest_csv.name}  |  Ctrl+C to exit")
    print("═" * 78)


# ═════════════════════════════════════════════
#  ALERT PROCESSOR
# ═════════════════════════════════════════════

def process_alerts(
    states:    dict[str, VaultState],
    configs:   dict[str, VaultConfig],
    logger:    VaultLogger,
    alert_log: list[AlertEvent],
):
    for cfg in VAULT_REGISTRY:
        s = states[cfg.vault_id]
        for msg in s.alerts:
            level = "CRITICAL" if msg.startswith("CRITICAL") else \
                    "WARNING"  if msg.startswith("WARNING")  else "INFO"
            val = s.health_ratio if "health" in msg else \
                  s.utilisation_pct if "util" in msg else \
                  s.peg_price if "peg" in msg else s.tvl_usd

            event = AlertEvent(vault_id=cfg.vault_id, level=level, message=msg, value=val)
            alert_log.append(event)
            logger.log_alert(event)

            if level == "CRITICAL":
                log.critical(f"[{cfg.vault_id}] {msg}")
            elif level == "WARNING":
                log.warning(f"[{cfg.vault_id}] {msg}")


# ═════════════════════════════════════════════
#  HARVEST PROCESSOR
# ═════════════════════════════════════════════

def process_harvests(
    states:  dict[str, VaultState],
    configs: dict[str, VaultConfig],
    logger:  VaultLogger,
    tick:    int,
):
    """Auto-harvest yield every 10 ticks."""
    if tick % 10 != 0:
        return
    for cfg in VAULT_REGISTRY:
        s = states[cfg.vault_id]
        if s.yield_harvested > 0:
            tx_hash = "0x" + hex(random.getrandbits(128))[2:].upper().zfill(32)
            event   = HarvestEvent(
                vault_id    = cfg.vault_id,
                token       = cfg.token,
                amount_usd  = s.yield_harvested,
                apy_at_time = s.apy_current,
                tx_hash     = tx_hash,
            )
            logger.log_harvest(event)
            log.info(f"[HARVEST] {cfg.vault_id}  ${s.yield_harvested:.4f}  tx={tx_hash[:16]}…")


# ═════════════════════════════════════════════
#  MAIN MONITOR LOOP
# ═════════════════════════════════════════════

def run_monitor(max_ticks: int = MAX_TICKS, interval: int = REFRESH_INTERVAL):
    log.info("KAI Vault Monitor starting…")
    log.info(f"Monitoring {len(VAULT_REGISTRY)} pools  |  interval={interval}s  |  max_ticks={max_ticks or 'unlimited'}")

    sim        = MarketSimulator()
    logger     = VaultLogger()
    alert_log: list[AlertEvent] = []
    configs    = {cfg.vault_id: cfg for cfg in VAULT_REGISTRY}
    tick       = 0

    # Initial tick
    states = sim.tick()

    try:
        while True:
            tick  += 1
            states = sim.tick()

            process_alerts(states, configs, logger, alert_log)
            process_harvests(states, configs, logger, tick)
            logger.snapshot(states)

            render_dashboard(states, configs, tick, logger, alert_log)

            if max_ticks > 0 and tick >= max_ticks:
                log.info(f"Reached max_ticks={max_ticks}. Exiting.")
                break

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\n  Monitor stopped by user.")
        log.info("Monitor stopped by user.")

    # Final summary
    print("\n  ── FINAL SESSION SUMMARY ───────────────────────")
    total_tvl   = sum(s.tvl_usd for s in states.values())
    total_yield = sum(s.yield_harvested for s in states.values())
    print(f"  Ticks run:       {tick}")
    print(f"  Total TVL:       ${fmt(total_tvl)}")
    print(f"  Total yield:     ${fmt(total_yield, 4)}")
    print(f"  Total alerts:    {len(alert_log)}")
    print(f"  Harvest log:     {logger.harvest_csv}")
    print(f"  Alert log:       {logger.alerts_csv}")
    print(f"  Snapshot JSON:   {logger.snapshot_json}")
    print("═" * 78)


# ═════════════════════════════════════════════
#  ENTRY POINT
# ═════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="KAI Chain Vault & Pool Monitor")
    parser.add_argument("--ticks",    type=int, default=MAX_TICKS,        help="Max ticks (0=unlimited)")
    parser.add_argument("--interval", type=int, default=REFRESH_INTERVAL, help="Refresh interval in seconds")
    args = parser.parse_args()

    run_monitor(max_ticks=args.ticks, interval=args.interval)


# ─────────────────────────────────────────────
#  BOT-COMPATIBLE WRAPPER
# ─────────────────────────────────────────────

def print_vaults_overview():
    """Static vault summary used by the bot CLI (no infinite loop)."""
    configs = {cfg.vault_id: cfg for cfg in VAULT_REGISTRY}
    sim = MarketSimulator()
    states = sim.tick()

    total_tvl = sum(s.tvl_usd for s in states.values())
    print("\n" + "═" * 72)
    print("  KAI CHAIN — VAULT OVERVIEW")
    print("═" * 72)
    fmt_h = "  {:2} {:<22} {:>5}  {:>9}  {:>6}  {:>7}  {:>8}  Risk"
    print(fmt_h.format("", "Vault", "APY", "TVL", "Util%", "Health", "Yield $"))
    print("  " + "─" * 68)
    for cfg in VAULT_REGISTRY:
        s    = states[cfg.vault_id]
        icon = CATEGORY_ICONS.get(cfg.category, "•")
        tvl  = f"${s.tvl_usd/1_000_000:.2f}M" if s.tvl_usd >= 1_000_000 else f"${s.tvl_usd:,.0f}"
        print(
            f"  {icon} {cfg.vault_id:<22} "
            f"{s.apy_current:>4.1f}%  "
            f"{tvl:>9}  "
            f"{s.utilisation_pct:>5.1f}%  "
            f"{s.health_ratio:>7.2f}  "
            f"${s.yield_harvested:>7.4f}  "
            f"{cfg.category}"
        )
    print("─" * 72)
    print(f"  Total TVL: ${total_tvl/1_000_000:.2f}M  |  Vaults: {len(VAULT_REGISTRY)}")
    print("═" * 72 + "\n")
