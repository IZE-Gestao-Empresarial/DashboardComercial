from __future__ import annotations

import html

from ui.avatars import avatar_html
from core.people import pretty_name
from core.formatters import fmt_int, fmt_money


def contratos_faturamento_por_pessoa_card_html(title: str, rows: list[dict]) -> str:
    """Card com 3 métricas por pessoa (contratos, fat assinado, fat pago)."""
    if not rows:
        return f'''
        <div class="bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full flex items-center justify-center">
          <div class="text-zinc-500 font-semibold">Sem dados de {title}</div>
        </div>
        '''

    body = []
    for r in rows:
        name_u = str(r.get("name") or "").strip().upper()
        nm = html.escape(pretty_name(name_u))
        contratos = fmt_int(r.get("contratos"))
        fat_a = fmt_money(r.get("fat_assinado"))
        fat_p = fmt_money(r.get("fat_pago"))

        body.append(f'''
          <div class="flex items-start gap-3">
            {avatar_html(name_u, size_px=38)}
            <div class="flex-1 min-w-0">
              <div class="font-semibold text-zinc-900 truncate" style="font-size: var(--fs-label);">{nm}</div>

              <div class="mt-2 grid grid-cols-3 gap-2">
                <div class="bg-zinc-100 rounded-xl p-2">
                  <div class="text-zinc-500" style="font-size: var(--fs-sub); line-height: 1;">Contratos</div>
                  <div class="font-extrabold text-zinc-900 tabular-nums" style="font-size: var(--fs-label);">{contratos}</div>
                </div>

                <div class="bg-zinc-100 rounded-xl p-2">
                  <div class="text-zinc-500" style="font-size: var(--fs-sub); line-height: 1;">Fat Assinado</div>
                  <div class="font-extrabold text-zinc-900 tabular-nums truncate" style="font-size: var(--fs-label);">{fat_a}</div>
                </div>

                <div class="bg-zinc-100 rounded-xl p-2">
                  <div class="text-zinc-500" style="font-size: var(--fs-sub); line-height: 1;">Fat Pago</div>
                  <div class="font-extrabold text-zinc-900 tabular-nums truncate" style="font-size: var(--fs-label);">{fat_p}</div>
                </div>
              </div>
            </div>
          </div>
        ''')

    return f'''
    <div class="bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full" style="padding: var(--pad);">
      <div class="font-extrabold text-zinc-900" style="font-size: var(--fs-title);">{title}</div>
      <div class="mt-4 space-y-4">
        {''.join(body)}
      </div>
    </div>
    '''
