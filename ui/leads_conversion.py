from __future__ import annotations

import html
import math

from core.formatters import fmt_int
from core.formatters import pct_to_float_percent


def _pct_br_compact(percent: float | None) -> str:
    """
    Formata percent (ex.: 22.0 -> '22 %', 7.8 -> '7,8 %', -5.0 -> '-5 %').
    - 1 casa decimal quando necessário
    - remove '.0'
    - usa vírgula pt-BR
    """
    if percent is None:
        return "-"

    try:
        v = float(percent)
    except Exception:
        return "-"

    if math.isnan(v) or math.isinf(v):
        return "-"

    # Decide se mostra decimal
    if abs(v - round(v)) < 1e-9:
        s = str(int(round(v)))
    else:
        s = f"{v:.1f}".replace(".", ",")
        if s.endswith(",0"):
            s = s[:-2]

    return f"{s} %"


def _dot_ring_svg(percent: float, *, size: int = 360) -> str:
    """Anel de pontos idêntico ao visual 'Taxa de Conversão (3)'.

    - Total de 15 pontos.
    - Preenchimento sentido horário.
    - Ponto de partida ajustado (~150 graus).
    """
    pct = max(0.0, min(100.0, float(percent or 0.0)))

    dots_total = 15
    on = int(math.ceil((pct / 100.0) * dots_total))

    if pct > 0 and on < 1:
        on = 1
    on = max(0, min(dots_total, on))

    on_idx: set[int] = set(range(on))

    cx = cy = size / 2
    r = size * 0.42
    dot_r = size * 0.048

    circles: list[str] = []

    start_angle = math.radians(150)
    step = (2 * math.pi) / dots_total

    for i in range(dots_total):
        ang = start_angle + (step * i)
        x = cx + r * math.cos(ang)
        y = cy + r * math.sin(ang)

        fill = "#F4561F" if i in on_idx else "#403D38"
        circles.append(
            f"<circle cx='{x:.2f}' cy='{y:.2f}' r='{dot_r:.2f}' fill='{fill}' />"
        )

    return f"""<svg class='lc-ring' viewBox='0 0 {size} {size}' aria-hidden='true'>
      {''.join(circles)}
    </svg>"""


def leads_conversion_card_html(
    *,
    leads_total: float | int | None,
    taxa_conversao: float | None,
    title: str = "Leads | Taxa de Conversão (Geral)",
) -> str:
    """Card 'Taxa de Conversão | Leads' (Design Prototipo 3)."""

    leads_txt = fmt_int(leads_total)

    # taxa_conversao aqui deve ser RATIO (ex.: 0.22) -> percent (22.0)
    pct = pct_to_float_percent(taxa_conversao)

    pct_txt = _pct_br_compact(pct) if taxa_conversao is not None else "-"

    ring = _dot_ring_svg(pct, size=300)

    return f"""<div class='lc-card' aria-label='{html.escape(title)}'>

      <div class='lc-gauge-side'>
        <div class='lc-ring-wrap'>
          {ring}
          <div class='lc-ring-text'>
            <div class='lc-pct'>{html.escape(pct_txt)}</div>
            <div class='lc-label'>Taxa de Conversão</div>
          </div>
        </div>
      </div>

      <div class='lc-data-side'>
        <div class='lc-pill'>
          {html.escape(leads_txt)}
        </div>
        <div class='lc-data-label'>Leads Criados</div>
      </div>

    </div>"""
