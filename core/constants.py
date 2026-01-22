# core/constants.py
from dataclasses import dataclass

# =========================
# Config central
# =========================
REFRESH_MS = 5_000
CACHE_TTL_SECONDS = 4


@dataclass(frozen=True)
class _Indicators:
    # Indicadores (normalizamos pra UPPER)
    REUNIOES_REAL: str = "REUNIÕES OCORRIDAS"
    REUNIOES_META: str = "REUNIÕES OCORRIDAS - META"
    REUNIOES_PERC: str = "PERC META REUNIÕES OCORRIDAS"
    REUNIOES_DIF:  str = "DIF META REUNIÕES OCORRIDAS"

    FAT_REAL: str = "FATURAMENTO PAGO"         # preferimos pago
    FAT_FALLBACK_REAL: str = "FATURAMENTO"     # fallback
    FAT_META: str = "FATURAMENTO - META"
    FAT_PERC: str = "PERC META FATURAMENTO"
    FAT_DIF:  str = "DIF META FATURAMENTO"


INDICATORS = _Indicators()
