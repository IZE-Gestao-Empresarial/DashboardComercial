from __future__ import annotations

from core.formatters import fmt_int
from ui.ranklist import fmt_percent_br


def leads_conversion_card_html(
    *,
    leads_total: float | int | None,
    taxa_conversao: float | None,
    title: str = "Leads | Taxa de Conversão (Geral)",
) -> str:
    """Card compacto com 2 KPIs (leads e taxa de conversão geral)."""

    leads_txt = fmt_int(leads_total)
    taxa_txt = fmt_percent_br(taxa_conversao) if taxa_conversao is not None else "-"

    return f'''
    <div class="bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full flex flex-col" style="padding: var(--pad);">
      <div class="text-center font-extrabold" style="font-size: var(--fs-title);">{title}</div>

      <div class="flex-1 min-h-0 flex items-center justify-center" style="padding-top: calc(var(--gap) * 0.6);">
        <div class="grid grid-cols-2" style="gap: var(--gap); width: 100%;">
          <div class="rounded-2xl bg-zinc-50 border border-zinc-200 flex flex-col items-center justify-center" style="padding: var(--box-pad); min-height: var(--pill-min-h);">
            <div class="text-zinc-500 font-semibold" style="font-size: var(--fs-label);">Leads</div>
            <div class="text-zinc-900 font-extrabold" style="font-size: var(--fs-kpi); line-height: 1;">{leads_txt}</div>
          </div>

          <div class="rounded-2xl bg-zinc-50 border border-zinc-200 flex flex-col items-center justify-center" style="padding: var(--box-pad); min-height: var(--pill-min-h);">
            <div class="text-zinc-500 font-semibold" style="font-size: var(--fs-label);">Conversão</div>
            <div class="text-zinc-900 font-extrabold" style="font-size: var(--fs-kpi); line-height: 1;">{taxa_txt}</div>
          </div>
        </div>
      </div>
    </div>
    '''
