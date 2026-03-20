"""
ai_service.py
──────────────────────────────────────────────────────────────────
KAIBAR AI — Gemini (primary) + Ollama (fallback)
Provides investment strategy, vault analysis, and conversational AI.
"""
from __future__ import annotations
import os
import httpx
from typing import Optional

try:
    import google.generativeai as genai
    _GEMINI_AVAILABLE = True
except ImportError:
    _GEMINI_AVAILABLE = False

GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "qwen:0.5b")

KAIBA_SYSTEM_CONTEXT = """
You are KAIBAR AI — an intelligent DeFi financial advisor for the KAIBAR ecosystem on Hedera Hashgraph.
You help users with:
- Investment strategy recommendations across yield vaults
- Vault APY analysis and comparison
- Token portfolio optimization (YToken, YGOLD, GAMI, YBOB, KAI)
- Insurance, pension, and trust planning
- Understanding Hedera DeFi concepts
- Bonzo Finance integration guidance

Token ecosystem:
- YToken (YTK): BTC/HBAR exposure + multi-strategy DeFi yield (22–38% APY)
- YGOLD: gold & infrastructure bond exposure (26–55% APY)
- GAMI: community rewards and social DeFi mining (12–22% APY)
- YBOB: algorithmic stablecoin for liquidity and payments
- KAI: ecosystem governance and utility token

Products available:
- Vaults (YToken, YGOLD, MMF, Insurance, Pension, Flash Loans)
- Bonzo Finance DEX vaults for BTC.HBAR LP farming
- Hedera Scheduled Service for trust/pension automation
- HCS-10 autonomous agents (Vault, Market, Wallet, Compliance)
- M-Pesa onramp (fiat to HBAR) and X402 QR payments

Always be concise, actionable, and Web3-friendly. Recommend strategies based on user's risk tolerance.
"""

# ── Gemini ──────────────────────────────────────────────────────

def _init_gemini():
    if not _GEMINI_AVAILABLE or not GEMINI_API_KEY:
        return None
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        return genai.GenerativeModel("gemini-1.5-flash")
    except Exception:
        return None

_gemini_model = _init_gemini()

async def gemini_query(prompt: str) -> Optional[str]:
    if not _gemini_model:
        return None
    try:
        response = _gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return None

# ── Ollama ──────────────────────────────────────────────────────

async def ollama_query(prompt: str) -> Optional[str]:
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            res = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            )
            if res.status_code == 200:
                return res.json().get("response", "")
    except Exception:
        pass
    return None

# ── Public interface ─────────────────────────────────────────────

async def ai_query(user_query: str, context: Optional[dict] = None) -> str:
    """Query AI with optional context injection."""
    ctx = KAIBA_SYSTEM_CONTEXT
    if context:
        ctx += f"\n\n[Live User Data]: {context}"
    prompt = f"{ctx}\n\nUser: {user_query}\n\nKAIBAR AI:"
    
    result = await gemini_query(prompt)
    if not result:
        result = await ollama_query(prompt)
    if not result:
        result = (
            "⚠️ AI service temporarily unavailable. "
            "Please check your Gemini API key or ensure Ollama is running locally.\n\n"
            "For now: the YToken Vault at 22–38% APY is our top performer, "
            "with low risk and BTC.HBAR backing."
        )
    return result

async def analyze_vaults(vaults: list) -> str:
    vault_summary = "\n".join([
        f"- {v.get('name', v.get('id', ''))}: APY {v.get('apy', 0):.2f}%, "
        f"TVL ${v.get('tvl', 0):,.0f}, Risk: {v.get('risk', 'medium')}"
        for v in vaults
    ])
    prompt = (
        f"{KAIBA_SYSTEM_CONTEXT}\n\n"
        f"Available KAIBAR vaults:\n{vault_summary}\n\n"
        f"Analyze the top opportunities and suggest a 3-step allocation strategy "
        f"for a moderate-risk investor with $1000. Be concise."
    )
    result = await gemini_query(prompt)
    if not result:
        result = await ollama_query(prompt)
    return result or "APY data loaded. Top pick: YToken Vault (22–38% APY, AI-managed, low risk)."

async def get_strategy_recommendation(balance: float, risk_profile: str) -> str:
    prompt = (
        f"{KAIBA_SYSTEM_CONTEXT}\n\n"
        f"User balance: ${balance:.2f} HBAR equivalent\n"
        f"Risk profile: {risk_profile}\n\n"
        f"Provide a 3-point investment strategy for this user in the KAIBAR ecosystem. Keep it under 100 words."
    )
    result = await gemini_query(prompt)
    if not result:
        result = await ollama_query(prompt)
    return result or f"With ${balance:.0f} and {risk_profile} risk: 50% YToken Vault, 30% MMF, 20% YGOLD Bond. Target APY: ~28%."
