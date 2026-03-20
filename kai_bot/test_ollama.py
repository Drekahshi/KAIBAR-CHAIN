import httpx
import asyncio
import os

async def main():
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            res = await client.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "qwen3.5:0.8b",
                    "messages": [{"role": "user", "content": "What is Hedera?"}],
                    "stream": False
                }
            )
            res.raise_for_status()
            print("SUCCESS:")
            print(res.json()["message"]["content"])
        except Exception as e:
            import traceback
            print("ERROR:")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
