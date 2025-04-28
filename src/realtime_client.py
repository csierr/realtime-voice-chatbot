import asyncio
import json
import base64
import websockets
from .audio_handler import AudioHandler
from .event_handler import EventHandler

class RealtimeClient:
    """
    Cliente para interactuar con la API Realtime de OpenAI via WebSocket.
    """
    def __init__(self, api_key, instructions, voice):
        self.url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "OpenAI-Beta": "realtime=v1"
        }
        self.audio_handler = AudioHandler()
        self.event_handler = EventHandler(self.audio_handler)
        self.ws = None
        self.instructions = instructions
        self.voice = voice
        self.VAD_turn_detection = True
        self.VAD_config = {
            "type": "server_vad",
            "threshold": 0.8,
            "prefix_padding_ms": 300,  
            "silence_duration_ms": 1000,
            "interrupt_response": False
        }
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
        Conexión al servidor del WebSocket y envío de configuración
        """
        self.ws = await websockets.connect(self.url, extra_headers=self.headers)
        await self.send_event({"type": "session.update", "session": self.session_config})
        await self.send_event({"type": "response.create"})


    async def send_event(self, event):
        """
        Envío de eventos a servidor WebSocket
        
        event: Evento a enviar (desde usuario)
        """
        await self.ws.send(json.dumps(event))
        print(f"Evento enviado: {event['type']}")


    async def receive_events(self):
        """
        Recepción de eventos en servidor WebSocket
        """
        try:
            async for message in self.ws:
                event = json.loads(message)
                await self.event_handler.handle_event(event, self.send_event)
        except Exception as e:
            print(f"Error en recepción de eventos: {e}")


    async def send_text(self, text):
        """
        Envío de texto a servidor WebSocket
        
        text: Mensaje de texto a enviar
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


    async def send_audio(self):
        """
        Grabación y envío de audio usando VAD
        """
        self.audio_handler.start_recording()
        try:
            while True:
                chunk = self.audio_handler.record_chunk()
                if chunk:
                    base64_chunk = base64.b64encode(chunk).decode('utf-8')
                    await self.send_event({
                        "type": "input_audio_buffer.append",
                        "audio": base64_chunk
                    })
                    await asyncio.sleep(0.01)
                else:
                    break
        except Exception as e:
            print(f"Error durante grabacion de audio: {e}")
        finally:
            self.audio_handler.stop_recording()


    async def clean_up(self):
        """
        Libera recursos cerrando manejador de audio y WebSocket
        """
        self.audio_handler.clean_up()
        if self.ws:
            await self.ws.close()
