import pyaudio
import threading

class AudioHandler:
    """
    Maneja captura y reproducción (con PyAudio) de audio en tiempo real
    """
    def __init__(self, rate=24000, chunk_size=1024, channels=1):
        self.interface = pyaudio.PyAudio() # Inicializacion de PyAudio
        self.stream = None           
        self.audio_buffer = b''            # Buffer para almacenar audio
        self.chunk_size = chunk_size       # Tamaño de chunk de grabacion
        self.format = pyaudio.paInt16      # Formato audio (16-bit PCM)
        self.channels = channels           # Numero de canales (mono o stereo)
        self.rate = rate                   # Tasa de muestreo (Hz)
        self.is_recording = False          # Flag para indicar si se está grabando
    

    def start_recording(self):
        """
        Comienza grabación de audio
        """        
        self.is_recording = True
        self.audio_buffer = b''

        self.stream = self.interface.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )


    def stop_recording(self):
        """
        Detiene grabación y retorna audio grabado
        """
        self.is_recording = False

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        return self.audio_buffer
    

    def clean_up(self):
        """
        Libera recursos deteniendo y cerrando stream y terminando PyAudio
        """
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.interface.terminate()


    def record_chunk(self):
        """
        Graba chunks de tamaño chunk_size y los añade al buffer
        """
        if self.stream and self.is_recording:
            data = self.stream.read(self.chunk_size)
            self.audio_buffer += data
            return data
        return None
    
    
    def play_audio(self, audio_data):
        """
        Reproduce audio
        
        audio_data: Respuesta de audio recibida (respuesta de IA)
        """
        def play():
            stream = self.interface.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                output=True
            )
            stream.write(audio_data)
            stream.stop_stream()
            stream.close()

        playback_thread = threading.Thread(target=play)
        playback_thread.start()