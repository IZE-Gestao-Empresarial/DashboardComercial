from __future__ import annotations

import html

from core.formatters import fmt_money
from ui.ranklist import fmt_percent_br


def faturamento_ass_pago_card_html(
    *,
    title: str = "Faturamento ass x pago",
    total_assinado: float | int | None,
    total_pago: float | int | None,
    assinado_series: list[float] | None = None,
    pago_series: list[float] | None = None,
) -> str:
    """Card no visual do PROTÓTIPO 3 (barra horizontal + legenda).

    `*_series` ficam aceitos para compatibilidade, mas o layout do protótipo usa
    somente os totais.
    """
    ass = float(total_assinado or 0.0)
    pago = float(total_pago or 0.0)

    ratio = (pago / ass * 100.0) if ass > 0 else 0.0
    ratio = max(0.0, min(100.0, ratio))

    ass_txt = fmt_money(ass)
    pago_txt = fmt_money(pago)

    # no protótipo: 'Pago / Assinado'
    ratio_txt = fmt_percent_br(ratio) if ass > 0 else "0,0%"

    return f"""
    <div class="bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full flex flex-col overflow-hidden" style="padding: var(--pad);">
      <div class="font-extrabold text-zinc-900" style="font-size: var(--fs-title); line-height:1.1;">{html.escape(title)}</div>

      <div class="fa-panel">
        <div class="fa-bar-head">
          <div class="fa-head-col">
            <div class="fa-head-label">Assinado</div>
          </div>
          <div class="fa-head-col fa-right">
            <div class="fa-head-val">R$ {html.escape(ass_txt)}</div>
          </div>
        </div>

        <div class="fa-bar-wrap" role="img" aria-label="Progresso faturamento pago sobre assinado">
          <div class="fa-bar-bg">
            <div class="fa-bar-fill" style="width:{ratio:.3f}%"></div>
          </div>
        </div>

        <div class="fa-bar-foot">
          <div class="fa-foot-left">
            <span class="fa-dot fa-dot-pago"></span><span>Faturamento Pago</span>
          </div>
          <div class="fa-foot-mid">
            <span class="fa-dot fa-dot-ass"></span><span>Faturamento Assinado</span>
          </div>
          <div class="fa-foot-right">Pago / Assinado: {html.escape(ratio_txt)}</div>
        </div>

        <div class="fa-paid-val">R$ {html.escape(pago_txt)}</div>
      </div>
    </div>
    """
