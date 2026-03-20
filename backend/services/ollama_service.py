import httpx
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

KAIBA_SYSTEM_CONTEXT = "You are KAIBA AI — an intelligent DeFi financial advisor for KAIBAR on Hedera."

async def query_local_strategy(user_query: str, portfolio_context: Optional[Dict[str, Any]] = None) -> str:
    """
    Query the locally hosted Ollama model for offline/privacy-focused generation.
    """
    context = KAIBA_SYSTEM_CONTEXT
    if portfolio_context:
        context += f"\n\nPortfolio details: {portfolio_context}"
        
    prompt = f"{context}\n\nUser: {user_query}\n\nKAIBA AI:"
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    logger.info(f"Dispatching query to local Ollama via {OLLAMA_BASE_URL} (Model: {OLLAMA_MODEL})")
    try:
        async with httpx.AsyncClient(timeout=45) as client: # Local LLMs can be slow
            res = await client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
            res.raise_for_status()
            
            data = res.json()
            response_text = data.get("response")
            if response_text:
                return response_text
            else:
                logger.warning(f"Ollama returned malformed JSON: {data}")
                return "Ollama Error: Could not parse completion."
                
    except httpx.HTTPStatusError as exc:
        logger.error(f"Ollama HTTP {exc.response.status_code} Error: {exc.response.text}")
        return f"Ollama execution failed: HTTP {exc.response.status_code}"
    except httpx.RequestError as exc:
        logger.warning(f"Ollama Local Server Unreachable: {exc}")
        return "Local AI Service is currently offline. Ensure Ollama is running."
    except Exception as e:
        logger.error(f"Unexpected Local AI Error: {e}")
        return f"Unexpected Local AI Error: {str(e)}"
