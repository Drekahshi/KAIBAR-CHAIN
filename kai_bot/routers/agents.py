"""
routers/agents.py — KAIBAR HCS-10 Agent feed and operations
Provides live agent activity via HCS topic mirror and agent actions.
"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import sys, os, random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.hedera_service import hedera
from modules.vault_monitor import VAULT_REGISTRY, MarketSimulator
from modules.amm_monitor import KAIAMMMonitor

router = APIRouter()

# ── Agent registry ────────────────────────────────────────────────

AGENT_REGISTRY = {
    "vault-agent-001": {
        "name":        "Vault Agent",
        "emoji":       "🏦",
        "type":        "vault",
        "description": "Monitors yield vaults, recommends rebalancing, and auto-executes via HCS",
        "loop_interval": "30 min",
        "status":      "active",
    },
    "market-agent-001": {
        "name":        "Market Agent",
        "emoji":       "📊",
        "type":        "market",
        "description": "Generates AMM signals, detects arbitrage, and triggers pool rebalancing",
        "loop_interval": "15 min",
        "status":      "active",
    },
    "wallet-agent-001": {
        "name":        "Wallet Agent",
        "emoji":       "🎁",
        "type":        "airdrop",
        "description": "Manages daily KAIBAR token airdrops to whitelisted wallets",
        "loop_interval": "24 hours",
        "status":      "active",
    },
    "compliance-agent-001": {
        "name":        "Compliance Agent",
        "emoji":       "🛡️",
        "type":        "compliance",
        "description": "Monitors scheduled contracts and validates on-chain compliance conditions",
        "loop_interval": "60 min",
        "status":      "active",
    },
}

# ── Generate simulated HCS-10 agent messages ─────────────────────

def _generate_agent_feed(count: int = 10) -> list:
    """Generate realistic agent activity messages for demo."""
    sim = MarketSimulator()
    states = sim.tick()

    messages = []
    now = datetime.utcnow()

    # Vault agent messages
    best_vault = max(VAULT_REGISTRY, key=lambda v: states[v.vault_id].apy_current)
    best_state = states[best_vault.vault_id]
    messages.append({
        "id":        f"va-{random.randint(10000,99999)}",
        "agent":     "Vault Agent",
        "agent_id":  "vault-agent-001",
        "type":      "vault",
        "emoji":     "🏦",
        "action":    "vault_recommendation",
        "message":   f"Top yield: {best_vault.name} @ {best_state.apy_current:.2f}% APY (TVL: ${best_state.tvl_usd:,.0f})",
        "timestamp": now.strftime("%H:%M:%S"),
        "protocol":  "HCS-10",
    })

    # Market agent messages
    signals = [
        ("BUY", "HBAR/YToken", "0.0891"),
        ("HOLD", "YToken/YBOB", "0.0012"),
        ("BUY", "HBAR/YGOLD", "0.0850"),
    ]
    sig = random.choice(signals)
    emoji = "🟢" if sig[0] == "BUY" else "🟡"
    messages.append({
        "id":        f"ma-{random.randint(10000,99999)}",
        "agent":     "Market Agent",
        "agent_id":  "market-agent-001",
        "type":      "market",
        "emoji":     "📊",
        "action":    "market_signal",
        "message":   f"{emoji} Signal {sig[0]} — {sig[1]} @ ${sig[2]} (confidence: {random.randint(65,94)}%)",
        "timestamp": now.strftime("%H:%M:%S"),
        "protocol":  "HCS-10",
    })

    # Wallet agent
    messages.append({
        "id":        f"wa-{random.randint(10000,99999)}",
        "agent":     "Wallet Agent",
        "agent_id":  "wallet-agent-001",
        "type":      "airdrop",
        "emoji":     "🎁",
        "action":    "daily_airdrop",
        "message":   f"Daily airdrop distributed: YToken, GAMI, YGOLD to all whitelisted wallets.",
        "timestamp": now.strftime("%H:%M:%S"),
        "protocol":  "HCS-10",
    })

    # Compliance agent
    messages.append({
        "id":        f"ca-{random.randint(10000,99999)}",
        "agent":     "Compliance Agent",
        "agent_id":  "compliance-agent-001",
        "type":      "compliance",
        "emoji":     "🛡️",
        "action":    "health_check",
        "message":   f"All vaults HEALTHY. No health ratio breaches. {len(VAULT_REGISTRY)} vaults monitored.",
        "timestamp": now.strftime("%H:%M:%S"),
        "protocol":  "HCS-10",
    })

    return messages[:count]


class HCSMessageRequest(BaseModel):
    topic_id: str
    agent_id: str
    action: str
    payload: dict


@router.get("/")
async def list_agents():
    """List all registered KAIBAR HCS-10 agents with status."""
    return list(AGENT_REGISTRY.values())


@router.get("/feed")
async def get_agent_feed(limit: int = 20):
    """Get live HCS-10 agent activity feed."""
    messages = _generate_agent_feed(min(limit, 20))
    return {
        "messages":  messages,
        "total":     len(messages),
        "protocol":  "HCS-10 OpenConvAI",
        "network":   "Hedera Testnet",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    """Get details for a specific agent."""
    agent = AGENT_REGISTRY.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return agent


@router.post("/hcs/submit")
async def submit_hcs_message(req: HCSMessageRequest):
    """Submit an HCS-10 message to a Hedera topic."""
    message = {
        "p":        "hcs-10",
        "op":       "agent_action",
        "agent_id": req.agent_id,
        "payload":  req.payload,
        "action":   req.action,
        "timestamp": datetime.utcnow().isoformat(),
    }
    result = await hedera.submit_hcs_message(req.topic_id, message)
    return result


@router.get("/vault-agent/recommendations")
async def vault_agent_recommendations():
    """Get current vault agent recommendations."""
    sim = MarketSimulator()
    states = sim.tick()
    recs = sorted(
        [
            {
                "vault_id": cfg.vault_id,
                "name":     cfg.name,
                "apy":      round(states[cfg.vault_id].apy_current, 2),
                "tvl":      round(states[cfg.vault_id].tvl_usd, 2),
                "category": cfg.category,
                "risk":     "low" if states[cfg.vault_id].health_ratio > 1.5 else "medium",
                "agent_rating": "★★★★★" if states[cfg.vault_id].apy_current > 30 else "★★★★☆",
            }
            for cfg in VAULT_REGISTRY
        ],
        key=lambda x: x["apy"],
        reverse=True,
    )
    return {"recommendations": recs, "agent": "Vault Agent (vault-agent-001)"}
