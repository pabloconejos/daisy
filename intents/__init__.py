# intents/__init__.py
from typing import Optional, Tuple
import re

from .spotify_intents import SPOTIFY_PATTERNS
from .fun_intents import FUN_PATTERNS

_PATTERNS = SPOTIFY_PATTERNS + FUN_PATTERNS

def match_intent(text: str) -> Optional[Tuple[str, dict]]:
    t = text.strip()
    for rx, (intent, data) in _PATTERNS:
        m = rx.search(t)
        if m:
            slots = {}
            if data.get("slot") == "query":
                # grupo 2 = lo que viene después de "pon|reproduce"
                slots["query"] = m.group(2).strip()
            return intent, slots
    return None
