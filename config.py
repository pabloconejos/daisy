from pathlib import Path

# === AUDIO ===
SAMPLE_RATE = 48000  # Vosk recomienda 8k o 16k; 16k suele ir mejor
AUDIO_BLOCK_MS = 60  # tamaño del bloque de captura (ms)

# === VOSK MODEL ===
# Ruta a la carpeta del modelo descargado de:
# https://alphacephei.com/vosk/models
# Ej: "models/vosk-model-small-es-0.42"
VOSK_MODEL_PATH = Path("../../vosk_models/vosk-model-small-es-0.42")

# === MQTT ===
MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_USERNAME = None  # o "usuario"
MQTT_PASSWORD = None  # o "clave"
MQTT_BASE_TOPIC = "assistant"  # prefijo para tus topics

# === OTROS ===
DEBUG_LOG = True  # imprime logs de depuración
