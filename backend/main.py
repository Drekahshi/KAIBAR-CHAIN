import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers import vaults, agents, analytics, airdrop, ai

# Configure global logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("kaiba_backend")

app = FastAPI(
    title="KAIBA Backend MVP",
    description="Python FastAPI backend for KAIBAR built for Hedera Hackathon.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "message": str(exc)}
    )

app.include_router(vaults.router, prefix="/api/vaults", tags=["Vaults"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics & AMM"])
app.include_router(airdrop.router, prefix="/api/airdrop", tags=["Airdrop"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI Strategy"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up KAIBA Backend Engine on Hedera Testnet...")

@app.get("/", tags=["Health"])
def health():
    """Healthcheck endpoint for Kubernetes or load balancers."""
    return {
        "status": "ok",
        "platform": "KAIBA DeFi",
        "network": "Hedera Testnet",
        "message": "Backend engine is running securely for judges review!"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
