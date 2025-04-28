import json
from .realtime_client import RealtimeClient
from fastapi import WebSocket

class MyRealtimeClient(RealtimeClient):
    """
    Cliente que extiende funcionalidad de cliente base 'RealtimeClient' (interaccion con API Realtime OpenAI via WebSocket)
    para integrarse con una conexión WebSocket de FastAPI
    """
    def __init__(self, websocket: WebSocket, **kwargs):
        """
        Inicializa cliente con un WebSocket de FastAPI y otros parámetros

        websocket (WebSocket): WebSocket activo con el cliente
        kwargs: Argumentos adicionales pasados al cliente base
        """
        super().__init__(**kwargs)
        self.websocket = websocket


    async def handle_event(self, event: dict):
        """
        Maneja eventos especificos recibidos desde la conexion con la API Realtime
        Filtra por tipo de evento y envía mensajes en formato texto al cliente por WebSocket

        event (dict): Evento recibido desde OpenAI en formato JSON
        """
        event_type = event.get("type")
        print("🔁 Recibido desde OpenAI:", event_type)

        if event_type in ["response.audio_transcript.done", "conversation.item.input_audio_transcription.completed"]:
            transcript = event.get("transcript", "No transcript available.")
            print("📝 Transcript:", transcript)
            await self.websocket.send_json({"text": transcript})


    async def run(self):
        """
        Ejecuta ciclo principal del cliente Realtime: se conecta, escucha eventos entrantes y los pasa al manejador correspondiente
        Tambien maneja errores y realiza limpieza al finalizar la sesion
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
