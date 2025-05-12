import asyncio
import os
from dotenv import load_dotenv
from .realtime_client import RealtimeClient

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

INSTRUCTIONS = """
You are a kind person and you are talking to someone you just met. 
Give brief answers so the conversation goes naturally.
Also, start in English, but remember to then answer accordingly to the user's language.
"""

async def main():
    client = RealtimeClient(
        api_key=OPENAI_API_KEY, 
        instructions=INSTRUCTIONS, 
        voice="alloy"
        )
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())
