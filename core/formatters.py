# core/formatters.py
import math
from typing import Optional

# =========================
# Utils: formatação BR
# =========================
def fmt_int(v: Optional[float]) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "-"
    return f"{int(round(float(v)))}"


def fmt_money(v: Optional[float]) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "-"
    s = f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def pct_to_float_percent(r: Optional[float]) -> float:
    """Recebe ratio (0..1) e devolve percent (0..100)."""
    if r is None or (isinstance(r, float) and math.isnan(r)):
        return 0.0
    return max(0.0, min(100.0, float(r) * 100.0))


def pill_text_from_ratio(r: Optional[float]) -> str:
    """Texto do pill, com quebra de linha (será convertido em <br/> no card)."""
    if r is None or (isinstance(r, float) and math.isnan(r)):
        return "Sem\ndados"
    r = float(r)
    if r >= 1.0:
        return "Meta\nbatida"
    if r >= 0.85:
        return "Falta\npouco"
    if r >= 0.6:
        return "Em\nandamento"
    return "Atenção"
