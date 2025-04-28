import base64

class EventHandler:
    def __init__(self, audio_handler):
        self.audio_handler = audio_handler
        self.audio_buffer = b''

    async def handle_event(self, event, send_event):
        event_type = event.get("type")

        if event_type == "error":
            print(event_type, event['error']['message'])

        elif event_type == "response.text.delta":
            print(event["delta"], end="", flush=True)

        elif event_type in ["conversation.item.input_audio_transcription.delta", "response.audio_transcript.delta"]:
            pass

        elif event_type in ["conversation.item.input_audio_transcription.completed", "response.audio_transcript.done"]:
            with open("transcription.txt", "a", encoding="utf-8") as f:
                f.write(event["transcript"] + '\n')
                f.flush()

        elif event_type == "response.audio.delta":
            self.audio_buffer += base64.b64decode(event["delta"])

        elif event_type == "response.audio.done":
            if self.audio_buffer:
                self.audio_handler.play_audio(self.audio_buffer)
                self.audio_buffer = b''

        elif event_type == "response.done":
            print("Generación de respuesta completada")

        elif event_type == "conversation.item.created":
            print(f"Item de conversación creado: {event.get('item')}")

        elif event_type == "input_audio_buffer.speech_started":
            print("Inicio de voz detectado por VAD")

        elif event_type == "input_audio_buffer.speech_stopped":
            print("Fin de voz detectado por VAD")
            await send_event({"type": "response.create"})
