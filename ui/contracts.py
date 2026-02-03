from __future__ import annotations

import html

from core.people import pretty_name
from core.formatters import fmt_int, fmt_money
from ui.avatars import photo_src


def _metric_row(icon: str, label: str, value_html: str) -> str:
    return f'''
      <div class="flex items-center justify-between py-2" style="gap: 12px;">
        <div class="flex items-center gap-3 min-w-0">
          <div class="flex items-center justify-center rounded-lg bg-zinc-100" style="width: 34px; height: 34px; font-size: 18px;">
            {icon}
          </div>
          <div class="font-semibold text-zinc-900 truncate" style="font-size: var(--podium-row-fs);">
            {label}
          </div>
        </div>
        <div class="font-extrabold text-zinc-900 tabular-nums whitespace-nowrap" style="font-size: var(--podium-val-fs);">
          {value_html}
        </div>
      </div>
    '''


def _person_podium_card(name_upper: str, rank: int, contratos: float | None, fat_assinado: float | None, fat_pago: float | None) -> str:
    name_u = (name_upper or "").strip().upper()
    name_pretty = html.escape(pretty_name(name_u))

    # rank text: 1º / 2º
    rank_text = f"{rank}º"

    src = photo_src(name_u)
    if src:
        photo = f'<img src="{html.escape(src)}" alt="{name_pretty}" class="w-full h-full object-cover" />'
    else:
        # fallback simples: iniciais / fundo
        initials = "".join([p[0] for p in name_u.split()[:2] if p])[:2] or "?"
        photo = f'<div class="w-full h-full flex items-center justify-center bg-zinc-900 text-white font-extrabold" style="font-size: 44px;">{html.escape(initials)}</div>'

    contratos_v = fmt_int(contratos)
    fa_v = fmt_money(fat_assinado)
    fp_v = fmt_money(fat_pago)

    return f'''
    <div class="flex flex-col items-center justify-end" style="min-width: 0;">
      <div class="relative" style="width: var(--podium-photo); height: var(--podium-photo);">
        <div class="rounded-full overflow-hidden"
             style="width: 100%; height: 100%; border: var(--podium-ring) solid #F05914; box-shadow: 0 18px 40px rgba(0,0,0,0.18);">
          {photo}
        </div>
      </div>

      <div class="mt-3 w-full" style="max-width: var(--podium-card-w);">
        <div class="rounded-2xl overflow-hidden" style="box-shadow: 0 18px 40px rgba(0,0,0,0.14); border: 2px solid rgba(240,89,20,0.35);">
          <div class="text-white font-extrabold text-center"
               style="background: linear-gradient(180deg, #F05914 0%, #D94E12 100%); padding: 12px 12px; font-size: var(--podium-head-fs);">
            Contratos Assinados
          </div>

          <div class="bg-white" style="padding: 10px 12px;">
            <div class="text-center font-extrabold text-zinc-900" style="font-size: var(--podium-name-fs); margin-bottom: 6px;">
              {name_pretty}
            </div>

            <div class="h-px bg-zinc-200"></div>
            {_metric_row("📄", "Contratos Assinados", contratos_v)}
            <div class="h-px bg-zinc-200"></div>
            {_metric_row("🤝", "Fat. Assinado", fa_v)}
            <div class="h-px bg-zinc-200"></div>
            {_metric_row("💰", "Fat. Pago", fp_v)}
          </div>
        </div>
      </div>
    </div>
    '''


def contratos_faturamento_por_pessoa_card_html(title: str, rows: list[dict]) -> str:
    """Tile no estilo 'podium' para NURY e GUILHERME."""
    if not rows:
        return f'''
        <div class="bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full flex items-center justify-center">
          <div class="text-zinc-500 font-semibold">Sem dados de {html.escape(title)}</div>
        </div>
        '''

    rows2 = rows[:2]
    cards = []
    for i, r in enumerate(rows2, start=1):
        cards.append(
            _person_podium_card(
                name_upper=str(r.get("name") or ""),
                rank=i,
                contratos=r.get("contratos"),
                fat_assinado=r.get("fat_assinado"),
                fat_pago=r.get("fat_pago"),
            )
        )

    return f'''
    <div class="bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full" style="padding: var(--pad); overflow: hidden;">
      <div class="font-extrabold text-zinc-900" style="font-size: var(--fs-title);">{html.escape(title)}</div>

      <div class="mt-4 grid grid-cols-2" style="gap: var(--gap); align-items: end;">
        {"".join(cards)}
      </div>
    </div>
    '''
