from __future__ import annotations

from ui.ranklist import fmt_percent_br, ranklist_card_html


def conversion_general_card_html(title: str, percent: float) -> str:
    """Card: taxa geral grande."""
    percent_txt = fmt_percent_br(float(percent or 0.0))

    return f"""
    <div class="bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full flex flex-col justify-center overflow-hidden"
         style="padding: var(--pad);">
      <div class="font-extrabold text-zinc-900" style="font-size: var(--fs-title);">{title}</div>
      <div class="mt-3 font-extrabold text-zinc-900 tabular-nums"
           style="font-size: clamp(30px, 2.7vw, 56px); line-height: 1;">
        {percent_txt}
      </div>
      <div class="text-zinc-500 mt-2" style="font-size: var(--fs-sub);">
        Taxa de conversão (geral)
      </div>
    </div>
    """


def conversion_people_card_html(title: str, items: list[dict]) -> str:
    """Ranking por pessoa"""

    def _value(it: dict) -> str:
        try:
            pct = float(it.get("percent") or 0.0)
        except Exception:
            pct = 0.0
        return fmt_percent_br(pct)

    return ranklist_card_html(title=title, items=items, value_fn=_value)
