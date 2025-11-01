import asyncio
import random
from mqtt_bus import MqttBus

_JOKES = [
    "¿Qué le dice un techo a otro? Techo de menos.",
    "¿Cuál es el café más peligroso del mundo? El ex-preso.",
    "¿Por qué la computadora fue al médico? Porque tenía un virus."
]

class Actions:
    """
    Acciones asociadas a intents. Publican eventos MQTT u otras tareas locales.
    """
    def __init__(self, bus: MqttBus):
        self.bus = bus

    async def play_spotify(self):
        # Ejemplo: publicar un evento para que otro servicio (Home Assistant, Node-RED, etc.) lo consuma
        await self.bus.publish("spotify/play", "true")
        # También podrías lanzar un comando local en la Pi (p. ej. con spotifyd o librespot).
        # Aquí nos mantenemos en MQTT para mantener el diseño desacoplado.

    async def tell_joke(self):
        joke = random.choice(_JOKES)
        # Publica a un topic que tu TTS (eSpeak NG, Piper, etc.) esté escuchando
        await self.bus.publish("tts/say", joke)
        # Y de paso, un log/eco simple
        await self.bus.publish("log/info", f"JOKE::{joke}")

    async def handle(self, intent: str, slots: dict):
        if intent == "play_spotify":
            await self.play_spotify()
        elif intent == "tell_joke":
            await self.tell_joke()
        else:
            await self.bus.publish("log/warn", f"Intent no soportado: {intent}")
