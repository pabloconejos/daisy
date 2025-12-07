import re
from typing import Optional, Tuple

_PATTERNS = [
    # "Pon Spotify" / "Pon música"
    (re.compile(r"\b(pon|reproduce|enciende)\b.*\b(spotify|m[uú]sica)\b", re.IGNORECASE),
     ("play_spotify", {})),

    # "Pon <canción>" / "Reproduce <canción>"
    # Captura lo que viene después del verbo como 'query'
    (re.compile(r"\b(pon|reproduce)\b\s+(.+)", re.IGNORECASE),
     ("play_song_by_name", {"slot": "query"})),

    # "Siguiente" / "Pasa canción"
    (re.compile(r"\b(siguiente|pasa\s+canci[oó]n|pr[oó]xima)\b", re.IGNORECASE),
     ("next_track", {})),

    # "Parar canción" / "Detener música"
    (re.compile(r"\b(parar|detener)\b.*\b(canci[oó]n|m[uú]sica)\b", re.IGNORECASE),
     ("stop_music", {})),

    # "Cuéntame un chiste"
    (re.compile(r"\b(cu[eé]ntame|dime|cuenta)\b.*\b(chiste)\b", re.IGNORECASE),
     ("tell_joke", {})),

    # "Anterior" / "Vuelve canción"
    (re.compile(r"\b(anterior|vuelve\s+canci[oó]n|pr[eé]via)\b", re.IGNORECASE),
     ("previous_track", {})),

]

def match_intent(text: str) -> Optional[Tuple[str, dict]]:
    t = text.strip()
    for rx, (intent, data) in _PATTERNS:
        m = rx.search(t)
        if m:
            slots = {}
            if data.get("slot") == "query":
                # Toma el grupo 2 (lo que viene tras 'pon|reproduce')
                slots["query"] = m.group(2).strip()
            return intent, slots
    return None
