import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from services.vault_strategy import calculate_optimal_allocation, compute_apy_projection
from services.hedera_python import hedera

logger = logging.getLogger(__name__)
router = APIRouter()

class DepositRequest(BaseModel):
    amount_hbar: float = Field(..., gt=0, description="Amount of HBAR to deposit")
    vault_id: Optional[str] = Field(None, description="Vault Contract ID to deposit into")
    account_id: Optional[str] = Field(None, description="User's Hedera Account ID")

class WithdrawRequest(BaseModel):
    amount_hbar: float = Field(..., gt=0, description="Amount of HBAR to withdraw")
    vault_id: Optional[str] = Field(None, description="Vault Contract ID to withdraw from")
    account_id: Optional[str] = Field(None, description="User's Hedera Account ID")

class ProjectionRequest(BaseModel):
    principal: float = Field(..., gt=0, description="Starting principal amount")
    apy_pct: float = Field(..., ge=0, description="Expected Annual Percentage Yield")
    duration_days: int = Field(..., gt=0, description="Duration of staking in days")
    compound_frequency: int = Field(365, gt=0, description="Compounds per year (default daily)")

class AllocationRequest(BaseModel):
    total_capital: float = Field(1000.0, gt=0, description="Total capital available to allocate")
    risk_tolerance: str = Field("medium", pattern="^(low|medium|high)$", description="Risk appetite")

# Mock vault data for MVP display
MOCK_VAULTS = [
    {"id": "bonzo-usdc-1", "name": "Bonzo USDC", "apy": 14.5, "tvl": 250000, "risk": "low", "protocol": "Bonzo"},
    {"id": "kaiba-mmf-1", "name": "KAIBA Money Market", "apy": 18.2, "tvl": 500000, "risk": "low", "protocol": "KAIBA"},
    {"id": "bonzo-hbar-2", "name": "Bonzo HBAR", "apy": 21.3, "tvl": 150000, "risk": "medium", "protocol": "Bonzo"},
    {"id": "kaiba-ygold-1", "name": "YGOLD Bond Vault", "apy": 26.5, "tvl": 75000, "risk": "medium", "protocol": "KAIBA"},
]

@router.get("/opportunities")
async def vault_opportunities():
    """Returns aggregated vault opportunities across Bonzo and KAIBA with risk assessment."""
    logger.info("Fetching Vault opportunities")
    return {"vaults": MOCK_VAULTS}

@router.post("/deposit")
async def vault_deposit(req: DepositRequest):
    """Deposit HBAR into a Hedera Smart Contract Vault."""
    try:
        logger.info(f"Processing deposit of {req.amount_hbar} to vault {req.vault_id}")
        return await hedera.vault_deposit(req.amount_hbar, req.vault_id)
    except Exception as e:
        logger.error(f"Deposit failed: {e}")
        raise HTTPException(status_code=500, detail=f"Deposit execution failed: {str(e)}")

@router.post("/withdraw")
async def vault_withdraw(req: WithdrawRequest):
    """Withdraw HBAR from a Hedera Smart Contract Vault."""
    try:
        logger.info(f"Processing withdrawal of {req.amount_hbar} from vault {req.vault_id}")
        # MVP simulation: in production call hedera.vault_withdraw(...)
        return {
            "success": True,
            "amount_hbar": req.amount_hbar,
            "vault_id": req.vault_id or "default",
            "message": f"Withdrawal of {req.amount_hbar} HBAR processed."
        }
    except Exception as e:
        logger.error(f"Withdrawal failed: {e}")
        raise HTTPException(status_code=500, detail="Withdrawal execution failed.")

@router.post("/project")
async def project_yield(req: ProjectionRequest):
    """Calculates compounded APY projection."""
    logger.debug(f"Calculating projection for {req.principal} at {req.apy_pct}% over {req.duration_days} days")
    return compute_apy_projection(
        req.principal, req.apy_pct, req.duration_days, req.compound_frequency
    )

@router.post("/allocate")
async def allocate_vaults(req: AllocationRequest):
    """Executes a Markowitz-inspired risk-adjusted AI allocation."""
    logger.info(f"Calculating allocation for {req.total_capital} with risk {req.risk_tolerance}")
    allocated = calculate_optimal_allocation(MOCK_VAULTS, req.risk_tolerance, req.total_capital)
    if not allocated:
        raise HTTPException(status_code=404, detail="No valid vaults to allocate to.")
    return {
        "risk_tolerance": req.risk_tolerance,
        "total_capital": req.total_capital,
        "allocations": allocated,
    }
