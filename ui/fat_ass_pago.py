from __future__ import annotations

from core.formatters import fmt_money
from ui.ranklist import fmt_percent_br


def _spark_area_line_svg(
    *,
    area_values: list[float],
    line_values: list[float],
    height: int = 52,
) -> str:
    """Mini-gráfico SVG (área + linha) sem dependências JS.

    - Área: faturamento assinado
    - Linha: faturamento pago

    Espera listas com o MESMO tamanho.
    """
    if not area_values or not line_values:
        return ""

    n = min(len(area_values), len(line_values))
    if n < 2:
        return ""

    a = area_values[:n]
    b = line_values[:n]

    # normalização
    max_v = max([0.0] + [float(x or 0.0) for x in a] + [float(x or 0.0) for x in b])
    if max_v <= 0:
        max_v = 1.0

    vb_w, vb_h = 100.0, 40.0
    pad_t, pad_b = 4.0, 6.0
    plot_h = vb_h - pad_t - pad_b

    def xy(i: int, val: float) -> tuple[float, float]:
        x = (i / (n - 1)) * vb_w
        y = pad_t + (1.0 - (float(val or 0.0) / max_v)) * plot_h
        return x, y

    area_pts = [xy(i, a[i]) for i in range(n)]
    line_pts = [xy(i, b[i]) for i in range(n)]

    area_path = "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in area_pts)
    area_path += f" L {vb_w:.2f} {vb_h - pad_b:.2f} L 0.00 {vb_h - pad_b:.2f} Z"

    line_poly = " ".join(f"{x:.2f},{y:.2f}" for x, y in line_pts)

    # cores alinhadas ao padrão (laranja + neutros)
    fill = "rgba(235,94,40,0.22)"  # #EB5E28 com alpha
    stroke = "rgb(235,94,40)"
    grid = "rgba(0,0,0,0.08)"

    return f'''
      <svg viewBox="0 0 {vb_w:g} {vb_h:g}" width="100%" height="{height}" preserveAspectRatio="none" aria-hidden="true">
        <line x1="0" y1="{vb_h - pad_b:g}" x2="{vb_w:g}" y2="{vb_h - pad_b:g}" stroke="{grid}" stroke-width="0.8" />
        <line x1="0" y1="{pad_t:g}" x2="{vb_w:g}" y2="{pad_t:g}" stroke="{grid}" stroke-width="0.8" />

        <path d="{area_path}" fill="{fill}" />
        <polyline points="{line_poly}" fill="none" stroke="{stroke}" stroke-width="1.8" vector-effect="non-scaling-stroke" />

        <circle cx="{line_pts[-1][0]:.2f}" cy="{line_pts[-1][1]:.2f}" r="2.2" fill="{stroke}" />
      </svg>
    '''


def faturamento_ass_pago_card_html(
    *,
    total_assinado: float | None,
    total_pago: float | None,
    assinado_series: list[float] | None = None,
    pago_series: list[float] | None = None,
    title: str = "Faturamento ass x pago",
) -> str:
    """Card comparando faturamento assinado vs pago.

    Se houver série histórica, mostra um mini gráfico (área + linha).
    Caso contrário, exibe apenas os totais e a proporção.
    """

    ass_txt = fmt_money(total_assinado)
    pago_txt = fmt_money(total_pago)

    # Proporção pago/assinado
    ratio = None
    try:
        if total_assinado and float(total_assinado) != 0:
            ratio = float(total_pago or 0) / float(total_assinado)
    except Exception:
        ratio = None

    ratio_txt = fmt_percent_br(ratio) if ratio is not None else "-"

    spark_html = ""
    if assinado_series and pago_series and len(assinado_series) >= 2 and len(assinado_series) == len(pago_series):
        spark_html = _spark_area_line_svg(area_values=assinado_series, line_values=pago_series)

    return f'''
    <div class="bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full flex flex-col" style="padding: var(--pad);">
      <div class="text-center font-extrabold" style="font-size: var(--fs-title);">{title}</div>

      <div class="grid grid-cols-2" style="gap: var(--gap); padding-top: calc(var(--gap) * 0.55);">
        <div class="rounded-2xl bg-zinc-50 border border-zinc-200 flex flex-col items-center justify-center" style="padding: var(--box-pad); min-height: var(--pill-min-h);">
          <div class="text-zinc-500 font-semibold" style="font-size: var(--fs-label);">Assinado</div>
          <div class="text-zinc-900 font-extrabold" style="font-size: var(--fs-kpi); line-height: 1;">R$ {ass_txt}</div>
        </div>

        <div class="rounded-2xl bg-zinc-50 border border-zinc-200 flex flex-col items-center justify-center" style="padding: var(--box-pad); min-height: var(--pill-min-h);">
          <div class="text-zinc-500 font-semibold" style="font-size: var(--fs-label);">Pago</div>
          <div class="text-zinc-900 font-extrabold" style="font-size: var(--fs-kpi); line-height: 1;">R$ {pago_txt}</div>
        </div>
      </div>

      <div class="flex-1 min-h-0 flex flex-col items-center justify-end" style="padding-top: calc(var(--gap) * 0.35);">
        <div class="w-full" style="opacity: 0.92;">{spark_html}</div>

        <div class="text-zinc-500 font-semibold" style="font-size: var(--fs-sub); padding-top: 6px;">
          Pago / Assinado: <span class="text-zinc-800">{ratio_txt}</span>
        </div>
      </div>
    </div>
    '''
