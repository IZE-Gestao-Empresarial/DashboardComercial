from __future__ import annotations

from typing import Iterable, Optional
import math
import pandas as pd
import re

def _is_nan(x) -> bool:
    return x is None or (isinstance(x, float) and math.isnan(x))


_CLEAN_INVISIBLE_RE = re.compile(r"[\u200B-\u200F\uFEFF\u00AD]")

def _norm(s: str) -> str:
    s = str(s or "")
    s = _CLEAN_INVISIBLE_RE.sub("", s)
    s = s.replace("\u00A0", " ")
    s = " ".join(s.split())
    return s.strip().upper()



def total_for_indicator(
    df_latest: pd.DataFrame,
    indicador: str,
    prefer_responsavel: Optional[str] = None,
    exclude_responsaveis: Optional[Iterable[str]] = None,
) -> Optional[float]:
    """
    Total de um indicador.
    - Se existir linha do indicador com responsavel == prefer_responsavel, usa ela.
    - Senão soma todas as linhas do indicador (exceto exclude_responsaveis).
    """
    if df_latest is None or df_latest.empty:
        return None

    indicador_u = _norm(indicador)
    d = df_latest[df_latest["INDICADORES"] == indicador_u].copy()
    if d.empty:
        return None

    if exclude_responsaveis:
        excl = {_norm(x) for x in exclude_responsaveis}
        d = d[~d["RESPONSÁVEL"].isin(excl)]

    if prefer_responsavel:
        pr = _norm(prefer_responsavel)
        p = d[d["RESPONSÁVEL"] == pr]
        if not p.empty:
            v = p.iloc[-1]["VALOR"]
            return None if _is_nan(v) else float(v)

    vals = pd.to_numeric(d["VALOR"], errors="coerce")
    if vals.notna().any():
        return float(vals.sum())
    return None


def people_values(
    df_latest: pd.DataFrame,
    indicador: str,
    exclude_responsaveis: Optional[Iterable[str]] = None,
) -> list[dict]:
    """Retorna lista [{name, value}] por responsável para um indicador."""
    if df_latest is None or df_latest.empty:
        return []

    indicador_u = _norm(indicador)
    d = df_latest[df_latest["INDICADORES"] == indicador_u].copy()
    if d.empty:
        return []

    if exclude_responsaveis:
        excl = {_norm(x) for x in exclude_responsaveis}
        d = d[~d["RESPONSÁVEL"].isin(excl)]

    d["VALOR"] = pd.to_numeric(d["VALOR"], errors="coerce")
    d = d[d["VALOR"].notna()]

    return [{"name": str(r["RESPONSÁVEL"]), "value": float(r["VALOR"])} for _, r in d.iterrows()]


def shares_from_values(items: list[dict]) -> list[dict]:
    """Converte [{name, value}] em [{name, value, percent}] com percent em 0..100."""
    total = sum(float(x.get("value") or 0.0) for x in items)
    out = []
    for x in items:
        v = float(x.get("value") or 0.0)
        pct = (v / total * 100.0) if total > 0 else 0.0
        out.append({"name": x.get("name", ""), "value": v, "percent": pct})
    out.sort(key=lambda t: t["value"], reverse=True)
    return out


def top_n_with_others(items: list[dict], n: int, others_label: str = "OUTROS") -> list[dict]:
    """Mantém top N por 'value' e agrega o resto em OUTROS."""
    if n <= 0 or len(items) <= n:
        return items

    top = items[:n]
    rest = items[n:]
    rest_value = sum(float(x.get("value") or 0.0) for x in rest)
    if rest_value <= 0:
        return top

    top_total = sum(float(x.get("value") or 0.0) for x in top) + rest_value
    out = []
    for x in top:
        v = float(x.get("value") or 0.0)
        pct = (v / top_total * 100.0) if top_total > 0 else 0.0
        out.append({**x, "percent": pct})
    out.append(
        {
            "name": others_label,
            "value": rest_value,
            "percent": (rest_value / top_total * 100.0) if top_total > 0 else 0.0,
        }
    )
    return out


def to_percent_value(v: Optional[float]) -> float:
    """Normaliza taxa para 0..100 (aceita ratio 0..1 ou percent 0..100)."""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return 0.0
    v = float(v)
    if 0.0 <= v <= 1.5:
        return max(0.0, min(100.0, v * 100.0))
    return max(0.0, min(100.0, v))
