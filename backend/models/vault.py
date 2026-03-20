from pydantic import BaseModel, Field
from typing import Optional, List

class VaultConfig(BaseModel):
    vault_id: str = Field(..., description="Unique identifier for the Vault")
    name: str = Field(..., description="Display name of the Vault")
    token: str = Field(..., description="Primary asset token symbol")
    paired_token: str = Field(..., description="Paired asset token symbol for LP vaults")
    category: str = Field(..., description="Category: Yield, LP, Insurance, etc.")
    apy_min: float = Field(..., ge=0, description="Minimum expected APY")
    apy_max: float = Field(..., ge=0, description="Maximum expected APY")
    lock_period_days: int = Field(..., ge=0, description="Required lockup duration in days")
    description: str = Field(..., description="Brief summary of vault mechanics")

class VaultState(BaseModel):
    vault_id: str = Field(..., description="Unique identifier for the Vault")
    apy_current: float = Field(..., ge=0, description="Real-time APY calculation")
    tvl_usd: float = Field(..., ge=0, description="Total Value Locked in USD")
    utilisation_pct: float = Field(..., ge=0, le=100, description="Capital utilization percentage")
    health_ratio: float = Field(..., description="Risk health ratio (>1.0 is healthy)")
    alerts: List[str] = Field(default_factory=list, description="Active market alerts")

class VaultRecommendation(BaseModel):
    vault_id: str = Field(..., description="Recommended Vault ID")
    name: str = Field(..., description="Recommended Vault Name")
    apy: float = Field(..., description="Projected APY of recommendation")
    tvl: float = Field(..., description="TVL of recommended vault")
    risk: str = Field(..., description="Assessed Risk profile: low/medium/high")
    allocation_pct: float = Field(..., ge=0, le=100, description="Suggested allocation %")
    allocation_amount: float = Field(..., ge=0, description="Suggested hard amount to allocate")
