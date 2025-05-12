from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import asyncio
from .my_realtime_client import MyRealtimeClient
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()
app.mount("/static", StaticFiles(directory="public"), name="static")


@app.get("/")
async def get_index():
    return FileResponse("public/index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    client = MyRealtimeClient(
        websocket=websocket,
        api_key=OPENAI_API_KEY,
        instructions="You're kind, friendly and helpful. Please start speaking in English, and then answer accordingly in the language of the user.",
        voice="sage"
    )

    async def receive_from_frontend():
        async for data in websocket.iter_json():
            print("📨 Texto recibido del navegador:", data)
            if data.get("type") == "text":
                await client.send_text(text=data["data"])

    try:
        await asyncio.gather(
            client.run(),            # escucha a OpenAI y reenvía al navegador
            receive_from_frontend()  # escucha al navegador y reenvía a OpenAI
        )
    except Exception as e:
        print("Error websocket_server.py:", e)
    finally:
        await client.clean_up()
