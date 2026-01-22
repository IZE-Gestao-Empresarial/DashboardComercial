from __future__ import annotations

import html

from ui.avatars import avatar_html
from core.people import pretty_name


def conversion_general_card_html(title: str, percent: float) -> str:
    """Card: taxa geral grande."""
    return f'''
    <div class="bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full flex flex-col justify-center"
         style="padding: calc(var(--pad) * 1.2);">
      <div class="font-extrabold text-zinc-900" style="font-size: var(--fs-title);">{title}</div>
      <div class="mt-4 font-extrabold text-zinc-900 tabular-nums"
           style="font-size: clamp(36px, 3.2vw, 64px); line-height: 1;">
        {percent:.1f}%
      </div>
      <div class="text-zinc-500 mt-2" style="font-size: var(--fs-sub);">
        Taxa de conversão (geral)
      </div>
    </div>
    '''


def conversion_people_card_html(title: str, items: list[dict]) -> str:
    """Lista por pessoa com barra."""
    if not items:
        return f'''
        <div class="bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full flex items-center justify-center">
          <div class="text-zinc-500 font-semibold">Sem dados de {title}</div>
        </div>
        '''

    rows = []
    for it in items:
        name_u = str(it.get("name") or "").strip().upper()
        pct = float(it.get("percent") or 0.0)
        nm = html.escape(pretty_name(name_u))

        rows.append(f'''
          <div class="flex items-center gap-3">
            {avatar_html(name_u, size_px=38)}
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between gap-2">
                <div class="font-semibold text-zinc-900 truncate" style="font-size: var(--fs-label);">{nm}</div>
                <div class="font-extrabold text-zinc-900 tabular-nums" style="font-size: var(--fs-label);">{pct:.1f}%</div>
              </div>
              <div class="mt-2 h-2 rounded-full bg-zinc-200 overflow-hidden">
                <div class="h-full bg-[#F05914]" style="width: {max(0.0, min(100.0, pct)):.1f}%;"></div>
              </div>
            </div>
          </div>
        ''')

    return f'''
    <div class="bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full" style="padding: var(--pad);">
      <div class="font-extrabold text-zinc-900" style="font-size: var(--fs-title);">{title}</div>
      <div class="mt-4 space-y-4">
        {''.join(rows)}
      </div>
    </div>
    '''
