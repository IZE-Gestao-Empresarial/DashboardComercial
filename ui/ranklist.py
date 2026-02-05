from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Optional

import streamlit as st

from core.people import pretty_name
from ui.avatars import avatar_html
from ui.embed import file_to_data_uri
from ui.render import load_asset_text


def fmt_percent_br(p: float) -> str:
    """Formata percent em pt-BR (ex.: 55,5%)."""
    return f"{p:.1f}".replace(".", ",") + "%"


def _medal_data_uri(rank: int) -> str | None:
    """Tenta encontrar um PNG de colocação em assets/svg e retornar como data URI."""
    candidates = [
        f"assets/svg/rank_{rank}.png",
        f"assets/svg/rank-{rank}.png",
        f"assets/svg/podium_{rank}.png",
        f"assets/svg/podium-{rank}.png",
    ]
    if rank == 1:
        candidates += ["assets/svg/first.png", "assets/svg/ouro.png"]
    if rank == 2:
        candidates += ["assets/svg/second.png", "assets/svg/prata.png"]

    for rel in candidates:
        uri = file_to_data_uri(rel)
        if uri:
            return uri
    return None


def _medal_html(rank: int) -> str:
    uri = _medal_data_uri(rank)
    if uri:
        return f"<img class='rk-medal-img' src='{uri}' alt='{rank}º' />"
    return f"<div class='rk-medal-fallback'>{rank}</div>"


def _fmt_pct_compact(raw) -> str | None:
    """
    Normaliza um percentual para exibição curta (ex.: '15%').
    Aceita:
      - '15%' (string) -> '15%'
      - 0.15 (float) -> '15%'
      - 15 (int/float) -> '15%'
    """
    if raw is None:
        return None

    if isinstance(raw, str):
        s = raw.strip()
        if not s:
            return None

        if "%" in s:
            m = re.search(r"(-?\d+[.,]?\d*)\s*%", s)
            if m:
                try:
                    x = float(m.group(1).replace(",", "."))
                    return f"{int(round(x))}%"
                except Exception:
                    return None
            return s

        m = re.search(r"(-?\d+[.,]?\d*)", s)
        if not m:
            return None
        try:
            raw = float(m.group(1).replace(",", "."))
        except Exception:
            return None

    try:
        x = float(raw)
    except Exception:
        return None

    if 0.0 <= x <= 1.0:
        x *= 100.0

    return f"{int(round(x))}%"


def _norm_key(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").strip().lower())


def _get_value_by_key_fuzzy(it: dict, wanted_key: str):
    """Busca valor por chave exata ou por comparação normalizada."""
    if wanted_key in it:
        return it.get(wanted_key)

    w = _norm_key(wanted_key)
    if not w:
        return None

    for k in it.keys():
        if _norm_key(str(k)) == w:
            return it.get(k)
    return None


def _closer_pct_from_row(it: dict, pct_field: str) -> str | None:
    v = _get_value_by_key_fuzzy(it, pct_field)
    pct = _fmt_pct_compact(v)
    if pct is not None:
        return pct

    for k in ("pct", "percent", "percentual", "perc", "taxa", "taxa_fechamento", "pct_closer"):
        v2 = it.get(k)
        pct2 = _fmt_pct_compact(v2)
        if pct2 is not None:
            return pct2

    return None


# ============================================================
# CSS isolado do Ranklist
# - Arquivo: assets/css/ranklist.css
# - Escopo: .rk-scope
# - Cache seguro: depende do mtime do arquivo
# ============================================================

def _ranklist_css_file() -> Path:
    # Relativo ao projeto: ui/ -> (base_dir)/assets/css/ranklist.css
    base_dir = Path(__file__).resolve().parent.parent
    return base_dir / "assets" / "css" / "ranklist.css"


@st.cache_data(show_spinner=False)
def _load_ranklist_css_cached(_mtime: float) -> str:
    # usa o seu loader já cacheado, mas chaveado pelo mtime
    return load_asset_text("assets/css/ranklist.css")


def _ranklist_css_tag() -> str:
    p = _ranklist_css_file()
    if not p.exists():
        return ""  # <- se o arquivo sumiu, não injeta CSS

    try:
        css = _load_ranklist_css_cached(p.stat().st_mtime)
    except Exception:
        return ""

    if not css.strip():
        return ""

    return f"<style>\n{css}\n</style>"


def ranking_sdr_card_html(
    *,
    title: str,
    items: list[dict],
    limit: int = 2,
    avatar_size_px: int = 56,
) -> str:
    """Ranking SDR no layout do mock (pills com 2 colunas: Reuniões + Conversão)."""

    css_tag = _ranklist_css_tag()

    if not items:
        return f"""
        {css_tag}
        <div class="rk-scope">
          <div class="bg-white rounded-xl shadow-sm border border-zinc-100 h-full w-full flex items-center justify-center">
            <div class="text-zinc-500 font-semibold">Sem dados</div>
          </div>
        </div>
        """

    rows = items[: max(0, int(limit) or 2)]

    rows_html: list[str] = []
    for idx, it in enumerate(rows, start=1):
        name_u = str(it.get("name") or "").strip().upper()
        name_pretty = html.escape(pretty_name(name_u))

        reun = it.get("reunioes")
        try:
            reun_int = int(float(reun or 0))
        except Exception:
            reun_int = 0

        conv = it.get("conversao")
        try:
            conv_f = float(conv or 0.0)
        except Exception:
            conv_f = 0.0

        rows_html.append(
            f"""
            <div class='rk-row' data-rank='{idx}'>
              <div class='rk-medal'>{_medal_html(idx)}</div>

              <div class='rk-row-main'>
                <div class='rk-pill rk-pill-sdr'>
                  <div class='rk-name'>{name_pretty}</div>

                  <div class='rk-metrics'>
                    <div class='rk-metric'>
                      <div class='rk-label'>Reuniões</div>
                      <div class='rk-value'>{reun_int}</div>
                    </div>
                    <div class='rk-metric'>
                      <div class='rk-label'>Conversão (%)</div>
                      <div class='rk-value'>{int(round(conv_f))}%</div>
                    </div>
                  </div>

                  <div class='rk-avatar'>
                    {avatar_html(name_u, size_px=avatar_size_px, ring_px=0)}
                  </div>
                </div>
              </div>
            </div>
            """
        )

    return f"""
      {css_tag}
      <div class="rk-scope">
        <div class='rk-card bg-[#FFFFFF] rounded-xl shadow-sm border border-zinc-100 h-full w-full flex flex-col overflow-hidden'
            style='padding: var(--rk-pad, var(--pad));'>
          <div class="rk-title-soft" style="font-size: var(--fs-title); line-height: 1.1;">
            {html.escape(title)}
          </div>

          <div class='rk-body'>{''.join(rows_html)}</div>
        </div>
      </div>
    """


def ranking_closer_card_html(
    *,
    title: str,
    rows: list[dict],
    limit: int = 2,
    avatar_size_px: int = 56,
    money_prefix: str = "R$ ",
    pct_field: str = "PERC FATURAMENTO PAGO",
) -> str:
    """Ranking Closer no layout do mock (pills com 2 colunas: Fat. Assinado + Fat. Pago)."""

    css_tag = _ranklist_css_tag()

    if not rows:
        return f"""
        {css_tag}
        <div class="rk-scope">
          <div class="bg-white rounded-xl shadow-sm border border-zinc-100 h-full w-full flex items-center justify-center">
            <div class="text-zinc-500 font-semibold">Sem dados</div>
          </div>
        </div>
        """

    def _k(r: dict) -> float:
        try:
            return float(r.get("fat_pago") or 0.0)
        except Exception:
            return 0.0

    ordered = sorted(rows, key=_k, reverse=True)[: max(0, int(limit) or 2)]

    def _money(v) -> str:
        if v is None:
            return "-"
        return str(v)

    rows_html: list[str] = []
    for idx, it in enumerate(ordered, start=1):
        name_u = str(it.get("name") or "").strip().upper()
        name_pretty = html.escape(pretty_name(name_u))

        contratos = it.get("contratos")
        try:
            if isinstance(contratos, str):
                s = re.sub(r"\D", "", contratos)
                contratos_int = int(s or 0)
            else:
                contratos_int = int(float(contratos or 0))
        except Exception:
            contratos_int = 0

        pct_txt = _closer_pct_from_row(it, pct_field)

        fa_txt = _money(it.get("fat_assinado"))
        fp_txt = _money(it.get("fat_pago"))

        pct_html = ""
        if pct_txt is not None:
            pct_html = f"<div class='rk-name-pct'>{html.escape(str(pct_txt))}</div>"

        rows_html.append(
            f"""
            <div class='rk-row' data-rank='{idx}'>
              <div class='rk-medal'>{_medal_html(idx)}</div>

              <div class='rk-row-main'>
                <div class='rk-pill rk-pill-closer'>
                  <div class='rk-name'>
                    <div class='rk-name-main'>{name_pretty}</div>
                    <div class='rk-name-sub'>{contratos_int} contratos</div>
                    {pct_html}
                  </div>

                  <div class='rk-metrics'>
                    <div class='rk-metric'>
                      <div class='rk-label'>Fat. Assinado</div>
                      <div class='rk-value'>{html.escape(str(fa_txt))}</div>
                    </div>
                    <div class='rk-metric'>
                      <div class='rk-label'>Fat. Pago</div>
                      <div class='rk-value'>{html.escape(str(fp_txt))}</div>
                    </div>
                  </div>

                  <div class='rk-avatar'>
                    {avatar_html(name_u, size_px=avatar_size_px, ring_px=0)}
                  </div>
                </div>
              </div>
            </div>
            """
        )

    return f"""
      {css_tag}
      <div class="rk-scope">
        <div class='rk-card bg-[#FFFFFF] rounded-xl shadow-sm border border-zinc-100 h-full w-full flex flex-col overflow-hidden'
            style='padding: var(--rk-pad, var(--pad));'>
          <div class="rk-title-soft" style="font-size: var(--fs-title); line-height: 1.1;">
            {html.escape(title)}
          </div>
          <div class='rk-body'>{''.join(rows_html)}</div>
        </div>
      </div>
    """