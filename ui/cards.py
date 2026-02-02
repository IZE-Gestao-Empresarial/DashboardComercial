from ui.gauge import gauge_svg
import re


def _pct_br(x: float) -> str:
    """55,5 (pt-BR)"""
    return f"{x:.1f}".replace(".", ",")


def kpi_card_html(
    title: str,
    percent_float: float,
    subtitle: str,
    left_label: str,
    left_value: str,
    left_badge: str,   # badge do box ESQUERDO
    mid_label: str,
    mid_value: str,
    right_pill: str,   # badge do box DIREITO
) -> str:
    svg = gauge_svg(percent_float)
    pct_txt = _pct_br(float(percent_float or 0.0))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _parse_first_number(raw: str):
        """
        Extrai o primeiro número (com sinal) de uma string e retorna:
        (num_float, tail_text)

        Ex:
        "-3,5%"       -> (-3.5, "")
        "-2 reuniões" -> (-2.0, "reuniões")
        """
        if not raw:
            return None, ""

        s = str(raw).strip()
        m = re.search(r"([+-]?\d+(?:[.,]\d+)?)\s*(%?)", s)

        if not m:
            return None, s

        num_str = m.group(1)
        num = float(num_str.replace(",", "."))
        tail = (s[m.end():] or "").strip()

        return num, tail

    def _format_signed(num: float, raw: str, tail: str, emoji_on_zero: bool):
        """
        Formata como:
        - negativo: "-N"
        - zero: "0 ✅" (se emoji_on_zero)
        - positivo: "+N"

        Mantém % e sufixos (ex: "reuniões").
        """
        has_percent = "%" in (raw or "")

        if abs(num - round(num)) < 1e-9:
            mag = str(int(abs(round(num))))
        else:
            mag = _pct_br(abs(num))

        if abs(num) < 1e-9:
            txt = "0"
        elif num > 0:
            txt = f"+{mag}"
        else:
            txt = f"-{mag}"

        if has_percent:
            txt = f"{txt}%"

        if tail:
            txt = f"{txt} {tail}"

        if abs(num) < 1e-9 and emoji_on_zero:
            txt = f"{txt} ✅"

        return txt

    def _badge_html(raw_value: str, emoji_on_zero: bool):
        """
        Regras de cor:
        - num < 0  -> preto
        - num >= 0 -> laranja
        """
        raw_value = (raw_value or "").strip()
        if not raw_value:
            return ""

        num, tail = _parse_first_number(raw_value)

        if num is None:
            bg = "#F4561F"
            txt = raw_value.replace("\n", "<br/>")
        else:
            bg = "#111827" if num < 0 else "#F4561F"
            txt = _format_signed(num, raw_value, tail, emoji_on_zero)

        return f"""
        <div class="shrink-0" style="transform: translateY(var(--badge-y, 0px));">
          <div
            class="inline-flex items-center justify-center rounded-full font-semibold tabular-nums whitespace-nowrap"
            style="
              background:{bg};
              color:#fff;
              padding: 2px 12px;
              gap: 6px;
              font-size: var(--fs-badge, 12px);
              line-height: 1;
            "
          >
            <span style="font-size:9px">{txt}</span>
          </div>
        </div>
        """


    # ------------------------------------------------------------------
    # Pré-processamento
    # ------------------------------------------------------------------

    left_badge_html = _badge_html(left_badge, emoji_on_zero=True)
    right_badge_html = _badge_html(right_pill, emoji_on_zero=False)

    left_label_html = (left_label or "").replace("\n", "<br/>")
    mid_label_html = (mid_label or "").replace("\n", "<br/>")

    # ------------------------------------------------------------------
    # HTML
    # ------------------------------------------------------------------

    return f"""
    <div class="bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full flex flex-col"
         style="padding: var(--pad); border-radius: 12px;">

      <div class="kpi-title text-zinc-900"
      style="font-size: var(--fs-title); line-height: 1.1;">
      {title}
    </div>


      <div class="relative mt-2 flex-1 flex justify-center items-center"
           style="min-height: var(--gauge-min-h);">
        {svg}

        <div class="absolute inset-0 flex flex-col items-center justify-center text-center"
             style="transform: translateY(var(--gauge-text-shift));">
          <div class="font-bold text-zinc-900 tabular-nums"
               style="font-size: var(--fs-center); line-height: 1;">
            {pct_txt}%
          </div>

          <div class="font-bold text-zinc-500"
               style="font-size: var(--fs-sub); margin-top: 6px; line-height: 1.1;">
            {subtitle}
          </div>
        </div>
      </div>

      <div class="mt-2 grid grid-cols-2" style="gap: var(--gap);">

          <!-- BOX ESQUERDO -->
          <div class="bg-[#F6F6F6] rounded-2xl flex flex-col"
          style="padding: calc(var(--box-pad) + var(--box-pad-extra)); min-height: var(--pill-min-h);">

          <div class="flex items-center justify-between gap-2">
            <div
              class="text-zinc-600 leading-snug text-left"
              style="font-size: calc(var(--fs-label) - 1px);"
            >
              {left_label_html}
            </div>

            {left_badge_html}
          </div>

          <div class="mt-1 font-extrabold text-zinc-900 tabular-nums"
               style="font-size: var(--fs-kpi); line-height: 1;">
            {left_value}
          </div>
        </div>

        <!-- BOX DIREITO -->
        <div class="bg-[#F6F6F6] rounded-2xl flex flex-col"
        style="padding: calc(var(--box-pad) + var(--box-pad-extra)); min-height: var(--pill-min-h);">

          <div class="flex items-center justify-between gap-2">
          <div
            class="text-zinc-600 leading-snug text-left"
            style="font-size: calc(var(--fs-label) - 1px);"
          >
            {mid_label_html}
          </div>


            {right_badge_html}
          </div>

          <div class="mt-1 font-extrabold text-zinc-900 tabular-nums"
               style="font-size: var(--fs-kpi); line-height: 1;">
            {mid_value}
          </div>
        </div>

      </div>
    </div>
    """
