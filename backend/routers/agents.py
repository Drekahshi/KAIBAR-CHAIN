import logging
from fastapi import APIRouter, HTTPException
from models.agent import AgentAction
import httpx
import os

logger = logging.getLogger(__name__)
router = APIRouter()

MIRROR_NODE = os.getenv("HEDERA_MIRROR_NODE", "https://testnet.mirrornode.hedera.com")
FEED_TOPIC_ID = os.getenv("HCS_FEED_TOPIC_ID", "0.0.12345")

@router.get("/feed")
async def get_agent_feed():
    """Reads the real-time HCS-10 Topic via Hedera Mirror Node. Returns simulation if failing."""
    logger.info(f"Requesting Agent Feed from HCS Topic: {FEED_TOPIC_ID}")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            res = await client.get(
                f"{MIRROR_NODE}/api/v1/topics/{FEED_TOPIC_ID}/messages",
                params={"limit": 20, "order": "desc"}
            )
            res.raise_for_status()
            
            messages = res.json().get("messages", [])
            if len(messages) > 0:
                feed = []
                for m in messages:
                    # In a fully deployed MVP we'd decode base64 topic messages here securely
                    feed.append({
                        "sequence_number": m.get("sequence_number"),
                        "consensus_timestamp": m.get("consensus_timestamp"),
                        "message": m.get("message")
                    })
                return {"messages": feed, "source": "network"}
    except httpx.RequestError as e:
        logger.warning(f"Could not reach Hedera mirror node: {e}. Falling back to simulations.")
    except Exception as e:
        logger.warning(f"Error querying HCS topic: {e}. Falling back to simulation mode.")

    # High-quality simulation response demonstrating what the dApp expects
    return {
        "source": "simulated",
        "messages": [
            {
                "id": "1",
                "agent": "vault-agent-001",
                "action": "vault_recommendation",
                "message": "Yield opportunity identified: USDC/HBAR Pool increased to 14.5% APY on Bonzo Finance.",
                "timestamp": "Just now",
                "type": "vault"
            },
            {
                "id": "2",
                "agent": "market-agent-001",
                "action": "amm_rebalance",
                "message": "BUY pressure detected -> Rebalancing HBAR/USD targets at $0.085 execution price.",
                "timestamp": "5 mins ago",
                "type": "market"
            },
            {
                "id": "3",
                "agent": "compliance-agent",
                "action": "pension_audit",
                "message": "Routine Smart Contract audit complete. KAIBA Pension vault solvent ratio: 1.045.",
                "timestamp": "22 mins ago",
                "type": "compliance"
            }
        ]
    }
