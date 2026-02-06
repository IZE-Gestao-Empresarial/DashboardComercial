from dataclasses import dataclass

# =========================
# Config central
# =========================
REFRESH_MS = 300_000        # 30s em ms
CACHE_TTL_SECONDS = 270     # 25s

@dataclass(frozen=True)
class _Indicators:
    # Indicadores (normalizamos pra UPPER)
    REUNIOES_REAL: str = "REUNIÕES OCORRIDAS"
    REUNIOES_META: str = "REUNIÕES OCORRIDAS - META"
    REUNIOES_PERC: str = "PERC META REUNIÕES OCORRIDAS"
    REUNIOES_DIF:  str = "DIF META REUNIÕES OCORRIDAS"
    REUNIOES_CRESC: str = "PERC CRESCIMENTO REUNIOES"

    FAT_REAL: str = "FATURAMENTO PAGO"         
    FAT_FALLBACK_REAL: str = "FATURAMENTO"
    FAT_META: str = "FATURAMENTO - META"
    FAT_PERC: str = "PERC META FATURAMENTO"
    FAT_DIF:  str = "DIF META FATURAMENTO"
    FAT_CRESC: str = "PERC CRESCIMENTO FATURAMENTO"

    # Novos cards (básico)
    LEADS_CRIADOS: str = "LEADS CRIADOS"
    TAXA_CONVERSAO: str = "TAXA DE CONVERSÃO"
    CONTRATOS_ASSINADOS: str = "CONTRATOS ASSINADOS"
    FATURAMENTO_ASSINADO: str = "FATURAMENTO ASSINADO"
    FATURAMENTO_PAGO: str = "FATURAMENTO PAGO"
    TAX_CONV_FUNIL_1: str = "TAXA DE CONVERSÃO FUNIL 1"
    TAX_CONV_FUNIL_2: str = "TAXA DE CONVERSÃO FUNIL 2"

INDICATORS = _Indicators()
