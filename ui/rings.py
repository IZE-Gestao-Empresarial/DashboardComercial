from __future__ import annotations

import math

from core.formatters import fmt_int
from ui.ranklist import fmt_percent_br, ranklist_card_html


def donut_svg(segments: list[dict], size: int = 210, stroke: int = 18) -> str:
    """Donut completo com segmentos (stroke-dasharray).

    Mantido no projeto para possíveis evoluções, mas no layout atual o card de
    'Reuniões por pessoa' foi padronizado como ranking.
    """
    r = (size - stroke) / 2
    c = 2 * math.pi * r

    palette = ["#F05914", "#111827", "#6B7280", "#D4D4D8", "#FDBA74", "#374151", "#A1A1AA"]
    start = 0.0
    rings = []

    for i, s in enumerate(segments):
        pct = max(0.0, float(s.get("percent") or 0.0))
        length = c * (pct / 100.0)
        gap = c - length
        color = palette[i % len(palette)]
        rings.append(
            f'''
            <circle cx="{size/2}" cy="{size/2}" r="{r}"
                    fill="transparent"
                    stroke="{color}"
                    stroke-width="{stroke}"
                    stroke-linecap="butt"
                    stroke-dasharray="{length:.3f} {gap:.3f}"
                    stroke-dashoffset="{-start:.3f}" />
        '''
        )
        start += length

    bg = f'''
      <circle cx="{size/2}" cy="{size/2}" r="{r}"
              fill="transparent" stroke="#E5E7EB" stroke-width="{stroke}" />
    '''
    return f'''
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" aria-hidden="true" style="width: var(--donut-size); height: var(--donut-size); max-width: 100%; max-height: 100%;">
      {bg}
      {''.join(rings)}
    </svg>
    '''


def reuniões_por_pessoa_card_html(title: str, items: list[dict]) -> str:
    """Card: ranking por pessoa"""

    def _value(it: dict) -> str:
        try:
            pct = float(it.get("percent") or 0.0)
        except Exception:
            pct = 0.0
        return fmt_percent_br(pct)

    def _sub(it: dict) -> str:
        return f"{fmt_int(it.get('value'))} reuniões"

    return ranklist_card_html(title=title, items=items, value_fn=_value, sub_fn=_sub)
