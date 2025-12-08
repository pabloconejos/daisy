from flask import Flask, jsonify, render_template_string, redirect, request
import socket
import os

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()  # carga variables de .env

app = Flask(__name__)

# ---------- Config Spotify ----------
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SPOTIFY_CACHE_PATH = os.getenv("SPOTIFY_CACHE_PATH", ".cache-spotify")

SPOTIFY_SCOPES = (
    "user-read-playback-state "
    "user-modify-playback-state "
    "user-read-currently-playing "
    "user-read-recently-played"
)

def get_spotify_oauth():
    """Crea un objeto SpotifyOAuth con la misma config que usa spotify_agent."""
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SPOTIFY_SCOPES,
        cache_path=SPOTIFY_CACHE_PATH,
        open_browser=False,
    )


def has_spotify_token():
    """Devuelve True si ya hay un token guardado en cache."""
    return os.path.exists(SPOTIFY_CACHE_PATH)


# ---------- Utilidades generales ----------
def get_local_ip():
    """Devuelve la IP local principal."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


# ---------- Rutas HTML ----------
@app.route("/")
def index():
    ip = get_local_ip()
    spotify_connected = has_spotify_token()

    html = """
    <!doctype html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <title>Panel del dispositivo</title>
        <style>
            body { font-family: sans-serif; background: #111827; color: #e5e7eb; margin:0; padding:0; }
            .container { max-width: 700px; margin: 40px auto; padding: 24px; background:#1f2937; border-radius:16px; }
            h1 { margin-top:0; }
            .tag { display:inline-block; padding: 4px 8px; border-radius:999px; background:#10b98122; font-size: 12px; }
            code { background:#374151; padding:2px 6px; border-radius:4px; }
            a { color:#60a5fa; text-decoration:none; }
            a.button { display:inline-block; padding:8px 14px; border-radius:999px; background:#2563eb; color:white; margin-top:8px; }
            .card { padding:16px; border-radius:12px; background:#111827; margin-top:16px; }
            .status-ok { color:#10b981; }
            .status-bad { color:#f97316; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="tag">BETA</div>
            <h1>Panel del dispositivo</h1>

            <p>Estás accediendo al panel del dispositivo en <code>{{ ip }}:8080</code></p>

            <div class="card">
                <h2>Estado general</h2>
                <p>API de estado: <code>/api/status</code></p>
            </div>

            <div class="card">
                <h2>Spotify</h2>
                {% if spotify_connected %}
                    <p class="status-ok">✔ Cuenta de Spotify vinculada.</p>
                    <p><a class="button" href="/spotify/logout">Cerrar sesión de Spotify</a></p>
                {% else %}
                    <p class="status-bad">✖ No hay ninguna cuenta vinculada.</p>
                    <p><a class="button" href="/spotify/login">Conectar con Spotify</a></p>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, ip=ip, spotify_connected=spotify_connected)


# ---------- API simple ----------
@app.route("/api/status")
def status():
    data = {
        "ok": True,
        "device": "raspberry-assistant",
        "ip": get_local_ip(),
        "features": {
            "spotify_connected": has_spotify_token(),
            "version": "0.2.0"
        }
    }
    return jsonify(data)


# ---------- Flujo Spotify ----------
@app.route("/spotify/login")
def spotify_login():
    if not (SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET and SPOTIFY_REDIRECT_URI):
        return "Spotify no está configurado correctamente (falta CLIENT_ID/SECRET/REDIRECT_URI en .env).", 500

    auth = get_spotify_oauth()
    auth_url = auth.get_authorize_url()
    # Redirigimos al usuario a Spotify
    return redirect(auth_url)


@app.route("/spotify/callback")
def spotify_callback():
    error = request.args.get("error")
    code = request.args.get("code")

    if error:
        return f"Error al autorizar Spotify: {error}", 400

    if not code:
        return "No se recibió el parámetro 'code' de Spotify.", 400

    auth = get_spotify_oauth()
    try:
        token_info = auth.get_access_token(code, as_dict=True)
    except Exception as e:
        return f"Error al obtener el token de Spotify: {e}", 500

    # En este punto SpotifyOAuth ya ha guardado el token en cache_path (.cache-spotify)
    access_token = token_info.get("access_token")
    if not access_token:
        return "No se obtuvo access_token de Spotify.", 500

    html = """
    <!doctype html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <title>Spotify conectado</title>
        <style>
            body { font-family: sans-serif; background: #111827; color: #e5e7eb; margin:0; padding:0; }
            .container { max-width: 600px; margin: 40px auto; padding: 24px; background:#1f2937; border-radius:16px; text-align:center; }
            a { color:#60a5fa; }
            a.button { display:inline-block; padding:8px 14px; border-radius:999px; background:#2563eb; color:white; margin-top:16px; text-decoration:none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Spotify conectado ✅</h1>
            <p>El dispositivo ya tiene autorización para controlar tu cuenta de Spotify.</p>
            <p>Ahora puedes usar los comandos de voz o el resto del sistema.</p>
            <a class="button" href="/">Volver al panel</a>
        </div>
    </body>
    </html>
    """
    return html


@app.route("/spotify/logout")
def spotify_logout():
    # Cerrar sesión = eliminar el archivo de cache
    if os.path.exists(SPOTIFY_CACHE_PATH):
        os.remove(SPOTIFY_CACHE_PATH)
    html = """
    <!doctype html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <title>Spotify desconectado</title>
        <style>
            body { font-family: sans-serif; background: #111827; color: #e5e7eb; margin:0; padding:0; }
            .container { max-width: 600px; margin: 40px auto; padding: 24px; background:#1f2937; border-radius:16px; text-align:center; }
            a { color:#60a5fa; }
            a.button { display:inline-block; padding:8px 14px; border-radius:999px; background:#2563eb; color:white; margin-top:16px; text-decoration:none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Spotify desconectado</h1>
            <p>Se ha eliminado la autorización de Spotify para este dispositivo.</p>
            <a class="button" href="/">Volver al panel</a>
        </div>
    </body>
    </html>
    """
    return html


# ---------- Arranque ----------
if __name__ == "__main__":
    print("Iniciando panel en https://0.0.0.0:8080 ...")
    app.run(host="0.0.0.0", port=8080, debug=False, ssl_context=("cert.pem", "key.pem"))
