# actions/spotify_actions.py
from mqtt_bus import MqttBus

class SpotifyActions:
    def __init__(self, bus: MqttBus):
        self.bus = bus

    async def play_spotify(self):
        await self.bus.publish("spotify/play", "true")

    async def play_song_by_name(self, query: str):
        await self.bus.publish("spotify/play_song", query or "")

    async def next_track(self):
        await self.bus.publish("spotify/next", "1")

    async def previous_track(self):
        await self.bus.publish("spotify/previous", "1")

    async def resume_music(self):
        await self.bus.publish("spotify/resume", "true")

    async def stop_music(self):
        await self.bus.publish("spotify/stop", "true")

    async def volume_up(self):
        await self.bus.publish("spotify/volume_up", "true")

    async def volume_down(self):
        await self.bus.publish("spotify/volume_down", "true")

    async def handle(self, intent: str, slots: dict):
        if intent == "play_spotify":
            await self.play_spotify()
        elif intent == "play_song_by_name":
            await self.play_song_by_name(slots.get("query", ""))
        elif intent == "next_track":
            await self.next_track()
        elif intent == "previous_track":
            await self.previous_track()
        elif intent == "resume_music":
            await self.resume_music()
        elif intent == "stop_music":
            await self.stop_music()
        elif intent == "volume_up":
            await self.volume_up()
        elif intent == "volume_down":
            await self.volume_down()
