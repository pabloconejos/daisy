import os
import time
import json
import threading
from typing import Optional

import paho.mqtt.client as mqtt
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from dotenv import load_dotenv
load_dotenv()

# ---------- Config ----------
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
BASE = os.getenv("MQTT_BASE_TOPIC", "assistant")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback")
SPOTIFY_DEVICE_NAME = os.getenv("SPOTIFY_DEVICE_NAME")  # opcional

SCOPE = "user-read-playback-state,user-modify-playback-state,user-read-currently-playing"
POLL_INTERVAL = 1.0  # seg
CACHE_PATH = ".cache-spotify"

TOPIC_CMD_PLAY_SONG = f"{BASE}/spotify/play_song"   # payload: texto con nombre de canción
TOPIC_CMD_RESUME    = f"{BASE}/spotify/play"      # payload: cualquiera
TOPIC_CMD_NEXT      = f"{BASE}/spotify/next"        # payload: cualquier cosa
TOPIC_STATE_JSON    = f"{BASE}/spotify/track/json"  # JSON con info básica
# también publicamos campos simples:
TOPIC_TITLE         = f"{BASE}/spotify/track/title"
TOPIC_ARTISTS       = f"{BASE}/spotify/track/artists"
TOPIC_ALBUM         = f"{BASE}/spotify/track/album"
TOPIC_COVER         = f"{BASE}/spotify/track/cover"
TOPIC_PROGRESS      = f"{BASE}/spotify/track/progress_ms"
TOPIC_DURATION      = f"{BASE}/spotify/track/duration_ms"

def make_spotify() -> spotipy.Spotify:
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=SCOPE,
            open_browser=False,
            cache_path=CACHE_PATH,
        )
    )

def pick_device_id(sp: spotipy.Spotify) -> Optional[str]:
    """Devuelve el device activo, o el primero disponible. Si SPOTIFY_DEVICE_NAME está definido, lo prioriza."""
    devices = sp.devices().get("devices", [])
    if SPOTIFY_DEVICE_NAME:
        for d in devices:
            if d.get("name") == SPOTIFY_DEVICE_NAME:
                return d["id"]
    for d in devices:
        if d.get("is_active"):
            return d["id"]
    return devices[0]["id"] if devices else None

class SimpleSpotifyAgent:
    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        self.sp: Optional[spotipy.Spotify] = None
        self.device_id: Optional[str] = None

        # cache para no spamear MQTT
        self._last_track_id = None
        self._last_bucket = None  # progreso redondeado a segundos

        self._stop = threading.Event()

    # ---- MQTT callbacks ----
    def _on_connect(self, client, userdata, *args):
        reason_code = args[1] if len(args) >= 2 else 0
        code = getattr(reason_code, "value", reason_code)
        print(f"[MQTT] Conectado (code={code})")
        # Subscripciones
        client.subscribe(TOPIC_CMD_PLAY_SONG)
        client.subscribe(TOPIC_CMD_RESUME)
        client.subscribe(TOPIC_CMD_NEXT)

    def _on_disconnect(self, client, userdata, *args):
        code = getattr(args[-2], "value", args[-2]) if len(args) >= 2 else 0
        print(f"[MQTT] Desconectado (code={code})")

    def _on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8").strip()
        try:
            if self.sp is None:
                self.sp = make_spotify()
            if self.device_id is None:
                self.device_id = pick_device_id(self.sp)
                if not self.device_id:
                    print("[SPOTIFY] No hay dispositivos Connect disponibles")
                    return

            if msg.topic == TOPIC_CMD_PLAY_SONG:
                self.play_song_by_name(payload)
            elif msg.topic == TOPIC_CMD_NEXT:
                self.sp.next_track(device_id=self.device_id)
            elif msg.topic == TOPIC_CMD_RESUME:
                self.resume_playback()  
        except Exception as e:
            print(f"[SPOTIFY] Error mensaje: {e}")

    # ---- Acciones ----
    def play_song_by_name(self, query: str):
        if not query:
            print("[SPOTIFY] play_song vacío")
            return
        res = self.sp.search(q=query, type="track", limit=1)
        items = (res.get("tracks") or {}).get("items") or []
        if not items:
            print(f"[SPOTIFY] No encontré: {query}")
            return
        uri = items[0]["uri"]
        # asegúrate de transferir al device
        self.sp.transfer_playback(device_id=self.device_id, force_play=False)
        time.sleep(0.2)
        self.sp.start_playback(device_id=self.device_id, uris=[uri])
        print(f"[SPOTIFY] Reproduciendo: {items[0]['name']}")
    
    def resume_playback(self):
        """
        Reanuda lo último que se estaba reproduciendo.
        - Si hay playback pausado: start_playback() sin URIs (resume).
        - Si no hay playback activo: toma la última canción reproducida y la lanza.
        """
        try:
            # Garantiza que el audio salga por el device elegido
            self.sp.transfer_playback(device_id=self.device_id, force_play=False)
            time.sleep(0.2)

            pb = self.sp.current_playback()
            if pb and not pb.get("is_playing", False):
                # Hay algo pausado: reanuda en el contexto actual (playlist/album/cola)
                self.sp.start_playback(device_id=self.device_id)
                print("[SPOTIFY] Reanudando reproducción anterior")
                return

            if not pb:
                # No hay playback: usa la última canción reproducida como fallback
                recent = self.sp.current_user_recently_played(limit=1)
                items = (recent or {}).get("items") or []
                if items:
                    last_track = (items[0].get("track") or {})
                    uri = last_track.get("uri")
                    if uri:
                        self.sp.start_playback(device_id=self.device_id, uris=[uri])
                        print(f"[SPOTIFY] Reproduciendo lo último escuchado: {last_track.get('name','')}")
                        return

            # Si ya está reproduciendo, no hacemos nada
            print("[SPOTIFY] Ya se está reproduciendo música")
        except Exception as e:
            print(f"[SPOTIFY] Error al reanudar: {e}")

    def next_track(self):
        """
        Salta a la siguiente pista en el dispositivo activo.
        - Transfiere la sesión al device elegido (por si estás controlando otro).
        - Lanza 'next' en ese device.
        """
        try:
            # Asegura que el playback está en el device seleccionado
            self.sp.transfer_playback(device_id=self.device_id, force_play=False)
            time.sleep(0.15)
            self.sp.next_track(device_id=self.device_id)
            print("[SPOTIFY] Siguiente pista ▶▶")
        except Exception as e:
            print(f"[SPOTIFY] Error al pasar a la siguiente pista: {e}")

    # ---- Estado → MQTT ----
    def publish_state_loop(self):
        while not self._stop.is_set():
            try:
                if self.sp is None:
                    self.sp = make_spotify()
                pb = self.sp.current_playback()
                if not pb:
                    time.sleep(POLL_INTERVAL)
                    continue

                item = pb.get("item") or {}
                if not item:
                    time.sleep(POLL_INTERVAL)
                    continue

                track_id = item.get("id")
                name = item.get("name") or ""
                artists = ", ".join([a.get("name") for a in item.get("artists", [])])
                album = (item.get("album") or {}).get("name") or ""
                images = (item.get("album") or {}).get("images") or []
                cover_url = images[0]["url"] if images else ""
                duration_ms = item.get("duration_ms") or 0
                progress_ms = pb.get("progress_ms") or 0

                # Publica solo si cambia pista o segundo
                bucket = progress_ms // 1000
                changed = (track_id != self._last_track_id) or (bucket != self._last_bucket)
                if changed:
                    self._last_track_id = track_id
                    self._last_bucket = bucket

                    self.client.publish(TOPIC_TITLE, name, qos=0, retain=False)
                    self.client.publish(TOPIC_ARTISTS, artists, qos=0, retain=False)
                    self.client.publish(TOPIC_ALBUM, album, qos=0, retain=False)
                    self.client.publish(TOPIC_COVER, cover_url, qos=0, retain=False)
                    self.client.publish(TOPIC_DURATION, str(duration_ms), qos=0, retain=False)
                    self.client.publish(TOPIC_PROGRESS, str(progress_ms), qos=0, retain=False)

                    payload = {
                        "id": track_id,
                        "title": name,
                        "artists": artists,
                        "album": album,
                        "cover_url": cover_url,
                        "duration_ms": duration_ms,
                        "progress_ms": progress_ms,
                        "uri": item.get("uri"),
                    }
                    self.client.publish(TOPIC_STATE_JSON, json.dumps(payload, ensure_ascii=False), qos=0, retain=False)

            except Exception as e:
                print(f"[SPOTIFY] Error estado: {e}")
                time.sleep(1.5)
            time.sleep(POLL_INTERVAL)

    # ---- Ciclo ----
    def start(self):
        if not (SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET and SPOTIFY_REDIRECT_URI):
            print("[SPOTIFY] Faltan credenciales. Exporta SPOTIFY_CLIENT_ID/SECRET/REDIRECT_URI")
            return
        self.client.connect(MQTT_HOST, MQTT_PORT, 60)
        t = threading.Thread(target=self.client.loop_forever, daemon=True)
        t.start()
        try:
            self.publish_state_loop()
        except KeyboardInterrupt:
            pass
        finally:
            self._stop.set()
            self.client.disconnect()

if __name__ == "__main__":
    SimpleSpotifyAgent().start()
