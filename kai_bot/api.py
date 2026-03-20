"""
api.py — KAIBAR FastAPI Backend (ENHANCED)
═══════════════════════════════════════════════════════════════════
Full-stack backend for KAIBAR DeFi platform on Hedera Hashgraph.

Endpoints:
  /api/dashboard          — Ecosystem overview
  /api/chat               — Agent KAI conversational AI
  /api/wallets            — Wallet registry (CRUD)
  /api/tokenomics         — Token ecosystem data
  /api/amm (legacy)       — Legacy AMM monitor pools
  /api/vaults/*           — Vault operations (deposit/withdraw/project/allocate/pension/insurance/flash)
  /api/analytics/*        — AMM pools, swap quotes, arbitrage, ecosystem summary
  /api/agents/*           — HCS-10 agent feed and operations
  /api/airdrop/*          — Whitelist + airdrop schedule + distribution
  /api/ai/*               — AI investment strategy (Gemini + Ollama)
  /api/payments/*         — M-Pesa STK push + X402 QR payments
  /api/hedera/*           — Hedera SDK operations (account, HSS, HCS, network)

Run:
  cd kai_bot
  python api.py
  OR: uvicorn api:app --reload --port 8000

═══════════════════════════════════════════════════════════════════
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
import os
import sys
import httpx
from datetime import datetime

# ── Path setup ──────────────────────────────────────────────────
_BOT_DIR = os.path.dirname(os.path.abspath(__file__))
if _BOT_DIR not in sys.path:
    sys.path.insert(0, _BOT_DIR)

# ── Core imports ────────────────────────────────────────────────
try:
    from modules.tokenomics import TOKENS as TOKENOMICS_DATA
    from modules.amm_monitor import KAIAMMMonitor
    from modules.vault_monitor import VAULT_REGISTRY, MarketSimulator
    from modules.airdrop_engine import distribute_airdrop
    from kai_bot import _init_agent, list_wallets, _load_schedules, register_wallet, remove_wallet
    from agents import AgentOrchestrator
    from config import AI_PROVIDER, OLLAMA_MODEL, OLLAMA_BASE_URL
except ImportError as e:
    print(f"Error importing core modules: {e}")
    sys.exit(1)

# ── Router imports ───────────────────────────────────────────────
try:
    from routers.vaults    import router as vaults_router
    from routers.analytics import router as analytics_router
    from routers.agents    import router as agents_router
    from routers.airdrop   import router as airdrop_router
    from routers.ai        import router as ai_router
    from routers.payments  import router as payments_router
    from routers.hedera    import router as hedera_router
    _ROUTERS_AVAILABLE = True
except ImportError as e:
    print(f"⚠  Router import error: {e}. Some endpoints may be unavailable.")
    _ROUTERS_AVAILABLE = False

# ── App init ────────────────────────────────────────────────────
app = FastAPI(
    title="KAIBAR DeFi API",
    description="Full-stack Hedera DeFi backend for KAIBAR Hackathon — HCS-10 · HSS · Smart Contracts · Bonzo Vaults",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow frontend on any port during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static frontend mount (legacy)
if os.path.isdir(os.path.join(_BOT_DIR, "app")):
    app.mount("/app", StaticFiles(directory="app", html=True), name="app")

# ── Agent setup ─────────────────────────────────────────────────
fallback = _init_agent()
if fallback:
    if AI_PROVIDER == "ollama":
        print(f"🦙 Ollama mode — model: {OLLAMA_MODEL} @ {OLLAMA_BASE_URL}")
    else:
        print("🤖 Cloud AI agent initialized.")
else:
    print("⚠️  No AI fallback. Set AI_PROVIDER=ollama or GEMINI_API_KEY in .env.")

orchestrator = AgentOrchestrator(fallback_agent=fallback)

# ── Mount new routers ────────────────────────────────────────────
if _ROUTERS_AVAILABLE:
    app.include_router(vaults_router,    prefix="/api/vaults",    tags=["Vaults"])
    app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics & AMM"])
    app.include_router(agents_router,    prefix="/api/agents",    tags=["HCS-10 Agents"])
    app.include_router(airdrop_router,   prefix="/api/airdrop",   tags=["Airdrops"])
    app.include_router(ai_router,        prefix="/api/ai",        tags=["AI Strategy"])
    app.include_router(payments_router,  prefix="/api/payments",  tags=["Payments"])
    app.include_router(hedera_router,    prefix="/api/hedera",    tags=["Hedera SDK"])
    print("✅ All KAIBAR routers mounted.")

# ══════════════════════════════════════════════════════════════════
#  LEGACY / CORE ENDPOINTS (preserved for frontend compatibility)
# ══════════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    message: str

class WalletRequest(BaseModel):
    account_id: str


@app.get("/", tags=["Health"])
async def root():
    return {
        "status":   "ok",
        "platform": "KAIBAR DeFi",
        "version":  "2.0.0",
        "network":  os.getenv("HEDERA_NETWORK", "testnet"),
        "docs":     "/docs",
        "features": [
            "Hedera Smart Contracts", "HCS-10 OpenConvAI Agents",
            "Hedera Scheduled Service", "Bonzo DEX Vaults",
            "M-Pesa Payments", "X402 QR Payments",
            "AI Strategy (Gemini + Ollama)",
        ],
    }


@app.get("/api/dashboard", tags=["Dashboard"])
async def get_dashboard():
    """Main dashboard data for the home page."""
    wallets  = list_wallets()
    schedules = _load_schedules()
    pending  = [s for s in schedules if s.get("status") == "pending"]
    sim      = MarketSimulator()
    states   = sim.tick()
    total_tvl = sum(s.tvl_usd for s in states.values())
    top_vault  = max(states.items(), key=lambda x: x[1].apy_current)

    return {
        "network":         os.getenv("HEDERA_NETWORK", "testnet"),
        "wallets_count":   len(wallets),
        "schedules_count": len(pending),
        "status":          "Operational",
        "total_tvl_usd":   round(total_tvl, 2),
        "top_apy_vault":   top_vault[0],
        "top_apy_pct":     round(top_vault[1].apy_current, 2),
        "active_vaults":   len(VAULT_REGISTRY),
        "hbar_usd":        0.09,
        "kai_price":       TOKENOMICS_DATA.get("KAI", {}).get("usd_price", 0.00042),
        "timestamp":       datetime.now().isoformat(),
    }


@app.get("/api/tokenomics", tags=["Tokenomics"])
async def get_tokenomics():
    """Full tokenomics data for all KAI ecosystem tokens."""
    return TOKENOMICS_DATA


@app.get("/api/amm", tags=["Legacy AMM"])
async def get_amm():
    """Legacy AMM monitor pools (backward compatible)."""
    mon = KAIAMMMonitor()
    pools = []
    for p_id, p_obj in mon.pools.items():
        pools.append({
            "id":         p_id,
            "name":       p_obj.pool.name,
            "liquidity":  p_obj.pool.liquidity_usd,
            "apy":        p_obj.pool.apy,
            "volume_24h": p_obj.pool.volume_24h_usd,
        })
    return pools


@app.get("/api/vaults-legacy", tags=["Legacy Vaults"])
async def get_vaults_legacy():
    """Legacy vault list (backward compatible — use /api/vaults/ for full data)."""
    sim = MarketSimulator()
    states = sim.tick()
    return [
        {
            "id":          cfg.vault_id,
            "name":        cfg.name,
            "apy":         round(states[cfg.vault_id].apy_current, 2),
            "tvl":         round(states[cfg.vault_id].tvl_usd, 2),
            "utilization": round(states[cfg.vault_id].utilisation_pct, 2),
            "health":      round(states[cfg.vault_id].health_ratio, 4),
        }
        for cfg in VAULT_REGISTRY
    ]


@app.post("/api/chat", tags=["Chat"])
async def chat(request: ChatRequest):
    """Agent KAI conversational AI — routes to specialist agents."""
    try:
        result = await orchestrator.process_query(request.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/wallets", tags=["Wallets"])
async def get_wallets():
    """Get all registered wallet addresses."""
    return list_wallets()


@app.post("/api/wallets", tags=["Wallets"])
async def add_wallet(request: WalletRequest):
    """Register a wallet to the airdrop whitelist."""
    if register_wallet(request.account_id):
        return {"message": f"Registered {request.account_id}", "status": "new"}
    return {"message": "Already registered", "status": "exists"}


@app.delete("/api/wallets/{account_id}", tags=["Wallets"])
async def delete_wallet(account_id: str):
    """Remove a wallet from the registry."""
    if remove_wallet(account_id):
        return {"message": f"Removed {account_id}"}
    raise HTTPException(status_code=404, detail="Wallet not found")


# ══════════════════════════════════════════════════════════════════
#  STARTUP
# ══════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def on_startup():
    print("\n" + "═" * 60)
    print("  KAIBAR DeFi API v2.0.0 — Starting up…")
    print("  Hedera Network: " + os.getenv("HEDERA_NETWORK", "testnet"))
    print("  Docs: http://localhost:8000/docs")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
