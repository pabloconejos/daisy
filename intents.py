import re
from typing import Optional, Tuple

# Patrón muy simple. Para producción considera Rasa, Snips, intent parsers con ML, o reglas más ricas.
# Aquí mapeamos a intents + (opcional) slots.
_PATTERNS = [
    (re.compile(r"\b(pon|reproduce|abre)\b.*\b(spotify)\b", re.IGNORECASE), ("play_spotify", {})),
    # antes solo "cuéntame/dime"
    (re.compile(r"\b(cu[eé]nta(me)?|dime|cuenta)\b.*\b(chiste)\b", re.IGNORECASE), ("tell_joke", {})),
]
    

def match_intent(text: str) -> Optional[Tuple[str, dict]]:
    t = text.strip()
    for rx, (intent, _slot) in _PATTERNS:
        if rx.search(t):
            return intent, {}
    return None
