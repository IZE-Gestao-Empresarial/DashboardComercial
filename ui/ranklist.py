from __future__ import annotations

import html
from typing import Callable, Optional

from core.people import pretty_name
from ui.avatars import avatar_html


def fmt_percent_br(p: float) -> str:
    """Formata percent em pt-BR (ex.: 55,5%)."""
    return f"{p:.1f}".replace(".", ",") + "%"


def ranklist_card_html(
    title: str,
    items: list[dict],
    *,
    value_fn: Callable[[dict], str],
    sub_fn: Optional[Callable[[dict], str]] = None,
    empty_text: Optional[str] = None,
    avatar_size_px: int = 70,
) -> str:
    """Card no padrão do (ranking em pills).

    items: lista de dicts com pelo menos a chave 'name' (em UPPER ou não).
    value_fn/sub_fn: retornam as strings já formatadas para exibição.
    """

    if not items:
        msg = empty_text or f"Sem dados de {title}"
        return f"""
        <div class="bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full flex items-center justify-center">
          <div class="text-zinc-500 font-semibold">{html.escape(msg)}</div>
        </div>
        """

    rows_html: list[str] = []
    for idx, it in enumerate(items, start=1):
        name_u = str(it.get("name") or "").strip().upper()
        name_pretty = html.escape(pretty_name(name_u))

        value_text = html.escape(value_fn(it) or "")
        sub_text = sub_fn(it) if sub_fn else None
        sub_html = f'<div class="rl-sub">{html.escape(sub_text)}</div>' if sub_text else ""

        # Top 1 ganha um pouco mais de destaque (aro do avatar mais grosso)
        ring_px = 4 if idx == 1 else 2

        rows_html.append(
            f"""
            <div class="rl-row" data-rank="{idx}">
              <div class="rl-badge">{idx}</div>
              <div class="rl-pill">
                <div class="rl-text">
                  <div class="rl-name">{name_pretty}</div>
                  <div class="rl-value">{value_text}</div>
                  {sub_html}
                </div>
                <div class="rl-avatar">{avatar_html(name_u, size_px=avatar_size_px, ring_px=ring_px)}</div>
              </div>
            </div>
            """
        )

    return f"""
    <div class="ranklist-card bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full flex flex-col overflow-hidden" style="padding: var(--pad);">
      <div class="font-extrabold text-zinc-900" style="font-size: var(--fs-title); line-height: 1.1;">{html.escape(title)}</div>
      <div class="ranklist-body">{''.join(rows_html)}</div>
    </div>
    """
