import asyncio
import os
from dotenv import load_dotenv
from .realtime_client import RealtimeClient

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

INSTRUCTIONS = """
Eres una persona amable. 
Estas conversando con alguien que acabas de conocer.
Da respuestas breves para que la conversación fluya y la otra persona pueda contestar.
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
