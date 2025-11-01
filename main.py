import asyncio
from config import DEBUG_LOG
from mqtt_bus import MqttBus
from stt import VoskSTT
from intents import match_intent
from actions import Actions
from asyncio import run_coroutine_threadsafe 

class VoiceAssistant:
    def __init__(self):
        self.bus = MqttBus() # Crea y guarda el cliente MQTT en la instancia (self.bus) para poder usarlo en todo el objeto.
        self.actions = Actions(self.bus) # Crea el manejador de acciones y le inyecta el bus MQTT (dependencia) para que pueda publicar.
        self.loop = None

    async def start(self):
        await self.bus.connect() # Conecta al broker MQTT.
        self.loop = asyncio.get_running_loop()
        # Arrancamos STT (hilo + stream de audio)
        self.stt = VoskSTT(on_text=self.on_text_detected) # Crea el motor de STT y le pasa como callback self.on_text_detected, que se llamará cuando haya texto final reconocido.
        self.stt.start() # Inicia la captura del micrófono y el loop de reconocimiento (hilo + flujo de audio).
        if DEBUG_LOG:
            print("[CORE] Asistente de voz iniciado. Di: 'Pon Spotify' o 'Cuéntame un chiste'.")

        # Mantener vivo el bucle principal (Ctrl+C para salir)
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt: # Si pulsas Ctrl+C, se captura la interrupción y (si hay debug) se imprime un mensaje de salida ordenada.
            if DEBUG_LOG: print("\n[CORE] Saliendo…")
        finally:
            self.stt.stop() # Detiene el hilo de STT.
            await self.bus.disconnect() # Cierra la conexión MQTT.

    def on_text_detected(self, text: str):
        """
        Callback desde STT. No es async, así que despachamos a asyncio.create_task.
        """
        match = match_intent(text) # Intenta detectar un intent a partir del texto reconocido.
        if not match:
            if DEBUG_LOG: print("[NLP] No se reconoció un intent.")
            return

        intent, slots = match # Desempaqueta el intent y los posibles “slots” (parámetros extraídos del texto).
        if DEBUG_LOG: print(f"[NLP] Intent: {intent} | slots: {slots}")
        run_coroutine_threadsafe(self.actions.handle(intent, slots), self.loop) # Llama al manejador de acciones para que procese el intent.

if __name__ == "__main__":
    asyncio.run(VoiceAssistant().start())
