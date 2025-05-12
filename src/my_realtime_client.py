import json
import json
import websockets
from fastapi import WebSocket
from pydub import AudioSegment
import io
import base64

class MyRealtimeClient:
    """
    Client to interact with the OpenAI Realtime API via WebSocket and to integrate with a FastAPI WebSocket connection.
    """
    def __init__(self, api_key: str, instructions: str, voice: str, websocket: WebSocket = None):
        """
        Initializes client with a FastAPI WebSocket and other parameters
        """
        self.url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "OpenAI-Beta": "realtime=v1"
        }
        self.ws = None
        self.websocket = websocket
        self.instructions = instructions
        self.voice = voice

        # VAD configuration (enabled by default)
        self.VAD_turn_detection = True
        self.VAD_config = {
            "type": "server_vad",
            "threshold": 0.8,
            "prefix_padding_ms": 300,
            "silence_duration_ms": 1000,
            "interrupt_response": False
        }

        # Session configuration
        self.session_config = {
            "modalities": ["audio", "text"],
            "instructions": self.instructions,
            "voice": self.voice,
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "turn_detection": self.VAD_config if self.VAD_turn_detection else None,
            "input_audio_transcription": {"model": "whisper-1"},
            "temperature": 0.6,
        }

    
    async def connect(self):
        """
        Connects to OpenAI Realtime WebSocket and sends session config
        """
        self.ws = await websockets.connect(self.url, extra_headers=self.headers)
        await self.send_event({"type": "session.update", "session": self.session_config})
        await self.send_event({"type": "response.create"})


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

    
    async def send_event(self, event):
        """
        Sending events to WebSocket server

        event: Event to send (from user)
        """
        await self.ws.send(json.dumps(event))
        print(f"Event sent: {event['type']}")

    
    async def send_text(self, text):
        """
        Sending text to WebSocket server

        text: Text message to send
        """
        await self.send_event({
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": text}]
            }
        })
        await self.send_event({"type": "response.create"})


    async def clean_up(self):
        """
        Closes the WebSocket connection
        """
        if self.ws:
            await self.ws.close()


    async def run(self):
        """
        Establishes a connection to the OpenAI Realtime API, then listens for incoming events
        and processes them accordingly. If a FastAPI WebSocket is provided, events are forwarded
        to the connected client. Automatically handles cleanup and error reporting.
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
