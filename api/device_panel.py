from flask import Flask, jsonify, render_template_string
import socket

app = Flask(__name__)

def get_local_ip():
    """Devuelve la IP local principal (para mostrarla en el panel si quieres)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

@app.route("/")
def index():
    ip = get_local_ip()
    html = """
    <!doctype html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <title>Panel del dispositivo</title>
        <style>
            body { font-family: sans-serif; background: #111827; color: #e5e7eb; margin:0; padding:0; }
            .container { max-width: 600px; margin: 40px auto; padding: 24px; background:#1f2937; border-radius:16px; }
            h1 { margin-top:0; }
            .tag { display:inline-block; padding: 4px 8px; border-radius:999px; background:#10b98122; font-size: 12px; }
            code { background:#374151; padding:2px 6px; border-radius:4px; }
            a { color:#60a5fa; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="tag">BETA</div>
            <h1>Panel del dispositivo</h1>
            <p>El panel está funcionando 🎉</p>
            <p>Puedes acceder desde esta IP local: <code>{{ ip }}:8080</code></p>

            <h2>API de ejemplo</h2>
            <p>Prueba a acceder a <code>/api/status</code> para ver el estado en JSON.</p>

            <p style="margin-top:32px;font-size:12px;opacity:0.7;">
                Próximos pasos: Spotify, WiFi, QR en pantalla…
            </p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, ip=ip)

@app.route("/api/status")
def status():
    # Más adelante aquí pondremos info real: estado Spotify, red, etc.
    data = {
        "ok": True,
        "device": "raspberry-assistant",
        "ip": get_local_ip(),
        "features": {
            "spotify": False,
            "wifi_config": False,
            "version": "0.1.0"
        }
    }
    return jsonify(data)

if __name__ == "__main__":
    # host=0.0.0.0 => accesible desde otros dispositivos en la red
    app.run(host="0.0.0.0", port=8080, debug=False)
