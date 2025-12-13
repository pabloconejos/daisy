#!/bin/bash

echo "🔌 Activando entorno virtual..."
source .venv/bin/activate

echo "🎵 Iniciando Spotify Agent..."
python spotify_agent.py &

sleep 2

echo "🧠 Iniciando núcleo principal..."
python main.py &

sleep 2

echo "🌐 Iniciando panel web..."
python api/device_panel.py &

echo "✅ Todo iniciado correctamente"
wait
