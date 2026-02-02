from __future__ import annotations

import html
import re
from typing import Callable, Optional

from core.people import pretty_name
from ui.avatars import avatar_html
from ui.embed import file_to_data_uri


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


def ranking_sdr_card_html(
    *,
    title: str,
    items: list[dict],
    limit: int = 2,
    avatar_size_px: int = 56,
) -> str:
    """Ranking SDR no layout do mock (pills com 2 colunas: Reuniões + Conversão)."""

    if not items:
        return f"""
        <div class="bg-white rounded-xl shadow-sm border border-zinc-100 h-full w-full flex items-center justify-center">
          <div class="text-zinc-500 font-semibold">Sem dados</div>
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

        ring_px = 4 if idx == 1 else 3

        rows_html.append(
            f"""
            <div class='rk-row' data-rank='{idx}'>
              <div class='rk-medal'>{_medal_html(idx)}</div>

              <div class='rk-pill'>
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
            """
        )

    # ✅ TÍTULO no MESMO padrão do KPI (sem bold extra)
    return f"""
      <div class='rk-card bg-[#FFFFFF] rounded-xl shadow-sm border border-zinc-100 h-full w-full flex flex-col overflow-hidden'
          style='padding: var(--rk-pad, var(--pad));'>
<div class="rk-title-soft text-zinc-900" style="font-size: var(--fs-title); line-height: 1.1;">
  {html.escape(title)}
</div>

      <div class='rk-body'>{''.join(rows_html)}</div>
    </div>
    """


def ranking_closer_card_html(
    *,
    title: str,
    rows: list[dict],
    limit: int = 2,
    avatar_size_px: int = 56,
    money_prefix: str = "R$ ",
) -> str:
    """Ranking Closer no layout do mock (pills com 2 colunas: Fat. Assinado + Fat. Pago)."""

    if not rows:
        return f"""
        <div class="bg-white rounded-xl shadow-sm border border-zinc-100 h-full w-full flex items-center justify-center">
          <div class="text-zinc-500 font-semibold">Sem dados</div>
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

        fa_txt = _money(it.get("fat_assinado"))
        fp_txt = _money(it.get("fat_pago"))

        ring_px = 4 if idx == 1 else 3

        rows_html.append(
            f"""
            <div class='rk-row' data-rank='{idx}'>
              <div class='rk-medal'>{_medal_html(idx)}</div>

              <div class='rk-pill rk-pill-closer'>
                <div class='rk-name'>
                  <div class='rk-name-main'>{name_pretty}</div>
                  <div class='rk-name-sub'>{contratos_int} contratos</div>
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
            """
        )

    # ✅ TÍTULO no MESMO padrão do KPI (sem bold extra)
    return f"""
  <div class='rk-card bg-[#FFFFFF] rounded-xl shadow-sm border border-zinc-100 h-full w-full flex flex-col overflow-hidden'
      style='padding: var(--rk-pad, var(--pad));'>
      <div class="rk-title-soft text-zinc-900" style="font-size: var(--fs-title); line-height: 1.1;">
        {html.escape(title)}
      </div>
      <div class='rk-body'>{''.join(rows_html)}</div>
    </div>
    """
