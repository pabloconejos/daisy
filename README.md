# 🗣️ README — Puesta en marcha (Raspberry Pi)

Guía corta para ejecutar el asistente de voz. Asume que **ya tienes el código** en `~/proyectos/daisy/` y que `mqtt_bus.py` usa **paho-mqtt 2.x** (sin `asyncio-mqtt`).

---

## 1) Preparar entorno

```bash
cd ~/proyectos/daisy
python3 -m venv .venv
source .venv/bin/activate
sudo apt update
sudo apt install -y python3-dev python3-pip portaudio19-dev mosquitto mosquitto-clients
```

## 2) Instalar Python deps

Usa este `requirements.txt` mínimo:

```
vosk==0.3.44
sounddevice==0.4.7
paho-mqtt==2.1.0
```

Instala:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 3) Modelo Vosk (español, pequeño)

```bash
mkdir -p models && cd models
wget https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip
unzip vosk-model-small-es-0.42.zip
cd ..
```

En `config.py`:
```python
VOSK_MODEL_PATH = Path("models/vosk-model-small-es-0.42")
MQTT_HOST = "localhost"
MQTT_PORT = 1883
DEBUG_LOG = True
```

> Opcional: silenciar logs de Vosk al inicio del programa:
> ```bash
> export VOSK_LOG_LEVEL=-1
> ```

## 4) Iniciar broker y monitor

```bash
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
# En otra terminal:
mosquitto_sub -h localhost -t "#" -v
```

## 5) Ejecutar el asistente

```bash
source .venv/bin/activate
python main.py
```

Deberías ver:
```
[MQTT] Conectado (code=0)
[STT] Iniciando captura de audio…
[CORE] Asistente de voz iniciado…
```

## 6) Probar

Di cerca del micro:
- “**Pon Spotify**” → publica `assistant/spotify/play = true`
- “**Cuéntame un chiste**” → publica `assistant/tts/say = <chiste>`
- “**Pon Rosalia**” → publica `assistant/spotify/play_song = Rosalia`

Los verás en la terminal del `mosquitto_sub`.

## 7) Salir

`Ctrl + C` para detener el asistente.


python spotify_agent.py
python main.py