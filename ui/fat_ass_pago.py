from __future__ import annotations

import html

from core.formatters import fmt_money
from ui.ranklist import fmt_percent_br


def _clean_money_txt(s: str) -> str:
    """Remove decimais ,00/.00 quando vierem do fmt_money (para ficar igual ao protótipo)."""
    s = (s or "").strip()
    if s.endswith(",00") or s.endswith(".00"):
        return s[:-3]
    return s


def faturamento_ass_pago_card_html(
    *,
    title: str = "Faturamento Assinado x Pago",
    total_assinado: float | int | None,
    total_pago: float | int | None,
    assinado_series: list[float] | None = None,
    pago_series: list[float] | None = None,
) -> str:
    """Card 'Faturamento Assinado x Pago' no visual do protótipo (2 barras sobrepostas + pills).

    Mantém `*_series` por compatibilidade (não usado no layout).
    """

    # Normaliza o título padrão do dashboard
    t = (title or "").strip()
    if (not t) or (t.lower().replace("  ", " ") in {"faturamento ass x pago", "faturamento assinado x pago"}):
        title = "Faturamento Assinado x Pago"

    ass = float(total_assinado or 0.0)
    pago = float(total_pago or 0.0)

    ratio = (pago / ass * 100.0) if ass > 0 else 0.0
    ratio = max(0.0, min(100.0, ratio))

    # Valores no protótipo aparecem sem o prefixo 'R$'
    ass_txt = _clean_money_txt(fmt_money(ass))
    pago_txt = _clean_money_txt(fmt_money(pago))

    # No protótipo o % é inteiro (ex.: 80%)
    ratio_int = int(round(ratio))

    # Também deixamos o % pt-BR disponível (caso queira 1 casa no futuro)
    _ = fmt_percent_br(ratio)  # noqa: F841

    return f"""
    <div class=\"fatap-card\" role=\"group\" aria-label=\"{html.escape(title)}\">
      <div class=\"fatap-stage\">
        <div class=\"fatap-bars\" style=\"--fatap-r:{ratio:.3f};\" role=\"img\" aria-label=\"Comparação: faturamento pago sobre faturamento assinado\">
          <div class=\"fatap-bar fatap-bar-ass\" aria-hidden=\"true\"></div>

          <div class=\"fatap-bar fatap-bar-pago\" aria-hidden=\"true\"></div>

          <div class=\"fatap-pill fatap-pill-ass\" title=\"Faturamento Assinado\">{html.escape(ass_txt)}</div>
          <div class=\"fatap-pill fatap-pill-pago\" title=\"Faturamento Pago\">{html.escape(pago_txt)}</div>

          <div class=\"fatap-ratio\" aria-label=\"{ratio_int}%\">{ratio_int}%</div>
        </div>
      </div>

      <div class=\"fatap-title\">{html.escape(title)}</div>
    </div>
    """
