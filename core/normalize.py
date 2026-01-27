from __future__ import annotations

import re

# Caracteres invisíveis comuns vindos do Google Sheets / copy-paste:
# - Zero width space (U+200B) etc
# - BOM (U+FEFF)
# - Soft hyphen (U+00AD)
_CLEAN_INVISIBLE_RE = re.compile(r"[\u200B-\u200F\uFEFF\u00AD]")

def strip_invisible(text: object) -> str:
    """Remove caracteres invisíveis e padroniza NBSP em espaço."""
    s = "" if text is None else str(text)
    s = _CLEAN_INVISIBLE_RE.sub("", s)
    s = s.replace("\u00A0", " ")  # NBSP
    return s

def norm_text(text: object) -> str:
    """
    Normaliza texto:
    - remove invisíveis
    - troca NBSP por espaço
    - colapsa whitespace
    - strip + UPPER
    """
    s = strip_invisible(text)
    s = " ".join(s.split())
    return s.strip().upper()
