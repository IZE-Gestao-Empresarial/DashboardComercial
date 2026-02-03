from __future__ import annotations

from core.formatters import fmt_int


def simple_total_card_html(title: str, value: float | None, subtitle: str | None = None) -> str:
    """Card simples no MESMO padrão de disposição da conversão geral."""
    v = fmt_int(value)

    sub = (subtitle or title).strip()

    return f"""
    <div class="bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full flex flex-col justify-center overflow-hidden"
         style="padding: var(--pad);">
      <div class="font-extrabold text-zinc-900" style="font-size: var(--fs-title);">{title}</div>

      <div class="mt-3 font-extrabold text-zinc-900 tabular-nums"
           style="font-size: clamp(30px, 2.7vw, 56px); line-height: 1;">
        {v}
      </div>

      <div class="text-zinc-500 mt-2" style="font-size: var(--fs-sub);">
        {sub}
      </div>
    </div>
    """