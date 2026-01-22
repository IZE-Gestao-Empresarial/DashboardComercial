from __future__ import annotations

from core.formatters import fmt_int


def simple_total_card_html(title: str, value: float | None, subtitle: str | None = None) -> str:
    """Card simples: título + número grande."""
    v = fmt_int(value)
    sub = subtitle or ""
    sub_html = f'<div class="text-zinc-500 mt-2" style="font-size: var(--fs-sub);">{sub}</div>' if sub else ""

    return f'''
    <div class="bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full flex flex-col justify-center"
         style="padding: calc(var(--pad) * 1.2);">
      <div class="font-extrabold text-zinc-900" style="font-size: var(--fs-title);">
        {title}
      </div>
      {sub_html}
      <div class="mt-4 font-extrabold text-zinc-900 tabular-nums"
           style="font-size: clamp(36px, 3.2vw, 64px); line-height: 1;">
        {v}
      </div>
    </div>
    '''
