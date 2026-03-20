from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class AgentAction(BaseModel):
    agent_id: str = Field(..., description="ID of the HCS-10 Agent executing action")
    action_type: str = Field(..., description="Type of action: swap, rebalance, allocate, etc.")
    payload: Dict[str, Any] = Field(..., description="Data payload for action execution")
    hcs_topic_id: Optional[str] = Field(None, description="Related Hedera Consensus Service Topic")
    status: str = Field("success", description="Status of the action execution")

class AiQueryRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=1000, description="User question for KAIBA AI")
    portfolio_context: Optional[Dict[str, Any]] = Field(None, description="Optional user portfolio dump for context-aware answers")
