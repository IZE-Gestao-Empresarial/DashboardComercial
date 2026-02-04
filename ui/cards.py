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
        if raw is None:
            return None, ""

        s = str(raw).strip()
        if not s:
            return None, ""

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

        # ✅ para percent, sempre mostra 1 casa decimal (ex.: 5,0%)
        if has_percent:
            mag = _pct_br(abs(num))
        else:
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
        - num < 0  -> preto (#111827)
        - num >= 0 -> laranja (#F05914)
        
        ✅ Badge compacto ao lado do label
        """
        raw_value = (str(raw_value) if raw_value is not None else "").strip()
        if not raw_value:
            return ""

        num, tail = _parse_first_number(raw_value)

        if num is None:
            bg = "#F05914"
            txt = raw_value.replace("\n", "<br/>")
        else:
            bg = "#111827" if num < 0 else "#F05914"
            txt = _format_signed(num, raw_value, tail, emoji_on_zero)

        return f"""
        <div class="inline-flex items-center justify-center rounded-full font-bold tabular-nums whitespace-nowrap flex-shrink-0"
             style="
               background: {bg};
               color: #fff;
               padding: 2px 8px;
               font-size: calc(var(--fs-label) * 0.65);
               line-height: 1.1;
             ">
          {txt}
        </div>
        """

    def _coerce_percent_if_numeric(v) -> str:
        """
        ✅ Para o badge da esquerda: se vier número (float/int/string numérica) sem '%',
        adiciona '%' para renderizar como porcentagem.
        """
        if v is None:
            return ""
        s = str(v).strip()
        if not s:
            return ""
        if "%" in s:
            return s
        # parece número puro? então vira percent
        if re.fullmatch(r"[+-]?\d+(?:[.,]\d+)?", s):
            return s + "%"
        return s

    # ------------------------------------------------------------------
    # Pré-processamento
    # ------------------------------------------------------------------

    # ✅ ESQUERDA: força percent quando for numérico
    left_badge_html = _badge_html(_coerce_percent_if_numeric(left_badge), emoji_on_zero=True)

    # ✅ DIREITA: mantém comportamento atual (não força %)
    right_badge_html = _badge_html(right_pill, emoji_on_zero=False)

    left_label_html = (left_label or "").replace("\n", "<br/>")
    mid_label_html = (mid_label or "").replace("\n", "<br/>")

    # ------------------------------------------------------------------
    # HTML
    # ------------------------------------------------------------------

    return f"""
    <div class="kpi-card bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full flex flex-col"
         style="padding: var(--pad); border-radius: 12px;">

      <div class="kpi-title text-zinc-900"
           style="font-size: var(--fs-title); line-height: 1.1;">
        {title}
      </div>

      <div class="kpi-gauge relative mt-2 flex-1 flex justify-center items-center"
           style="
             /* ✅ escala segura (evita valores absurdos tipo 0.45) */
             --kpi-gauge-scale-safe: clamp(0.78, var(--kpi-gauge-scale, 0.92), 1);
             --gauge-scale: var(--kpi-gauge-scale-safe);

             /* ✅ o bloco também encolhe junto (pra não empurrar os subcards) */
             min-height: calc(var(--gauge-min-h) * var(--kpi-gauge-scale-safe));

             /* ✅ respiro lateral/topo: evita encostar na borda do card */
             padding-top: calc(6px * var(--ui-scale));
             padding-left: calc(10px * var(--ui-scale));
             padding-right: calc(10px * var(--ui-scale));
             box-sizing: border-box;
           ">

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
        <div class="kpi-box bg-[#F6F6F6] rounded-2xl flex flex-col"
             style="padding: calc(var(--box-pad) + var(--box-pad-extra)); min-height: var(--pill-min-h);">

          <!-- Label + Badge (mesma linha) -->
          <div class="flex items-center justify-between gap-2">
            <div class="text-zinc-600 leading-snug text-left"
                 style="font-size: calc(var(--fs-label) - 1px);">
              {left_label_html}
            </div>
            {left_badge_html}
          </div>

          <!-- Valor grande -->
          <div class="mt-1 font-extrabold text-zinc-900 tabular-nums"
               style="font-size: var(--fs-kpi); line-height: 1;">
            {left_value}
          </div>
        </div>

        <!-- BOX DIREITO -->
        <div class="kpi-box bg-[#F6F6F6] rounded-2xl flex flex-col"
             style="padding: calc(var(--box-pad) + var(--box-pad-extra)); min-height: var(--pill-min-h);">

          <!-- Label + Badge (mesma linha) -->
          <div class="flex items-center justify-between gap-2">
            <div class="text-zinc-600 leading-snug text-left"
                 style="font-size: calc(var(--fs-label) - 1px);">
              {mid_label_html}
            </div>
            {right_badge_html}
          </div>

          <!-- Valor grande -->
          <div class="mt-1 font-extrabold text-zinc-900 tabular-nums"
               style="font-size: var(--fs-kpi); line-height: 1;">
            {mid_value}
          </div>
        </div>

      </div>
    </div>
    """