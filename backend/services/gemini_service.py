import google.generativeai as genai
import os
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        logger.info("Gemini 1.5 Flash Model initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini Model: {e}")
        model = None
else:
    logger.warning("GEMINI_API_KEY not found in environment variables. Gemini AI service will be simulated/offline.")
    model = None

KAIBA_SYSTEM_CONTEXT = """
You are KAIBA AI — an intelligent DeFi financial advisor running natively on Hedera.
Your goal is to help users manage their token portfolios securely.
Token ecosystem: YToken (BTC/HBAR exposure), YGold (gold exposure), GAMI (community rewards), KAIBAR (utility), KYBOB (stablecoin).
Products: Bonzo Vaults, KAIBA native Insurance (staking-funded), Trust (Hedera Scheduled Service), Pension (long-term staking).
Keep responses concise, very actionable, avoiding over-explaining and focusing on Hedera mechanics.
"""

async def query_investment_strategy(
    user_query: str,
    portfolio_context: Optional[Dict[str, Any]] = None
) -> str:
    """Passes user query combined with HTS account info to Gemini for financial planning."""
    if not model:
        logger.error("Attempted Gemini query but model is offline.")
        return "I am currently offline due to missing Gemini API configuration. Check your .env file."
        
    context = KAIBA_SYSTEM_CONTEXT
    if portfolio_context:
        context += f"\n\nUser's current Hedera portfolio: {portfolio_context}"
    
    prompt = f"{context}\n\nUser Objective: {user_query}\n\nProvide Expert Analysis:"
    
    try:
        logger.info("Generating investment strategy via Gemini...")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Generate content error: {e}", exc_info=True)
        return f"AI Service temporarily struggling: {str(e)}"

async def analyze_vault_opportunities(vaults: List[Dict[str, Any]]) -> str:
    """Takes active vault states and queries Gemini for highest-efficacy descriptions."""
    if not model:
        return "Configure Gemini API key."
        
    vault_summary = "\n".join([
        f"- {v.get('name', 'Vault')}: APY {v.get('apy', 0)}%, Risk: {v.get('risk', 'unknown')}, Protocol: {v.get('protocol', 'KAIBA')}"
        for v in vaults
    ])
    prompt = f"{KAIBA_SYSTEM_CONTEXT}\n\nCurrently active vaults on network:\n{vault_summary}\n\nAnalyze these opportunities and output a short, strategic recommendation."
    
    try:
        logger.info("Generating vault analysis via Gemini...")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Vault analysis error: {e}")
        return "Could not process vault analysis."

async def get_apy_recommendation(user_balance: float, risk_profile: str) -> str:
    """Suggests an exact portfolio split based on APY/Risk profiles."""
    if not model:
        return "Configure Gemini API key."
    prompt = f"{KAIBA_SYSTEM_CONTEXT}\n\nUser Capital: ${user_balance:,.2f}\nRisk profile: {risk_profile}\n\nProvide the optimal numerical percentage allocation strategy."
    try:
        logger.info(f"Generating APY recommendation for $ {user_balance} / {risk_profile}")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"APY Recommendation error: {e}")
        return "APY Recommendation generation failed."
