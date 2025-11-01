import queue
import threading
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer
from typing import Callable
from config import SAMPLE_RATE, AUDIO_BLOCK_MS, VOSK_MODEL_PATH, DEBUG_LOG

class VoskSTT:
    """
    Captura audio del micro y emite frases reconocidas (texto) vía callback.
    Usa VAD interno de Vosk por bloques; simple y robusto para empezar.
    """
    def __init__(self, on_text: Callable[[str], None]):
        if not VOSK_MODEL_PATH.exists():
            raise FileNotFoundError(
                f"No se encontró el modelo Vosk en {VOSK_MODEL_PATH}. "
                "Descárgalo y ajusta la ruta en config.py."
            )
        self.model = Model(str(VOSK_MODEL_PATH))
        self.rec = KaldiRecognizer(self.model, SAMPLE_RATE)
        self.rec.SetWords(True)  # opcional
        self.on_text = on_text

        self.q = queue.Queue()
        self._stop = threading.Event()
        self._worker = threading.Thread(target=self._recognize_loop, daemon=True)

    def start(self):
        if DEBUG_LOG: print("[STT] Iniciando captura de audio…")
        self._stop.clear()
        self._worker.start()
        sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            blocksize=int(SAMPLE_RATE * (AUDIO_BLOCK_MS / 1000)),
            callback=self._audio_callback,
        ).start()

    def stop(self):
        self._stop.set()

    def _audio_callback(self, indata, frames, time, status):
        if status:
            print(f"[Audio] Estado: {status}")
        self.q.put(bytes(indata))

    def _recognize_loop(self):
        """
        Va alimentando a Vosk con bloques y emite texto cuando detecta fin de frase.
        """
        while not self._stop.is_set():
            data = self.q.get()
            if self.rec.AcceptWaveform(data):
                result = self.rec.Result()
                try:
                    text = json.loads(result).get("text", "").strip()
                except json.JSONDecodeError:
                    text = ""
                if text:
                    if DEBUG_LOG: print(f"[STT] Frase: {text}")
                    self.on_text(text)
            else:
                # Parcial: self.rec.PartialResult() si quieres feedback en vivo
                pass
