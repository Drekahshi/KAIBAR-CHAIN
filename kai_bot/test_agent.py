import os
import asyncio
from hedera_agent_kit import HederaAgentKit, HederaConversationalAgent
from config import HEDERA_ACCOUNT_ID, HEDERA_PRIVATE_KEY, HEDERA_NETWORK, ANTHROPIC_API_KEY, OPENROUTER_API_KEY

async def main():
    if not HEDERA_ACCOUNT_ID or not HEDERA_PRIVATE_KEY:
        print("Missing required environment variables for Hedera connection.")
        return
        
    if not ANTHROPIC_API_KEY and not OPENROUTER_API_KEY:
        print("Missing required environment variables for AI (Anthropic or OpenRouter).")
        return

    try:
        # Initialize the kit with your Hedera credentials
        kit = HederaAgentKit(
            account_id=HEDERA_ACCOUNT_ID,
            private_key=HEDERA_PRIVATE_KEY,
            network=HEDERA_NETWORK,
        )

        if ANTHROPIC_API_KEY:
            # Create a conversational agent backed by Claude
            agent = HederaConversationalAgent(
                kit=kit,
                llm_provider="anthropic",
                api_key=ANTHROPIC_API_KEY,
            )
        elif OPENROUTER_API_KEY:
            # Create a conversational agent backed by OpenRouter
            os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
            agent = HederaConversationalAgent(
                kit=kit,
                llm_provider="openai",
                api_key=OPENROUTER_API_KEY,
            )

        # Ask it a natural language question
        print("Asking Agent: What is my HBAR balance?")
        response = await agent.chat("What is my HBAR balance?")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error testing AI agent: {e}")

if __name__ == "__main__":
    asyncio.run(main())
