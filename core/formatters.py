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
    """
    Recebe ratio (tipicamente -1..1) e devolve percent (-100..100).
    ✅ Não zera negativos.
    """
    if r is None or (isinstance(r, float) and math.isnan(r)):
        return 0.0
    v = float(r) * 100.0
    # clamp simétrico só pra evitar absurdos caso venha algo fora do esperado
    return max(-100.0, min(100.0, v))


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


def fmt_money_no_cents(x) -> str:
    """
    98874 ou 98874.0 ou '98.874,00' -> '98.874'
    Mantém sinal e separador de milhar pt-BR.
    """
    if x is None:
        return "0"

    # Se vier string tipo '98.874,00', remove milhar e troca vírgula por ponto
    if isinstance(x, str):
        s = x.strip()
        s = s.replace(".", "").replace(",", ".")  # '98.874,00' -> '98874.00'
        try:
            n = float(s)
        except Exception:
            n = 0.0
    else:
        try:
            n = float(x)
        except Exception:
            n = 0.0

    n_int = int(round(n))  # arredonda e remove centavos
    return f"{n_int:,}".replace(",", ".")
