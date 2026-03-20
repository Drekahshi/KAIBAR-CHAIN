"""
routers/vaults.py — KAIBAR Vault endpoints
All vault operations: list, deposit, withdraw, projection, allocation, pension, insurance, flash loans.
"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.vault_monitor import VAULT_REGISTRY, MarketSimulator
from services.vault_strategy import (
    compute_apy_projection, calculate_optimal_allocation,
    score_vault_risk, compute_pension, compute_insurance, estimate_flash_loan
)
from services.hedera_service import hedera

router = APIRouter()

# ── Pydantic models ───────────────────────────────────────────────

class DepositRequest(BaseModel):
    amount_hbar: float
    vault_id: Optional[str] = None
    account_id: Optional[str] = None

class WithdrawRequest(BaseModel):
    amount_hbar: float
    vault_id: Optional[str] = None
    account_id: Optional[str] = None

class ProjectionRequest(BaseModel):
    principal: float
    apy_pct: float
    duration_days: int
    compound_frequency: int = 365

class AllocationRequest(BaseModel):
    total_capital: float = 1000.0
    risk_tolerance: str = "medium"

class PensionRequest(BaseModel):
    principal: float
    years: int

class InsuranceRequest(BaseModel):
    stake_amount: float
    coverage_multiplier: float = 2.0
    apy: float = 12.0

class FlashLoanRequest(BaseModel):
    amount: float
    fee_pct: float = 0.05

# ── Endpoints ─────────────────────────────────────────────────────

@router.get("/")
async def list_vaults():
    """List all KAI vaults with live simulated state."""
    sim = MarketSimulator()
    states = sim.tick()
    result = []
    for cfg in VAULT_REGISTRY:
        s = states[cfg.vault_id]
        risk = score_vault_risk(s.utilisation_pct, s.health_ratio, s.apy_current)
        result.append({
            "id":            cfg.vault_id,
            "name":          cfg.name,
            "token":         cfg.token,
            "paired_token":  cfg.paired_token,
            "category":      cfg.category,
            "apy":           round(s.apy_current, 2),
            "apy_min":       cfg.apy_min,
            "apy_max":       cfg.apy_max,
            "tvl":           round(s.tvl_usd, 2),
            "utilization":   round(s.utilisation_pct, 2),
            "health":        round(s.health_ratio, 4),
            "risk":          risk,
            "lock_days":     cfg.lock_period_days,
            "description":   cfg.description,
            "alerts":        s.alerts,
        })
    return result


@router.post("/deposit")
async def vault_deposit(req: DepositRequest):
    """Deposit HBAR into a vault via Hedera SDK."""
    if req.amount_hbar <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    result = await hedera.vault_deposit(req.amount_hbar, req.vault_id)
    return result


@router.post("/withdraw")
async def vault_withdraw(req: WithdrawRequest):
    """Withdraw from a vault via Hedera SDK."""
    if req.amount_hbar <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    result = await hedera.vault_withdraw(req.amount_hbar, req.vault_id)
    return result


@router.post("/project")
async def project_yield(req: ProjectionRequest):
    """Project APY yield for given principal, APY%, and duration."""
    return compute_apy_projection(req.principal, req.apy_pct, req.duration_days, req.compound_frequency)


@router.post("/allocate")
async def allocate_vaults(req: AllocationRequest):
    """AI-powered optimal allocation across available vaults."""
    sim = MarketSimulator()
    states = sim.tick()
    vaults = []
    for cfg in VAULT_REGISTRY:
        s = states[cfg.vault_id]
        vaults.append({
            "id":   cfg.vault_id,
            "name": cfg.name,
            "apy":  s.apy_current,
            "tvl":  s.tvl_usd,
            "risk": score_vault_risk(s.utilisation_pct, s.health_ratio, s.apy_current),
        })
    allocated = calculate_optimal_allocation(vaults, req.risk_tolerance, req.total_capital)
    return {
        "risk_tolerance": req.risk_tolerance,
        "total_capital": req.total_capital,
        "allocations": allocated,
    }


@router.post("/pension/calculate")
async def calc_pension(req: PensionRequest):
    """Compute pension projection (long-term staking)."""
    return compute_pension(req.principal, req.years)


@router.post("/insurance/calculate")
async def calc_insurance(req: InsuranceRequest):
    """Calculate insurance coverage from staking amount."""
    return compute_insurance(req.stake_amount, req.coverage_multiplier, req.apy)


@router.post("/flash-loan/estimate")
async def flash_loan_estimate(req: FlashLoanRequest):
    """Estimate flash loan fee and repayment on Hedera (3–6s finality)."""
    return estimate_flash_loan(req.amount, req.fee_pct)


@router.get("/{vault_id}")
async def get_vault(vault_id: str):
    """Get a single vault by ID."""
    sim = MarketSimulator()
    states = sim.tick()
    for cfg in VAULT_REGISTRY:
        if cfg.vault_id == vault_id.upper():
            s = states[cfg.vault_id]
            return {
                "id":          cfg.vault_id,
                "name":        cfg.name,
                "apy":         round(s.apy_current, 2),
                "tvl":         round(s.tvl_usd, 2),
                "utilization": round(s.utilisation_pct, 2),
                "health":      round(s.health_ratio, 4),
                "risk":        score_vault_risk(s.utilisation_pct, s.health_ratio, s.apy_current),
                "description": cfg.description,
                "alerts":      s.alerts,
            }
    raise HTTPException(status_code=404, detail=f"Vault '{vault_id}' not found")
