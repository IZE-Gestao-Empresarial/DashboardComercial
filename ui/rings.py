from __future__ import annotations

import math
import html

from ui.avatars import avatar_html
from core.people import pretty_name


def donut_svg(segments: list[dict], size: int = 210, stroke: int = 18) -> str:
    """Donut completo com segmentos (stroke-dasharray)."""
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
        rings.append(f'''
            <circle cx="{size/2}" cy="{size/2}" r="{r}"
                    fill="transparent"
                    stroke="{color}"
                    stroke-width="{stroke}"
                    stroke-linecap="butt"
                    stroke-dasharray="{length:.3f} {gap:.3f}"
                    stroke-dashoffset="{-start:.3f}" />
        ''')
        start += length

    bg = f'''
      <circle cx="{size/2}" cy="{size/2}" r="{r}"
              fill="transparent" stroke="#E5E7EB" stroke-width="{stroke}" />
    '''
    return f'''
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" aria-hidden="true">
      {bg}
      {''.join(rings)}
    </svg>
    '''


def reuniões_por_pessoa_card_html(title: str, items: list[dict]) -> str:
    """Card: donut + lista com avatar, nome e %."""
    if not items:
        return f'''
        <div class="bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full flex items-center justify-center">
          <div class="text-zinc-500 font-semibold">Sem dados de {title}</div>
        </div>
        '''

    donut = donut_svg(items, size=230, stroke=18)

    rows = []
    for s in items:
        name_u = str(s.get("name") or "").strip().upper()
        nm = html.escape(pretty_name(name_u))
        pct = float(s.get("percent") or 0.0)
        val = float(s.get("value") or 0.0)

        rows.append(f'''
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3 min-w-0">
              {avatar_html(name_u, size_px=40)}
              <div class="min-w-0">
                <div class="font-semibold text-zinc-900 truncate" style="font-size: var(--fs-label);">{nm}</div>
                <div class="text-zinc-500 tabular-nums" style="font-size: var(--fs-sub);">{int(round(val))} reuniões</div>
              </div>
            </div>
            <div class="font-extrabold text-zinc-900 tabular-nums" style="font-size: var(--fs-kpi);">{pct:.1f}%</div>
          </div>
        ''')

    return f'''
    <div class="bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full" style="padding: var(--pad);">
      <div class="font-extrabold text-zinc-900" style="font-size: var(--fs-title);">{title}</div>

      <div class="mt-4 flex items-center justify-between gap-6">
        <div class="flex items-center justify-center" style="min-width: 240px;">
          {donut}
        </div>

        <div class="flex-1 space-y-3">
          {''.join(rows)}
        </div>
      </div>
    </div>
    '''
