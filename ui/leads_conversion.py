from __future__ import annotations

import html
import math

from core.formatters import fmt_int
from ui.ranklist import fmt_percent_br


def _dot_ring_svg(percent: float, *, size: int = 260, dots: int = 18) -> str:
    """Anel de pontos (visual do cliente).

    Regras visuais (referência do cliente):
    - pontos laranja concentrados no lado esquerdo (9h)
    - crescimento simétrico (um acima e um abaixo do ponto âncora)
    - para percentuais baixos, mantém um mínimo visual de 3 pontos acesos
    """
    pct = max(0.0, min(100.0, float(percent or 0.0)))

    # quantos pontos "acesos"
    on = int(math.ceil((pct / 100.0) * dots))
    if pct > 0 and on < 3:
        on = 3
    on = max(0, min(dots, on))

    # índices acesos em torno do ponto âncora (i=0)
    # ordem: 0, +1, -1, +2, -2...
    on_idx: set[int] = set()
    if on > 0:
        on_idx.add(0)
        step = 1
        sign = 1
        while len(on_idx) < on:
            on_idx.add((sign * step) % dots)
            sign *= -1
            if sign > 0:
                step += 1

    cx = cy = size / 2
    r = size * 0.38
    dot_r = size * 0.033

    circles = []
    for i in range(dots):
        # começa no lado esquerdo (9h) e segue no sentido horário
        ang = math.pi + (math.pi * 2) * (i / dots)
        x = cx + r * math.cos(ang)
        y = cy + r * math.sin(ang)
        fill = "#F05914" if i in on_idx else "#2B2B2B"
        circles.append(
            f"<circle cx='{x:.2f}' cy='{y:.2f}' r='{dot_r:.2f}' fill='{fill}' />"
        )

    return f"""<svg class='lc-ring' viewBox='0 0 {size} {size}' width='{size}' height='{size}' aria-hidden='true'>
      {''.join(circles)}
    </svg>"""


def leads_conversion_card_html(
    *,
    leads_total: float | int | None,
    taxa_conversao: float | None,
    title: str = "Leads | Taxa de Conversão (Geral)",
) -> str:
    """Card do cliente: anel + pill (sem alterar o restante do layout)."""

    leads_txt = fmt_int(leads_total)
    pct = float(taxa_conversao or 0.0)

    # "22,0 %"
    if taxa_conversao is None:
        pct_txt = "-"
    else:
        pct_txt = fmt_percent_br(pct).replace("%", " %")

    ring = _dot_ring_svg(pct, size=260, dots=18)

    # Importante: não cria wrapper global (bg-white etc).
    # A tile do template já controla o slot; este painel é o visual cinza do cliente.
    return f"""
    <div class="lc-panel" role="group" aria-label="{html.escape(title)}">
      <div class="lc-left">
        <div class="lc-ring-wrap">
          {ring}
          <div class="lc-center">
            <div class="lc-center-val">{html.escape(pct_txt)}</div>
            <div class="lc-center-sub">Taxa de Conversão</div>
          </div>
        </div>
      </div>

      <div class="lc-right">
        <div class="lc-right-wrap">
          <div class="lc-pill">
            <div class="lc-pill-val">{html.escape(leads_txt)}</div>
          </div>
          <div class="lc-pill-sub">Leads Criados</div>
        </div>
      </div>
    </div>
    """