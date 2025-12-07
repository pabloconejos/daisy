import re
from typing import Optional, Tuple

_PATTERNS = [
    # ----- REPRODUCCIÓN -----

    # "Pon Spotify" / "Pon música" / "Reproduce música"
    (re.compile(r"\b(pon|reproduce|enciende)\b.*\b(spotify|m[uú]sica)\b", re.IGNORECASE),
     ("play_spotify", {})),

    # "Pon <canción>" / "Reproduce <canción>"
    # Captura lo que viene después del verbo como 'query'
    (re.compile(r"\b(pon|reproduce)\b\s+(.+)", re.IGNORECASE),
     ("play_song_by_name", {"slot": "query"})),

    # "Siguiente" / "Pasa canción" / "Próxima"
    (re.compile(r"\b(siguiente|pasa\s+canci[oó]n|pr[oó]xima)\b", re.IGNORECASE),
     ("next_track", {})),

    # "Anterior" / "Vuelve canción" / "Pista previa"
    (re.compile(r"\b(anterior|vuelve\s+canci[oó]n|pr[eé]via|pista\s+anterior)\b", re.IGNORECASE),
     ("previous_track", {})),

    # ----- CONTROL DE REPRODUCCIÓN -----

    # "Pausa música" / "Para un momento" / "Páusala"
    # (re.compile(r"\b(pausa|pausar|para\s+un\s+momento|p[aá]usala)\b", re.IGNORECASE),
    #  ("pause_music", {})),

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

    # ----- CHISTES -----

    # "Cuéntame un chiste" / "Dime un chiste" / "Cuenta un chiste"
    (re.compile(r"\b(cu[eé]ntame|dime|cuenta)\b.*\b(chiste)\b", re.IGNORECASE),
     ("tell_joke", {})),
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
