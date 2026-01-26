from ui.gauge import gauge_svg


def _pct_br(x: float) -> str:
    """55,5 (pt-BR)"""
    return f"{x:.1f}".replace(".", ",")


def kpi_card_html(
    title: str,
    percent_float: float,
    subtitle: str,
    left_label: str,
    left_value: str,
    left_badge: str,
    mid_label: str,
    mid_value: str,
    right_pill: str,
) -> str:
    # Gauge no estilo da referência do prototipo — semi-arco com pílulas.
    svg = gauge_svg(percent_float)
    right_pill_html = right_pill.replace("\n", "<br/>")
    pct_txt = _pct_br(float(percent_float or 0.0))

    return f"""
    <div class="bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full overflow-hidden flex flex-col" style="padding: var(--pad);">
      <div class="font-extrabold text-zinc-900" style="font-size: var(--fs-title); line-height: 1.1;">
        {title}
      </div>

      <div class="relative mt-2 flex-1 flex justify-center items-center" style="min-height: var(--gauge-min-h);">
        {svg}
        <div class="absolute inset-0 flex flex-col items-center justify-center text-center"
             style="transform: translateY(var(--gauge-text-shift));">
          <div class="font-extrabold text-zinc-900 tabular-nums" style="font-size: var(--fs-center); line-height: 1;">
            {pct_txt}%
          </div>
          <div class="text-zinc-500" style="font-size: var(--fs-sub); margin-top: 6px; line-height: 1.1;">
            {subtitle}
          </div>
        </div>
      </div>

<div class="mt-2 grid grid-cols-2" style="gap: var(--gap);">
        <div class="bg-zinc-100 rounded-2xl flex flex-col" style="padding: var(--box-pad); min-height: var(--pill-min-h);">
          <div class="flex items-start justify-between gap-2">
            <div class="text-zinc-500 leading-tight min-w-0" style="font-size: var(--fs-label);">
              {left_label}
            </div>
          </div>
          <div class="mt-auto font-extrabold text-zinc-900 tabular-nums whitespace-nowrap overflow-hidden text-ellipsis"
               style="font-size: var(--fs-kpi); line-height: 1.1; padding-top: 8px;">
            {left_value}
          </div>
        </div>
        <div class="bg-zinc-100 rounded-2xl flex flex-col" style="padding: var(--box-pad); min-height: var(--pill-min-h);">
          <div class="text-zinc-500 leading-tight" style="font-size: var(--fs-label);">
            {mid_label}
          </div>
          <div class="mt-auto font-extrabold text-zinc-900 tabular-nums whitespace-nowrap overflow-hidden text-ellipsis"
               style="font-size: var(--fs-kpi); line-height: 1.1; padding-top: 8px;">
            {mid_value}
          </div>
        </div>
      </div>
    </div>
    """
