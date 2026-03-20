from pydantic import BaseModel, Field
from typing import List, Any

class TokenDistribution(BaseModel):
    token_id: str = Field(..., description="Hedera Token Service ID (0.0.X)")
    symbol: str = Field(..., description="Token Symbol (YTK, YGD, etc)")
    decimals: int = Field(..., ge=0, le=18, description="Token decimals")
    amount: float = Field(..., ge=0, description="Amount to distribute")
    
class AirdropStatus(BaseModel):
    account_id: str = Field(..., description="Hedera Account ID (0.0.X)")
    eligible: bool = Field(..., description="Is the account whitelisted and eligible?")
    balance: float = Field(..., description="Current HBAR balance")
    tokens: List[Any] = Field(default_factory=list, description="Current HTS token balances")
