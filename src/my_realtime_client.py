import json
from .realtime_client import RealtimeClient
from fastapi import WebSocket
from pydub import AudioSegment
import io
import base64

class MyRealtimeClient(RealtimeClient):
    """
    Client extending functionality of base client 'RealtimeClient' (interaction with Realtime OpenAI API via WebSocket)
    to integrate with a FastAPI WebSocket connection.
    """
    def __init__(self, websocket: WebSocket, **kwargs):
        """
        Initializes client with a FastAPI WebSocket and other parameters

        websocket (WebSocket): WebSocket active with client
        kwargs: additional arguments passed to the base client
        """
        super().__init__(**kwargs)
        self.websocket = websocket


    async def handle_event(self, event: dict):
        """
        Handles specific events received from the Realtime API connection
        Filters by event type and sends messages in text format to the client via WebSocket

        event (dict): Event received from OpenAI in JSON format
        """
        event_type = event.get("type")
        print("🔁 Received from OpenAI:", event_type)

        if event_type in ["response.audio_transcript.done", "conversation.item.input_audio_transcription.completed"]:
            transcript = event.get("transcript", "No transcript available.")
            print("📝 Transcript:", transcript)
            await self.websocket.send_json({"text": transcript})

        if event_type == 'response.audio.delta':
            delta_base64 = event.get('delta')
            if delta_base64:
                # Decode base64 PCM
                raw_pcm = base64.b64decode(delta_base64)
                # Create AudioSegment from raw PCM
                pcm_audio = AudioSegment(
                    data=raw_pcm,
                    sample_width=2,   
                    frame_rate=24000,    
                    channels=1           
                )
                # Export to MP3 in memory
                buffer = io.BytesIO()
                pcm_audio.export(buffer, format="mp3")
                mp3_bytes = buffer.getvalue()
                mp3_base64 = base64.b64encode(mp3_bytes).decode("utf-8")
                await self.websocket.send_json({
                    "type": "audio",
                    "data": mp3_base64
                })
        
        if event_type == 'response.audio.done':
            await self.websocket.send_json({"type": "audio_done"})


    async def run(self):
        """
        Executes main Realtime client cycle: connects, listens for incoming events and passes them to the corresponding handler
        It also handles errors and performs end-of-session cleanup.
        """
        await self.connect()
        try:
            async for message in self.ws:
                event = json.loads(message)
                await self.handle_event(event)
        except Exception as e:
            print("Error my_realtime_client.py:", e)
        finally:
            await self.clean_up()
