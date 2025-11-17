import os
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from .my_realtime_client import MyRealtimeClient
from .utils import load_prompt
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGUAGE = os.getenv("LANGUAGE")

app = FastAPI()

# CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # FE's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    client = MyRealtimeClient(
        websocket=websocket,
        api_key=OPENAI_API_KEY,
        instructions=load_prompt("instructions.txt").format(l1=LANGUAGE, l2=LANGUAGE),
        voice="sage"
    )

    async def receive_from_frontend():
        async for data in websocket.iter_json():
            print("📨 Text received from browser:", data)
            if data.get("type") == "text":
                await client.send_text(text=data["data"])

    try:
        await asyncio.gather(
            client.run(),            # Listens to OpenAI and forwards to browser
            receive_from_frontend()  # Listens to the browser and forwards to OpenAI
        )
    except Exception as e:
        print("Error in websocket_server.py:", e)
    finally:
        await client.clean_up()
