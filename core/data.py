from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import pandas as pd
import requests
import streamlit as st


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
        r = requests.get(_url, params={"token": _token}, timeout=25)
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

    for col in ["INDICADORES", "RESPONSÁVEL"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()

    if "VALOR" in df.columns:
        df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce")

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
        d = d[d["RESPONSÁVEL"] == responsavel]
    if d.empty:
        return None
    return d.iloc[-1]["VALOR"]
