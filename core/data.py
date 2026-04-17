from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import pandas as pd
import requests
import streamlit as st
import re

from core.normalize import norm_text as _norm_text_no_alias

_CLEAN_INVISIBLE_RE = re.compile(r"[\u200B-\u200F\uFEFF\u00AD]")

# ✅ aliases globais de responsáveis (já em UPPER)
_RESPONSAVEL_ALIASES = {
    "MARIA EDUARDA": "MARIA",
}

def _norm_text(s: object) -> str:
    """
    Normaliza texto vindo do Sheets:
    - remove invisíveis (zero-width, BOM, soft hyphen)
    - troca NBSP por espaço
    - colapsa espaços
    - strip + UPPER
    - aplica aliases (ex.: 'MARIA EDUARDA' -> 'MARIA')
    """
    s = "" if s is None else str(s)
    s = _CLEAN_INVISIBLE_RE.sub("", s)
    s = s.replace("\u00A0", " ")  # NBSP
    s = " ".join(s.split())       # colapsa whitespace
    s = s.strip().upper()

    # ✅ aplica alias depois de normalizar
    return _RESPONSAVEL_ALIASES.get(s, s)

def _parse_number(v: object) -> float | None:
    """Converte número vindo do Sheets/JSON para float.

    Suporta strings em pt-BR (ex.: "98.874,00", "0,1746", "500.000") e também
    valores já numéricos.
    """
    if v is None:
        return None

    if isinstance(v, (int, float)):
        try:
            return float(v)
        except Exception:
            return None

    s = str(v).strip()
    if not s or s == "-":
        return None

    s = s.replace("R$", "").replace("%", "").strip()
    s = s.replace("\u00A0", " ")
    s = s.replace(" ", "")

    # mantém apenas dígitos, sinal e separadores
    m = re.search(r"-?[\d\.,]+", s)
    if not m:
        return None
    num = m.group(0)

    if "." in num and "," in num:
        # se a última vírgula vem depois do último ponto, vírgula é decimal
        if num.rfind(",") > num.rfind("."):
            num = num.replace(".", "").replace(",", ".")
        else:
            num = num.replace(",", "")
    elif "," in num and "." not in num:
        # vírgula como decimal
        num = num.replace(".", "").replace(",", ".")
    else:
        # somente pontos: pode ser decimal OU milhar ("500.000")
        parts = num.split(".")
        if len(parts) > 1 and all(p.isdigit() for p in parts) and len(parts[-1]) == 3:
            num = "".join(parts)

    try:
        return float(num)
    except Exception:
        return None


def _safe_json(resp: requests.Response) -> Dict[str, Any]:
    try:
        return resp.json()
    except Exception:
        return {
            "error": "Resposta não-JSON do endpoint",
            "status_code": resp.status_code,
            "text": resp.text[:400],
        }


def fetch_payload(url: str, token: str, ttl_seconds: int = 4) -> Dict[str, Any]:
    """
    Busca o JSON do Apps Script WebApp.
    Cache (TTL) é aplicado aqui pra reduzir a carga e evitar rate-limit.
    """

    @st.cache_data(ttl=ttl_seconds, show_spinner=False)
    def _fetch(_url: str, _token: str) -> Dict[str, Any]:
        r = requests.get(_url, params={"token": _token}, timeout=60)
        r.raise_for_status()
        return _safe_json(r)

    return _fetch(url, token)


def payload_to_df(payload: Dict[str, Any]) -> Tuple[pd.DataFrame, Optional[str], Optional[str]]:
    updated_at = payload.get("updatedAt")
    sheet = payload.get("sheet")

    rows = payload.get("rows", [])
    df = pd.DataFrame(rows)

    if df.empty:
        return df, updated_at, sheet

    if "RESPONSÁVEL" in df.columns:
        df["RESPONSÁVEL_ORIGINAL"] = df["RESPONSÁVEL"].apply(_norm_text_no_alias)
        df["RESPONSÁVEL"] = df["RESPONSÁVEL"].apply(_norm_text)

    if "INDICADORES" in df.columns:
        df["INDICADORES"] = df["INDICADORES"].apply(_norm_text)

    if "VALOR" in df.columns:
        df["VALOR"] = df["VALOR"].apply(_parse_number)

    if "DATA_ATUALIZAÇÃO" in df.columns:
        df["DATA_ATUALIZAÇÃO"] = pd.to_datetime(df["DATA_ATUALIZAÇÃO"], errors="coerce", utc=True)

    return df, updated_at, sheet


def latest_values(df: pd.DataFrame) -> pd.DataFrame:
    """Mantém a última linha por (RESPONSÁVEL, INDICADORES), usando DATA_ATUALIZAÇÃO se existir."""
    if df.empty:
        return df
    d = df.copy()
    if "DATA_ATUALIZAÇÃO" in d.columns and d["DATA_ATUALIZAÇÃO"].notna().any():
        d = d.sort_values("DATA_ATUALIZAÇÃO")
    d = d.drop_duplicates(subset=["RESPONSÁVEL", "INDICADORES"], keep="last")
    return d


def get_val(df_latest: pd.DataFrame, indicador: str, responsavel: Optional[str] = None) -> Optional[float]:
    """Pega VALOR do indicador para um responsável (se informado)."""
    indicador = indicador.strip().upper()
    d = df_latest[df_latest["INDICADORES"] == indicador]
    if responsavel:
        responsavel = responsavel.strip().upper()
        # ✅ aplica alias também aqui (caso você passe "MARIA EDUARDA" em algum lugar)
        responsavel = _RESPONSAVEL_ALIASES.get(responsavel, responsavel)
        d = d[d["RESPONSÁVEL"] == responsavel]
    if d.empty:
        return None
    return d.iloc[-1]["VALOR"]
