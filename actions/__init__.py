# actions/__init__.py
from mqtt_bus import MqttBus
from .spotify_actions import SpotifyActions
from .fun_actions import FunActions

class Actions:
    """
    Router de acciones: decide qué módulo maneja cada intent.
    """
    def __init__(self, bus: MqttBus):
        self.spotify = SpotifyActions(bus)
        self.fun = FunActions(bus)

    async def handle(self, intent: str, slots: dict):
        # Intents de Spotify
        if intent in {
            "play_spotify",
            "play_song_by_name",
            "next_track",
            "previous_track",
            "resume_music",
            "stop_music",
            "volume_up",
            "volume_down",
        }:
            return await self.spotify.handle(intent, slots)

        # Intents de chistes
        if intent in {"tell_joke"}:
            return await self.fun.handle(intent, slots)

        # Si no lo reconoce
        await self.spotify.bus.publish("log/warn", f"Intent no soportado: {intent}")
