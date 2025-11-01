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

    # ----- SPOTIFY -----
    async def play_spotify(self):
        # Reproducción por defecto (playlist/query que definas en el agent)
        await self.bus.publish("spotify/play", "true")

    async def play_song_by_name(self, query: str):
        # Reproducir una canción por nombre (el agent la busca y la pone)
        await self.bus.publish("spotify/play_song", query or "")

    async def next_track(self):
        # Pasar a la siguiente canción
        await self.bus.publish("spotify/next", "1")

    # ----- OTROS -----
    async def tell_joke(self):
        joke = random.choice(_JOKES)
        await self.bus.publish("tts/say", joke)
        await self.bus.publish("log/info", f"JOKE::{joke}")

    async def handle(self, intent: str, slots: dict):
        if intent == "play_spotify":
            await self.play_spotify()
        elif intent == "play_song_by_name":
            await self.play_song_by_name(slots.get("query", ""))
        elif intent == "next_track":
            await self.next_track()
        elif intent == "tell_joke":
            await self.tell_joke()
        else:
            await self.bus.publish("log/warn", f"Intent no soportado: {intent}")
