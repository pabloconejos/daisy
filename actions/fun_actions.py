# actions/fun_actions.py
import random
from mqtt_bus import MqttBus

_JOKES = [
    "¿Qué le dice un techo a otro? Techo de menos.",
    "¿Cuál es el café más peligroso del mundo? El ex-preso.",
    "¿Por qué la computadora fue al médico? Porque tenía un virus."
]

class FunActions:
    def __init__(self, bus: MqttBus):
        self.bus = bus

    async def tell_joke(self):
        joke = random.choice(_JOKES)
        await self.bus.publish("tts/say", joke)
        await self.bus.publish("log/info", f"JOKE::{joke}")

    async def handle(self, intent: str, slots: dict):
        if intent == "tell_joke":
            await self.tell_joke()
