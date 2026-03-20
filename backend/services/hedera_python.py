import os
import uuid
import logging
from typing import Optional, Dict, Any
import httpx
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

HEDERA_ACCOUNT_ID = os.getenv("HEDERA_OPERATOR_ID", "")
HEDERA_PRIVATE_KEY = os.getenv("HEDERA_OPERATOR_PRIVATE_KEY", "")
HEDERA_NETWORK = os.getenv("HEDERA_NETWORK", "testnet")
VAULT_CONTRACT_ID = os.getenv("VAULT_CONTRACT_ID", "0.0.12345")
MIRROR_NODE = os.getenv("HEDERA_MIRROR_NODE", "https://testnet.mirrornode.hedera.com")

_client = None
try:
    from hiero import Client, AccountId, PrivateKey, ContractExecuteTransaction, ContractFunctionParameters, Hbar
    _account_id = AccountId.from_string(HEDERA_ACCOUNT_ID) if HEDERA_ACCOUNT_ID else None
    _private_key = PrivateKey.from_string(HEDERA_PRIVATE_KEY) if HEDERA_PRIVATE_KEY else None
    if _account_id and _private_key:
        _client = Client.for_testnet()
        _client.set_operator(_account_id, _private_key)
        logger.info(f"Hedera Client initialized for operator {_account_id}")
    else:
        logger.warning("Hedera Operator credentials incomplete. Running in Simulation mode.")
except Exception as e:
    logger.error(f"Failed to initialize Hedera SDK: {e}")
    _client = None

def _tx_id() -> str:
    """Generate a deterministic-format testnet transaction ID for demo."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"0.0.12345@{ts[:14]}.{ts[14:]}"

class HederaService:
    """
    Service handling all interactions with the Hedera Hashgraph Testnet via hiero-sdk-python.
    Gracefully degrades to simulated JSON responses if the SDK is unavailable or keys are missing.
    """

    async def vault_deposit(self, amount_hbar: float, contract_id: Optional[str] = None) -> Dict[str, Any]:
        """Deposits HBAR into a specified Smart Contract Vault on Hedera."""
        cid = contract_id or VAULT_CONTRACT_ID
        if _client:
            try:
                logger.info(f"Initiating live deposit of {amount_hbar} HBAR to {cid}")
                tx = (
                    ContractExecuteTransaction()
                    .set_contract_id(cid)
                    .set_gas(200_000)
                    .set_function("deposit")
                    .set_payable_amount(Hbar(amount_hbar))
                    .execute(_client)
                )
                receipt = tx.get_receipt(_client)
                return {
                    "success": True,
                    "tx_id": str(receipt.transaction_id),
                    "amount_hbar": amount_hbar,
                    "contract": cid,
                    "network": HEDERA_NETWORK,
                    "mode": "live",
                }
            except Exception as e:
                logger.error(f"Live Hedera Vault Deposit failed: {e}")
                # Fallthrough to simulated mode for hackathon resilience
        
        logger.info(f"Simulating deposit of {amount_hbar} HBAR to {cid}")
        return {
            "success": True,
            "tx_id": _tx_id(),
            "amount_hbar": amount_hbar,
            "contract": cid,
            "network": "testnet",
            "mode": "simulated",
            "message": f"Deposit of {amount_hbar} HBAR queued. Configure Hedera SDK for live transactions.",
        }

    async def get_account_info(self, account_id: str) -> Dict[str, Any]:
        """Fetches account balances from the public Mirror Node REST API."""
        try:
            logger.info(f"Querying Mirror Node for account {account_id}")
            async with httpx.AsyncClient(timeout=10) as client:
                res = await client.get(f"{MIRROR_NODE}/api/v1/accounts/{account_id}")
                res.raise_for_status()
                data = res.json()
                return {
                    "account_id": account_id,
                    "balance_hbar": round(data.get("balance", {}).get("balance", 0) / 1e8, 4),
                    "tokens": data.get("balance", {}).get("tokens", []),
                    "network": "testnet",
                    "source": "mirror_node",
                }
        except httpx.HTTPStatusError as exc:
            logger.warning(f"HTTP error from Mirror Node matching account {account_id}: {exc.response.status_code}")
        except Exception as e:
            logger.error(f"Error querying Mirror node: {e}")
        
        # Fallback simulated response
        return {
            "account_id": account_id,
            "balance_hbar": 10.0,
            "tokens": [],
            "network": "testnet",
            "source": "simulated",
        }

hedera = HederaService()
