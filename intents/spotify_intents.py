# intents/spotify_intents.py
import re

SPOTIFY_PATTERNS = [
    # ----- REPRODUCCIÓN -----

    # "Pon Spotify" / "Pon música" / "Reproduce música"
    (re.compile(r"\b(pon|reproduce|enciende)\b.*\b(spotify|m[uú]sica)\b", re.IGNORECASE),
     ("play_spotify", {})),

    # "Pon <canción>" / "Reproduce <canción>"
    (re.compile(r"\b(pon|reproduce)\b\s+(.+)", re.IGNORECASE),
     ("play_song_by_name", {"slot": "query"})),

    # "Siguiente" / "Pasa canción" / "Próxima"
    (re.compile(r"\b(siguiente|pasa\s+canci[oó]n|pr[oó]xima)\b", re.IGNORECASE),
     ("next_track", {})),

    # "Anterior" / "Vuelve canción" / "Pista previa"
    (re.compile(r"\b(anterior|vuelve\s+canci[oó]n|pr[eé]via|pista\s+anterior)\b", re.IGNORECASE),
     ("previous_track", {})),

    # "Reanuda música" / "Continúa la música" / "Sigue"
    (re.compile(r"\b(reanuda|reanudar|contin[uú]a|sigue)\b.*(m[uú]sica|reproducci[oó]n)?", re.IGNORECASE),
     ("resume_music", {})),

    # "Parar canción" / "Detener música"
    (re.compile(r"\b(parar|detener|stop)\b.*\b(canci[oó]n|m[uú]sica)\b", re.IGNORECASE),
     ("stop_music", {})),

    # ----- VOLUMEN -----

    # "Sube el volumen" / "Más volumen" / "Súbelo"
    (re.compile(r"\b(sube|incrementa|aumenta|m[aá]s)\b.*\b(volumen|audio|sonido)\b|\b(s[uú]belo)\b", re.IGNORECASE),
     ("volume_up", {})),

    # "Baja el volumen" / "Menos volumen" / "Bájalo"
    (re.compile(r"\b(baja|reduce|menos)\b.*\b(volumen|audio|sonido)\b|\b(b[aá]jalo)\b", re.IGNORECASE),
     ("volume_down", {})),
]
