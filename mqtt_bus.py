import asyncio
import threading
from typing import Optional
import paho.mqtt.client as mqtt
from config import MQTT_HOST, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD, MQTT_BASE_TOPIC, DEBUG_LOG

class MqttBus:
    def __init__(self):
        # Usa API v2 y protocolo MQTT v5 para que reason_code sea consistente
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            protocol=mqtt.MQTTv5
        )
        if MQTT_USERNAME and MQTT_PASSWORD:
            self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self._connected_evt = threading.Event()
        self._thread: Optional[threading.Thread] = None

    # ---------- Callbacks ----------
    def _on_connect(self, client, userdata, *args):
        # args = (flags, reason_code, properties) para v2/v5
        reason_code = args[1] if len(args) >= 2 else 0
        code = getattr(reason_code, "value", reason_code)
        if DEBUG_LOG: print(f"[MQTT] Conectado (code={code})")
        if code == 0:
            self._connected_evt.set()

    def _on_disconnect(self, client, userdata, *args):
        # args = (disconnect_flags, reason_code, properties) o (reason_code, properties)
        if len(args) == 0:
            code = 0
        elif len(args) == 1:
            code = getattr(args[0], "value", args[0])
        else:
            code = getattr(args[-2], "value", args[-2])
        if DEBUG_LOG: print(f"[MQTT] Desconectado (code={code})")
        self._connected_evt.clear()

    # ---------- API pública ----------
    async def connect(self):
        if self._thread and self._thread.is_alive():
            return
        self.client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
        self._thread = threading.Thread(target=self.client.loop_forever, daemon=True)
        self._thread.start()
        await asyncio.to_thread(self._connected_evt.wait)

    async def disconnect(self):
        if self._thread and self._thread.is_alive():
            self.client.disconnect()
            await asyncio.sleep(0.1)

    async def publish(self, topic_suffix: str, payload: str, qos: int = 0, retain: bool = False):
        if not self._connected_evt.is_set():
            await self.connect()
        topic = f"{MQTT_BASE_TOPIC}/{topic_suffix}"
        if DEBUG_LOG:
            print(f"[MQTT] → {topic}: {payload}")
        info = self.client.publish(topic, payload=payload, qos=qos, retain=retain)
        await asyncio.to_thread(info.wait_for_publish)

    async def subscribe_loop(self, topic_suffix: str, handler):
        pattern = f"{MQTT_BASE_TOPIC}/{topic_suffix}"
        if not self._connected_evt.is_set():
            await self.connect()

        def _on_message(client, userdata, msg):
            try:
                handler(msg.payload.decode("utf-8"))
            except Exception as e:
                print(f"[MQTT] Error en handler: {e}")

        self.client.on_message = _on_message
        self.client.subscribe(pattern)
        if DEBUG_LOG:
            print(f"[MQTT] Subscrito a {pattern}")

        try:
            while self._connected_evt.is_set():
                await asyncio.sleep(1.0)
        finally:
            self.client.on_message = None
