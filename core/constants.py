from dataclasses import dataclass

# =========================
# Config central
# =========================
REFRESH_MS = 600_000         # 5 min em ms
CACHE_TTL_SECONDS = 250     # 250s (4 min e 10s)
SHEET_ID = "1AFGtJnXdqb6KfmXOmSfFbSR_cmGho5d8d1yd9HX6RUo"
SHEET_GID = "0"

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
    TAX_CONV_FUNIL_1: str = "PRODUTIVIDADE POR EVENTOS DO PERÍODO 1"
    TAX_CONV_FUNIL_2: str = "PRODUTIVIDADE POR EVENTOS DO PERÍODO 2"

    # ✅ Ranking Closer: percentual deve vir do indicador (por responsável)
    TAXA_CONVERSAO_CLOSER: str = "TAXA DE CONVERS\u00c3O DO CLOSER"

INDICATORS = _Indicators()
