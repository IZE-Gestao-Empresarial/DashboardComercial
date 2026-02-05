from ui.gauge import gauge_svg
import re


def _pct_br(x: float) -> str:
    """
    Percentual pt-BR com 1 casa, mas remove ",0" quando zerado.
    Ex:
      6.0  -> "6"
      6.5  -> "6,5"
      100.0 -> "100"
    """
    s = f"{float(x or 0.0):.1f}".replace(".", ",")
    if s.endswith(",0"):
        s = s[:-2]
    return s


def kpi_card_html(
    title: str,
    percent_float: float,
    subtitle: str,
    left_label: str,
    left_value: str,
    left_badge: str,   # badge do box ESQUERDO (pode virar %)
    mid_label: str,
    mid_value: str,
    right_pill: str,   # badge do box DIREITO (sem seta)
) -> str:
    svg = gauge_svg(percent_float)
    pct_txt = _pct_br(float(percent_float or 0.0))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _fmt_int_br(n: int) -> str:
        """Inteiro pt-BR com separador de milhar '.'"""
        try:
            return f"{int(n):,}".replace(",", ".")
        except Exception:
            return str(n)

    def _fmt_num_br(v: float) -> str:
        """
        Número pt-BR com separador de milhar '.' e decimal ',' (até 1 casa).
        Remove ',0' quando zerado.
        """
        try:
            s = f"{float(v):,.1f}"
            # US -> pt-BR (thousands ',' -> '.', decimal '.' -> ',')
            s = s.replace(",", "X").replace(".", ",").replace("X", ".")
            if s.endswith(",0"):
                s = s[:-2]
            return s
        except Exception:
            return str(v)

    def _parse_first_number(raw: str):
        """
        Extrai o primeiro número (com sinal) de uma string e retorna:
        (num_float, tail_text)
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

    def _format_signed(num: float, raw: str, tail: str):
        """
        Formata como:
        - negativo: "-N"
        - zero: "0"
        - positivo: "+N"
        Mantém % e sufixos.
        (Usado no badge ESQUERDO, que é variação/delta.)
        """
        has_percent = "%" in (raw or "")

        if has_percent:
            mag = _pct_br(abs(num))  # remove ",0" quando for o caso
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

        return txt

    def _format_right_badge(num: float, raw: str, tail: str) -> str:
        """
        Badge DIREITO (valor absoluto):
        - NÃO adiciona '+' automaticamente
        - Formata milhares com '.' (pt-BR): 411300 -> 411.300
        - Mantém sinal apenas se vier no raw (+...) ou se for negativo
        - Mantém % se vier %
        """
        raw_s = (raw or "").strip()
        has_percent = "%" in raw_s

        explicit_plus = bool(re.match(r"^\s*\+", raw_s))
        explicit_minus = bool(re.match(r"^\s*-", raw_s)) or (num < 0)

        if has_percent:
            mag = _pct_br(abs(num))
            if explicit_minus:
                txt = f"-{mag}%"
            elif explicit_plus:
                txt = f"+{mag}%"
            else:
                txt = f"{mag}%"
        else:
            if abs(num - round(num)) < 1e-9:
                mag = _fmt_int_br(int(round(abs(num))))
            else:
                mag = _fmt_num_br(abs(num))

            if explicit_minus:
                txt = f"-{mag}"
            elif explicit_plus:
                txt = f"+{mag}"
            else:
                txt = mag

        if tail:
            txt = f"{txt} {tail}"

        return txt

    def _coerce_percent_if_numeric(v) -> str:
        """
        Para o badge da esquerda: se vier número sem '%', adiciona '%'.
        """
        if v is None:
            return ""
        s = str(v).strip()
        if not s:
            return ""
        if "%" in s:
            return s
        if re.fullmatch(r"[+-]?\d+(?:[.,]\d+)?", s):
            return s + "%"
        return s

    def _label_html(v: str) -> str:
        """
        Converte label em HTML respeitando quebra:
        - Se vier com <br> ou \n, respeita.
        - Se NÃO vier, força quebra após ' de '.
        """
        s = (v or "").strip()
        if not s:
            return ""

        if re.search(r"<br\s*/?>", s, flags=re.I):
            return s

        if "\n" in s:
            return s.replace("\n", "<br/>")

        s = s.replace(" de ", " de<br/> ", 1)
        return s

    def _is_long_percent(raw: str) -> bool:
        """
        Percent >= 100% (3+ dígitos).
        """
        if not raw or "%" not in raw:
            return False
        num, _ = _parse_first_number(raw)
        return (num is not None) and (abs(num) >= 100)

    def _is_long_number_for_badge(raw: str) -> bool:
        """
        Números muito grandes (sem %) que costumam estourar o badge.
        Regra prática: >= 6 dígitos (ex.: 100000) ou string numérica longa.
        """
        if not raw:
            return False
        s = str(raw).strip()
        if not s or "%" in s:
            return False

        num, _ = _parse_first_number(s)
        if num is not None:
            return abs(num) >= 100000  # 6 dígitos

        digits = re.sub(r"\D", "", s)
        return len(digits) >= 6

    def _badge_scale_for_raw(raw: str) -> float:
        """
        Escala automática do badge (altura + fonte) conforme o conteúdo.
        Mantém default 1.00 e reduz em cenários "grandes".
        """
        s = (str(raw) if raw is not None else "").strip()
        if not s:
            return 1.0

        if _is_long_percent(s):
            return 0.90

        if _is_long_number_for_badge(s):
            return 0.92

        # fallback: se a string for muito comprida
        if len(s) >= 8:
            return 0.93

        return 1.0

    # ------------------------------------------------------------------
    # SETA (base já apontando pra DIREITA)
    # ------------------------------------------------------------------

    _ARROW_SVG_RIGHT = """
<svg width="21" height="21" viewBox="0 0 21 21" fill="none" xmlns="http://www.w3.org/2000/svg">
  <g transform="rotate(-45 10.5 10.5)">
    <path d="M4 4 L15.5 15.5" stroke="#FFFFFF" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M15.5 15.5 V6.2" stroke="#FFFFFF" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M15.5 15.5 H6.2" stroke="#FFFFFF" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
  </g>
</svg>
""".strip()

    def _arrow_html_for_percent(num: float | None, raw: str) -> str:
        """
        Só renderiza seta quando for porcentagem.
        """
        if "%" not in (raw or ""):
            return ""

        if num is None or abs(num) < 1e-9:
            deg = 0
        elif num > 0:
            deg = -45
        else:
            deg = 45

        return f"""
<span style="
  display:inline-flex;
  align-items:center;
  justify-content:center;
  flex: 0 0 auto;

  width:  calc(10px * var(--ui-scale, 1) * var(--kpi-badge-scale, var(--kpi-box-badge-scale, 1)));
  height: calc(10px * var(--ui-scale, 1) * var(--kpi-badge-scale, var(--kpi-box-badge-scale, 1)));

  margin-left: calc(2px * var(--ui-scale, 1));

  transform: translateY(var(--kpi-arrow-nudge-y, 0px)) rotate({deg}deg);
  transform-origin: center;
">
  {_ARROW_SVG_RIGHT}
</span>
""".strip()

    # ------------------------------------------------------------------
    # BADGES (separados)
    # ------------------------------------------------------------------

    def _left_badge_html(raw_value: str) -> str:
        raw_value = (str(raw_value) if raw_value is not None else "").strip()
        if not raw_value:
            return ""

        num, tail = _parse_first_number(raw_value)

        if num is None:
            bg = "#F4561F"
            txt = raw_value.replace("\n", "<br/>")
        else:
            bg = "#252422" if num < 0 else "#F4561F"
            txt = _format_signed(num, raw_value, tail)

        arrow_html = _arrow_html_for_percent(num, raw_value)

        # ✅ wrapper interno pra "descer" só o conteúdo (texto + seta),
        # sem mexer no pill
        return f"""
<div class="inline-flex items-center justify-center rounded-full tabular-nums whitespace-nowrap flex-shrink-0"
     style="
       background: {bg};
       color: #fff;

       height: calc(var(--kpi-badge-h, 14px) * var(--ui-scale, 1) * var(--kpi-badge-scale, var(--kpi-box-badge-scale, 1)));
       min-width: calc(var(--kpi-badge-min-w, 36px) * var(--ui-scale, 1) * var(--kpi-badge-scale, var(--kpi-box-badge-scale, 1)));
       padding: 0 calc(var(--kpi-badge-pad-x, 4px) * var(--ui-scale, 1) * var(--kpi-badge-scale, var(--kpi-box-badge-scale, 1)));

       font-size: calc(
         var(--fs-label) * 0.99
         * var(--kpi-left-badge-font-scale, 1)
         * var(--kpi-badge-scale, var(--kpi-box-badge-scale, 1))
       );
       font-weight: 400;
       line-height: 1;
       text-align: center;
     ">

  <span style="
    display:inline-flex;
    align-items:center;
    justify-content:center;
    transform: translateY(calc(var(--kpi-left-badge-content-nudge-y, 0) * 1px));
  ">
    <span style="line-height:1;">{txt}</span>
    {arrow_html}
  </span>
</div>
""".strip()

    def _right_badge_html(raw_value: str) -> str:
        raw_value = (str(raw_value) if raw_value is not None else "").strip()
        if not raw_value:
            return ""

        num, tail = _parse_first_number(raw_value)

        if num is None:
            bg = "#F4561F"
            txt = raw_value.replace("\n", "<br/>")
        else:
            bg = "#252422" if num < 0 else "#F4561F"
            # ✅ aqui: formato pt-BR com milhar '.' e sem '+' automático
            txt = _format_right_badge(num, raw_value, tail)

        return f"""
<div class="inline-flex items-center justify-center rounded-full tabular-nums whitespace-nowrap flex-shrink-0"
     style="
       background: {bg};
       color: #fff;

       height: calc(var(--kpi-badge-h, 14px) * var(--ui-scale, 1) * var(--kpi-badge-scale, var(--kpi-box-badge-scale, 1)));
       min-width: calc(var(--kpi-badge-min-w, 36px) * var(--ui-scale, 1) * var(--kpi-badge-scale, var(--kpi-box-badge-scale, 1)));
       padding: 0 calc(var(--kpi-badge-pad-x, 4px) * var(--ui-scale, 1) * var(--kpi-badge-scale, var(--kpi-box-badge-scale, 1)));

       font-size: calc(var(--fs-label) * 0.99 * var(--kpi-badge-scale, var(--kpi-box-badge-scale, 1)));
       font-weight: 400;
       line-height: 1;
       text-align: center;
     ">
  {txt}
</div>
""".strip()

    # ------------------------------------------------------------------
    # Pré-processamento
    # ------------------------------------------------------------------

    left_badge_raw = _coerce_percent_if_numeric(left_badge)
    right_badge_raw = str(right_pill or "").strip()

    left_badge_html = _left_badge_html(left_badge_raw)
    right_badge_html = _right_badge_html(right_badge_raw)

    left_label_html = _label_html(left_label)
    mid_label_html = _label_html(mid_label)

    left_badge_scale = _badge_scale_for_raw(left_badge_raw)
    right_badge_scale = _badge_scale_for_raw(right_badge_raw)

    left_label_scale = 1.00 if left_badge_scale < 0.99 else None
    right_label_scale = 1.00 if right_badge_scale < 0.99 else None

    # ------------------------------------------------------------------
    # HTML
    # ------------------------------------------------------------------

    return f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap');

  .kpi-card {{
    font-family: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif !important;
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }}

  .kpi-card, .kpi-card * {{
    font-family: inherit !important;
  }}

  .kpi-card svg, .kpi-card text, .kpi-card tspan {{
    font-family: inherit !important;
  }}

  .kpi-card .tabular-nums {{
    font-variant-numeric: proportional-nums lining-nums !important;
    font-feature-settings: "tnum" 0, "lnum" 1 !important;
  }}
</style>

<div class="kpi-card bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full flex flex-col"
     style="
       padding: var(--pad);
       border-radius: 12px;

       --kpi-gauge-zoom: 1.04;
       --kpi-gauge-shift-y: -1px;
       --kpi-boxes-shift-y: -10px;
       --kpi-boxes-gap-delta: -10px;

       --kpi-box-min-h-delta: 14px;

       --kpi-box-label-scale: 1.001;
       --kpi-box-value-scale: 1.3;
       --kpi-box-badge-scale: 1.00;

       --kpi-box-title-value-gap: calc(4px * var(--ui-scale, 1));
       --kpi-boxes-inset-x: calc(5.8px * var(--ui-scale, 1));

       --kpi-badge-h: 14px;
       --kpi-badge-min-w: 36px;
       --kpi-badge-pad-x: 4px;

       --kpi-left-badge-font-scale: 0.96;
       /* ✅ ajuste fino do alinhamento vertical do conteúdo do badge esquerdo */
       --kpi-left-badge-content-nudge-y: 0.7;
     ">

  <div class="kpi-title"
       style="font-size: var(--fs-title); line-height: 1.1; color:#060606; font-weight:400;">
    {title}
  </div>

  <div class="kpi-gauge relative mt-2 flex-1 flex justify-center items-center"
       style="
         transform: translateY(var(--kpi-gauge-shift-y, 0px));
         transform-origin: top;

         --kpi-gauge-scale-safe: clamp(0.78, var(--kpi-gauge-scale, 0.92), 1);
         --gauge-scale: calc(var(--kpi-gauge-scale-safe) * var(--kpi-gauge-zoom, 1));

         min-height: calc(var(--gauge-min-h) * var(--kpi-gauge-scale-safe));
         padding-top: calc(6px * var(--ui-scale));
         padding-left: calc(10px * var(--ui-scale));
         padding-right: calc(10px * var(--ui-scale));
         box-sizing: border-box;
       ">

    {svg}

    <div class="absolute inset-0 flex flex-col items-center justify-center text-center"
         style="transform: translateY(var(--gauge-text-shift));">
      <div class="tabular-nums"
           style="font-size: var(--fs-center); line-height: 1; color:#000000; font-weight:600;">
        {pct_txt}%
      </div>

      <div style="font-size: var(--fs-sub); margin-top: 6px; line-height: 1.1; color:#454545; font-weight:400;">
        {subtitle}
      </div>
    </div>
  </div>

  <div class="mt-2 grid grid-cols-2"
       style="
         box-sizing: border-box;

         padding-left:  var(--kpi-boxes-inset-x, 0px);
         padding-right: var(--kpi-boxes-inset-x, 0px);

         gap: calc(var(--gap) + var(--kpi-boxes-gap-delta, 0px));
         transform: translateY(var(--kpi-boxes-shift-y, 0px));
         transform-origin: top;
       ">

    <!-- BOX ESQUERDO -->
    <div class="kpi-box bg-[#F6F6F6] rounded-2xl flex flex-col"
         style="
           --kpi-box-pad: calc(var(--box-pad) + var(--box-pad-extra));

           --kpi-badge-scale: {left_badge_scale};
           {'--kpi-label-scale: 1.00;' if left_label_scale is not None else ''}

           padding-left:  var(--kpi-box-pad);
           padding-right: calc(var(--kpi-box-pad) - var(--kpi-badge-nudge-right, 0px));
           padding-top:   calc(var(--kpi-box-pad) - var(--kpi-box-pad-y-reduce, 0px));
           padding-bottom:calc(var(--kpi-box-pad) - var(--kpi-box-pad-y-reduce, 0px));

           min-height: calc(var(--pill-min-h) + var(--kpi-box-min-h-delta, 0px));
           gap: calc(6px * var(--ui-scale) - var(--kpi-box-gap-reduce, 0px));
         ">

      <div class="flex items-start justify-between"
           style="gap: calc(6px * var(--ui-scale));">
        <div class="text-left"
             style="
               font-size: calc((var(--fs-label) - 1px) * var(--kpi-label-scale, var(--kpi-box-label-scale, 1)));
               line-height: 1.15;
               flex: 1 1 auto;
               min-width: 0;
               display: -webkit-box;
               -webkit-line-clamp: 2;
               -webkit-box-orient: vertical;
               overflow: hidden;
               color: #454545;
               font-weight: 400;
             ">
          {left_label_html}
        </div>
        {left_badge_html}
      </div>

      <div class="tabular-nums"
           style="
             margin-top: var(--kpi-box-title-value-gap);
             font-size: calc(var(--fs-kpi) * var(--kpi-box-value-scale, 1));
             line-height: 1;
             font-weight:600;
             color: #000000;
           ">
        {left_value}
      </div>
    </div>

    <!-- BOX DIREITO -->
    <div class="kpi-box bg-[#F6F6F6] rounded-2xl flex flex-col"
         style="
           --kpi-box-pad: calc(var(--box-pad) + var(--box-pad-extra));

           --kpi-badge-scale: {right_badge_scale};
           {'--kpi-label-scale: 1.00;' if right_label_scale is not None else ''}

           padding-left:  var(--kpi-box-pad);
           padding-right: calc(var(--kpi-box-pad) - var(--kpi-badge-nudge-right, 0px));
           padding-top:   calc(var(--kpi-box-pad) - var(--kpi-box-pad-y-reduce, 0px));
           padding-bottom:calc(var(--kpi-box-pad) - var(--kpi-box-pad-y-reduce, 0px));

           min-height: calc(var(--pill-min-h) + var(--kpi-box-min-h-delta, 0px));
           gap: calc(6px * var(--ui-scale) - var(--kpi-box-gap-reduce, 0px));
         ">

      <div class="flex items-start justify-between"
           style="gap: calc(6px * var(--ui-scale));">
        <div class="text-left"
             style="
               font-size: calc((var(--fs-label) - 1px) * var(--kpi-label-scale, var(--kpi-box-label-scale, 1)));
               line-height: 1.15;
               flex: 1 1 auto;
               min-width: 0;
               display: -webkit-box;
               -webkit-line-clamp: 2;
               -webkit-box-orient: vertical;
               overflow: hidden;
               color: #454545;
               font-weight: 400;
             ">
          {mid_label_html}
        </div>
        {right_badge_html}
      </div>

      <div class="tabular-nums"
           style="
             margin-top: var(--kpi-box-title-value-gap);
             font-size: calc(var(--fs-kpi) * var(--kpi-box-value-scale, 1));
             line-height: 1;
             font-weight:600;
             color: #000000;
           ">
        {mid_value}
      </div>
    </div>

  </div>
</div>
""".strip()
