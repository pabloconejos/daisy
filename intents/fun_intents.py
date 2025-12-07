# intents/fun_intents.py
import re

FUN_PATTERNS = [
    # "Cuéntame un chiste" / "Dime un chiste" / "Cuenta un chiste"
    (re.compile(r"\b(cu[eé]ntame|dime|cuenta)\b.*\b(chiste)\b", re.IGNORECASE),
     ("tell_joke", {})),
]
