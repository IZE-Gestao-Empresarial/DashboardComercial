# ui/cards.py
from ui.gauge import gauge_svg


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
    svg = gauge_svg(percent_float, segments=12)
    right_pill_html = right_pill.replace("\n", "<br/>")

    return f"""
    <div class="bg-white rounded-3xl shadow-sm border border-zinc-100" style="padding: var(--pad);">
      <div class="font-extrabold text-zinc-900" style="font-size: var(--fs-title); line-height: 1.1;">
        {title}
      </div>

      <div class="relative mt-3 flex justify-center">
        {svg}
        <div class="absolute inset-0 flex flex-col items-center justify-center text-center"
             style="transform: translateY(12px);">
          <div class="font-extrabold text-zinc-900 tabular-nums"
               style="font-size: var(--fs-center); line-height: 1;">
            {percent_float:.1f}%
          </div>
          <div class="text-zinc-500"
               style="font-size: var(--fs-sub); margin-top: 6px; line-height: 1.1;">
            {subtitle}
          </div>
        </div>
      </div>

      <div class="mt-3 grid grid-cols-3" style="gap: var(--gap);">
        <div class="relative bg-zinc-100 rounded-2xl" style="padding: var(--box-pad);">
          <div class="text-zinc-500 leading-4" style="font-size: var(--fs-label);">
            {left_label}
          </div>

          <div class="font-extrabold text-zinc-900 tabular-nums whitespace-nowrap overflow-hidden text-ellipsis"
               style="font-size: var(--fs-kpi); line-height: 1.15; margin-top: 8px;">
            {left_value}
          </div>

          <span class="absolute bg-[#F05914] text-white rounded-full font-semibold"
                style="top: 10px; right: 10px; font-size: var(--fs-badge); padding: 4px 8px; line-height: 1;">
            {left_badge}
          </span>
        </div>

        <div class="bg-zinc-100 rounded-2xl" style="padding: var(--box-pad);">
          <div class="text-zinc-500 leading-4" style="font-size: var(--fs-label);">
            {mid_label}
          </div>
          <div class="font-extrabold text-zinc-900 tabular-nums whitespace-nowrap overflow-hidden text-ellipsis"
               style="font-size: var(--fs-kpi); line-height: 1.15; margin-top: 8px;">
            {mid_value}
          </div>
        </div>

        <div class="bg-[#F05914] text-white rounded-2xl flex items-center justify-center text-center font-extrabold"
             style="padding: var(--box-pad); font-size: var(--fs-pill); line-height: 1.1; min-height: var(--pill-min-h);">
          {right_pill_html}
        </div>
      </div>
    </div>
    """
