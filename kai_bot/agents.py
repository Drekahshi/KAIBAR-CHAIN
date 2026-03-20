"""
agents.py — Multi-Agent Framework for AGENT KAI
===============================================
Defines specialized autonomous agents for different parts of the KAI ecosystem.
Each agent handles specific tasks and returns structured responses for the UI.
"""

import json
import random
import re
from datetime import datetime
from modules.tokenomics import TOKENS as TOKENOMICS_DATA
from modules.amm_monitor import KAIAMMMonitor
from modules.vault_monitor import VAULT_REGISTRY, MarketSimulator
from modules.airdrop_engine import distribute_airdrop
from modules.wallet_registry import list_wallets, register_wallet, remove_wallet
from modules.scheduler import schedule_transaction, list_scheduled

class BaseAgent:
    name: str = "Base"
    emoji: str = "🤖"
    description: str = "Standard KAI Agent"

    async def execute(self, action: str, params: dict) -> dict:
        return {"agent": self.name, "emoji": self.emoji, "text": "I process instructions.", "data": {}}

# --- Vault Agent (The Expert on Yield & Security) ---
class VaultAgent(BaseAgent):
    name = "Vault Agent"
    emoji = "🏦"
    description = "Specialist in KAI Savings, Pensions, and Yield Optimization"

    def __init__(self):
        self.simulator = MarketSimulator()

    async def execute(self, action: str, params: dict) -> dict:
        states = self.simulator.tick()
        
        if action == "list":
            output = "I've analyzed the current yield landscape in the KAI ecosystem. Here are the top performers:\n\n"
            data_list = []
            for cfg in VAULT_REGISTRY:
                s = states[cfg.vault_id]
                output += f"{self.emoji} **{cfg.name}**\n"
                output += f"   - APY: `{s.apy_current:.2f}%` | TVL: `${s.tvl_usd:,.0f}`\n"
                output += f"   - Risk: `{cfg.category.upper()}` | Status: `STABLE`\n\n"
                data_list.append({"id": cfg.vault_id, "apy": s.apy_current, "tvl": s.tvl_usd})
            return {
                "agent": self.name,
                "emoji": self.emoji,
                "text": output,
                "data": data_list
            }

        elif action == "deposit":
            vault_id = params.get("vault_id")
            amount = params.get("amount")
            # In a real app, this would call a Hedera transaction via Agent Kit
            return {
                "agent": self.name, 
                "emoji": self.emoji,
                "text": f"✔ **Transaction Processed!** I have successfully deposited `{amount} KAI` into the **{vault_id}**. Your funds are now earning yield at current rates.",
                "data": {"status": "success", "amount": amount, "vault": vault_id}
            }

        elif action == "withdraw":
            vault_id = params.get("vault_id")
            amount = params.get("amount")
            return {
                "agent": self.name,
                "emoji": self.emoji,
                "text": f"✔ **Withdrawal Complete.** Removed `{amount} KAI` from **{vault_id}**. The funds have been returned to your primary wallet.",
                "data": {"status": "success", "amount": amount, "vault": vault_id}
            }
            
        return await super().execute(action, params)

# --- Tokenomics Agent (The Data Analyst) ---
class TokenomicsAgent(BaseAgent):
    name = "Tokenomics Agent"
    emoji = "📊"
    description = "Tracks KAI supply, prices, and market health"

    async def execute(self, action: str, params: dict) -> dict:
        if action == "summary":
            output = "Here is the latest market data for the KAI ecosystem tokens:\n\n"
            for sym, t in TOKENOMICS_DATA.items():
                output += f"🔹 **{t['name']} ({sym})**\n"
                output += f"   - Price: `${t['usd_price']}` | FDV: `${(t['total_supply'] * t['usd_price']):,.0f}`\n"
                output += f"   - Category: `{t['category']}`\n\n"
            return {
                "agent": self.name,
                "emoji": self.emoji,
                "text": output,
                "data": TOKENOMICS_DATA
            }
        return await super().execute(action, params)

# --- AMM Agent (The Liquidity Specialist) ---
class AMMAgent(BaseAgent):
    name = "AMM Agent"
    emoji = "💧"
    description = "Monitors decentralized exchange pools and liquidity"

    async def execute(self, action: str, params: dict) -> dict:
        if action == "list":
            mon = KAIAMMMonitor()
            output = "Liquidity pools are currently healthy. Here's a breakdown of the deep pools:\n\n"
            pools = []
            for p_id, p_obj in mon.pools.items():
                p = p_obj.pool
                output += f"🌊 **{p.name}**\n"
                output += f"   - Liquidity: `${p.liquidity_usd:,.0f}` | 24h Vol: `${p.volume_24h_usd:,.0f}`\n"
                output += f"   - APY: `{p.apy:.2f}%` | Fees: `{p.fee_pct*100:.2f}%`\n\n"
                pools.append({"name": p.name, "apy": p.apy, "liquidity": p.liquidity_usd})
            return {
                "agent": self.name,
                "emoji": self.emoji,
                "text": output,
                "data": pools
            }
        return await super().execute(action, params)

# --- Airdrop Agent (The Growth Hacker) ---
class AirdropAgent(BaseAgent):
    name = "Airdrop Agent"
    emoji = "🎁"
    description = "Manages community distribution and rewards"

    async def execute(self, action: str, params: dict) -> dict:
        if action == "distribute":
            amount = params.get("amount", 100)
            wallets = list_wallets()
            if not wallets:
                return {"agent": self.name, "emoji": self.emoji, "text": "I can't distribute rewards without registered wallets. Please add wallets first!", "data": {}}
            
            # Simulated distribution
            distribute_airdrop(wallets, amount)
            return {
                "agent": self.name,
                "emoji": self.emoji,
                "text": f"🚀 **Mission Accomplished!** Distributed `{amount} KAI` to `{len(wallets)}` registered community wallets. Engagement metrics have been updated.",
                "data": {"wallets": len(wallets), "amount": amount}
            }
        return await super().execute(action, params)

# --- Wallet Agent (The Registry Keeper) ---
class WalletAgent(BaseAgent):
    name = "Wallet Agent"
    emoji = "👛"
    description = "Registers and secures community wallet IDs"

    async def execute(self, action: str, params: dict) -> dict:
        if action == "list":
            wallets = list_wallets()
            if not wallets:
                return {"agent": self.name, "emoji": self.emoji, "text": "The citizen registry is currently empty. No wallets are registered.", "data": []}
            
            output = f"I've retrieved the community registry. We have **{len(wallets)}** active wallets:\n\n"
            for w in wallets:
                output += f"   • `{w}`\n"
            return {"agent": self.name, "emoji": self.emoji, "text": output, "data": wallets}
        
        elif action == "register":
            wid = params.get("account_id")
            if register_wallet(wid):
                 return {"agent": self.name, "emoji": self.emoji, "text": f"✔ Citizen wallet `{wid}` successfully verified and registered into the KAI ecosystem.", "data": {"status": "new"}}
            return {"agent": self.name, "emoji": self.emoji, "text": f"ℹ Wallet `{wid}` is already in our registry. No duplicate action needed.", "data": {"status": "exists"}}
            
        return await super().execute(action, params)

# --- Core Agent (The Ecosystem Overseer) ---
class CoreAgent(BaseAgent):
    name = "Core Agent"
    emoji = "👑"
    description = "Master coordinator for the KAI ecosystem"

    async def execute(self, action: str, params: dict) -> dict:
        if action == "dashboard":
            wallets = list_wallets()
            vault_sim = MarketSimulator()
            vault_states = vault_sim.tick()
            total_vault_tvl = sum(s.tvl_usd for s in vault_states.values())
            
            kai_price = TOKENOMICS_DATA.get("KAI", {}).get("usd_price", 0.00042)
            
            output = "🏰 **KAI Ecosystem Executive Summary**\n"
            output += f"───────────────────\n"
            output += f"🌐 **Network Status**: `OPERATIONAL`\n"
            output += f"👥 **Active Citizens**: `{len(wallets)}` Wallets\n"
            output += f"💰 **Total Value Locked**: `${total_vault_tvl:,.2f}`\n"
            output += f"📈 **KAI Price**: `${kai_price:.6f}`\n"
            output += f"───────────────────\n"
            output += "I can help you with specific details on **vaults**, **liquidity**, or **tokenomics**. What's next?"
            
            return {
                "agent": self.name,
                "emoji": self.emoji,
                "text": output,
                "data": {
                    "wallets": len(wallets),
                    "tvl": total_vault_tvl,
                    "price": kai_price
                }
            }
        return await super().execute(action, params)

# --- Orchestrator (The Hive Mind) ---
class AgentOrchestrator:
    def __init__(self, fallback_agent=None):
        self.agents = {
            "vault": VaultAgent(),
            "tokens": TokenomicsAgent(),
            "amm": AMMAgent(),
            "airdrop": AirdropAgent(),
            "wallet": WalletAgent(),
            "core": CoreAgent()
        }
        self.fallback = fallback_agent

    async def process_query(self, query: str) -> dict:
        q = query.lower()
        
        # 1. Dashboard / Ecosystem Summary routing
        if any(w in q for w in ["ecosystem", "status", "dashboard", "overview", "summary", "how are we doing"]):
            return await self.agents["core"].execute("dashboard", {})

        # 2. Simple routing logic
        if any(w in q for w in ["vault", "yield", "apy", "save", "pension", "insurance", "deposit", "withdraw"]):
            agent = self.agents["vault"]
            if "deposit" in q:
                 # Extract amount and vault
                 amount = re.search(r'(\d+)', q)
                 amount = amount.group(1) if amount else "500"
                 # Find vault keyword
                 vault = next((v.vault_id for v in VAULT_REGISTRY if v.vault_id.lower() in q or v.name.lower() in q), "YT_VAULT")
                 return await agent.execute("deposit", {"vault_id": vault, "amount": amount})
            elif "withdraw" in q:
                 amount = re.search(r'(\d+)', q)
                 amount = amount.group(1) if amount else "100"
                 vault = next((v.vault_id for v in VAULT_REGISTRY if v.vault_id.lower() in q or v.name.lower() in q), "YT_VAULT")
                 return await agent.execute("withdraw", {"vault_id": vault, "amount": amount})
            return await agent.execute("list", {})

        if any(w in q for w in ["token", "supply", "price", "fdv", "cap"]):
            return await self.agents["tokens"].execute("summary", {})

        if any(w in q for w in ["amm", "pool", "liquidity", "dex"]):
            return await self.agents["amm"].execute("list", {})

        if any(w in q for w in ["airdrop", "distribute", "reward"]):
            amount = re.search(r'(\d+)', q)
            amount = int(amount.group(1)) if amount else 100
            return await self.agents["airdrop"].execute("distribute", {"amount": amount})

        if any(w in q for w in ["wallet", "register", "address"]):
            if "list" in q or "show" in q or "wallets" in q:
                return await self.agents["wallet"].execute("list", {})
            # Try to find a Hedera ID like 0.0.123
            match = re.search(r'(0\.0\.\d+)', q)
            if match:
                return await self.agents["wallet"].execute("register", {"account_id": match.group(1)})
            return await self.agents["wallet"].execute("list", {})

        # Fallback to general AI chat if enabled, otherwise a neutral agent response
        if self.fallback:
            # Smart Context Injection: Fetch real-time data to ground the AI
            try:
                vault_sim = MarketSimulator()
                vault_states = vault_sim.tick()
                total_tvl = sum(s.tvl_usd for s in vault_states.values())
                kai_price = TOKENOMICS_DATA.get("KAI", {}).get("usd_price", "Unknown")
                wallet_count = len(list_wallets())
                
                context = (
                    f"[SYSTEM CONTEXT: TVL=${total_tvl:,.0f}, KAI_PRICE=${kai_price}, ACTIVE_WALLETS={wallet_count}. "
                    f"Specialist agents are available for 'vaults', 'tokens', 'amm', and 'wallets'.]"
                )
                enriched_query = f"{context}\nUser: {query}"
                response = await self.fallback.chat(enriched_query)
            except Exception as e:
                print(f"Context injection failed: {e}")
                response = await self.fallback.chat(query)

            return {
                "agent": "Agent KAI",
                "emoji": "🤖",
                "text": response,
                "data": {}
            }
        
        return {
            "agent": "Agent KAI",
            "emoji": "🤖",
            "text": "I'm not sure which specialist should handle that. Try asking about **vaults**, **tokenomics**, **liquidity pools**, or **wallets**.",
            "data": {}
        }
