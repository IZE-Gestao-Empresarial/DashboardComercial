from __future__ import annotations

import html


def _fmt_int_br(x: float | int | None) -> str:
    """Inteiro com separador pt-BR (.) — ex.: 12345 -> 12.345"""
    try:
        n = int(round(float(x or 0)))
    except Exception:
        n = 0
    return f"{n:,}".replace(",", ".")


def _pct_br(x: float | int | None, decimals: int) -> str:
    """Percentual pt-BR com casas fixas e sufixo %."""
    try:
        v = float(x or 0.0)
    except Exception:
        v = 0.0
    v = max(0.0, min(999.99, v))
    s = f"{v:.{decimals}f}".replace(".", ",")
    return f"{s}%"


def funil_vendas_card_html(
    *,
    title: str = "Funil de Vendas",
    leads: float | int | None,
    reunioes: float | int | None,
    contratos: float | int | None,
    pct_leads_para_reunioes: float | int | None = None,
    pct_reunioes_para_contratos: float | int | None = None,
) -> str:
    """
    Card "Funil de Vendas" (3 estágios) no visual do protótipo.

    - Topo: Leads
    - Meio: Reuniões
    - Fundo: Contratos
    - Pills à direita: % de conversão em cada etapa

    Se `pct_*` não for fornecido, calculamos:
      - leads -> reuniões = reunioes/leads * 100
      - reuniões -> contratos = contratos/reunioes * 100
    """

    title = (title or "").strip() or "Funil de Vendas"

    l = float(leads or 0.0)
    r = float(reunioes or 0.0)
    c = float(contratos or 0.0)

    if pct_leads_para_reunioes is None:
        p1 = (r / l * 100.0) if l > 0 else 0.0
    else:
        p1 = float(pct_leads_para_reunioes or 0.0)

    if pct_reunioes_para_contratos is None:
        p2 = (c / r * 100.0) if r > 0 else 0.0
    else:
        p2 = float(pct_reunioes_para_contratos or 0.0)

    leads_txt = _fmt_int_br(l)
    reunioes_txt = _fmt_int_br(r)
    contratos_txt = _fmt_int_br(c)

    # igual ao print: 1ª pill com 1 casa; 2ª com 2 casas
    p1_txt = _pct_br(p1, 1)
    p2_txt = _pct_br(p2, 2)

    # Paths/posições extraídos do protótipo (viewBox 2048x1094)
    PATH_TOP = (
        "M 1482.0 363.5 L 564.0 363.5 L 551.0 359.5 L 535.0 348.5 "
        "L 521.5 328.0 L 480.5 195.0 L 478.5 167.0 L 486.5 147.0 "
        "L 501.0 131.5 L 527.0 121.5 L 1526.0 122.5 L 1544.0 129.5 "
        "L 1559.5 144.0 L 1569.5 167.0 L 1569.5 187.0 L 1524.5 328.0 "
        "L 1511.0 348.5 L 1502.0 355.5 L 1482.0 363.5 Z"
    )
    PATH_MID = (
        "M 1335.0 628.5 L 710.0 627.5 L 691.0 617.5 L 677.5 599.0 "
        "L 626.5 446.0 L 626.5 417.0 L 642.0 394.5 L 664.0 384.5 "
        "L 1390.0 385.5 L 1405.0 392.5 L 1418.5 407.0 L 1424.5 422.0 "
        "L 1423.5 445.0 L 1374.5 599.0 L 1361.0 617.5 L 1352.0 623.5 "
        "L 1335.0 628.5 Z"
    )
    PATH_ORA = (
        "M 1198.0 898.5 L 852.0 898.5 L 838.0 893.5 L 823.5 881.0 "
        "L 817.5 871.0 L 766.5 714.0 L 765.5 696.0 L 773.5 676.0 "
        "L 788.0 662.5 L 805.0 656.5 L 1246.0 656.5 L 1263.0 662.5 "
        "L 1275.5 674.0 L 1282.5 686.0 L 1285.5 697.0 L 1283.5 717.0 "
        "L 1233.5 870.0 L 1221.0 887.5 L 1211.0 894.5 L 1198.0 898.5 Z"
    )

    # Cores do protótipo
    TOP = "#403D38"
    MID = "#F1F1F1"
    ORA = "#EA591A"
    PILL = "#252422"
    LINE1 = "#C6C6C6"
    LINE2 = "#C0C0C0"

    return f"""
<div class="fv-card" role="group" aria-label="{html.escape(title)}">
  <div class="fv-stage">
    <div class="fv-figure" role="img" aria-label="Funil de vendas com conversões por etapa">
      <svg class="fv-svg" viewBox="0 0 2048 1094" preserveAspectRatio="xMidYMid meet" aria-hidden="true" focusable="false">
        <style>
          .fv-t {{
            font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
          }}
          .fv-num1 {{ font-size: 92px; font-weight: 800; fill: #fff; letter-spacing: -0.5px; }}
          .fv-lbl1 {{ font-size: 56px; font-weight: 500; fill: rgba(255,255,255,0.92); }}
          .fv-num2 {{ font-size: 90px; font-weight: 800; fill: #000; letter-spacing: -0.5px; }}
          .fv-lbl2 {{ font-size: 58px; font-weight: 500; fill: rgba(0,0,0,0.86); }}
          .fv-num3 {{ font-size: 92px; font-weight: 800; fill: #fff; letter-spacing: -0.5px; }}
          .fv-lbl3 {{ font-size: 58px; font-weight: 500; fill: rgba(255,255,255,0.95); }}
          .fv-pct  {{ font-size: 60px; font-weight: 500; fill: #fff; }}
          .fv-title{{ font-size: 58px; font-weight: 500; fill: {TOP}; }}
        </style>

        <!-- Shapes -->
        <path d="{PATH_TOP}" fill="{TOP}"/>
        <path d="{PATH_MID}" fill="{MID}"/>
        <path d="{PATH_ORA}" fill="{ORA}"/>

        <!-- Linhas conectoras -->
        <line x1="1483" y1="364" x2="1590" y2="364" stroke="{LINE1}" stroke-width="3" stroke-linecap="round"/>
        <line x1="1343" y1="627" x2="1439" y2="627" stroke="{LINE2}" stroke-width="3" stroke-linecap="round"/>

        <!-- Pills -->
        <rect x="1592" y="318" width="303" height="92" rx="46" fill="{PILL}"/>
        <rect x="1440" y="582" width="304" height="92" rx="46" fill="{PILL}"/>

        <!-- Textos -->
        <text class="fv-t fv-num1" x="1022" y="228" text-anchor="middle">{html.escape(leads_txt)}</text>
        <text class="fv-t fv-lbl1" x="1022" y="304" text-anchor="middle">Leads</text>

        <text class="fv-t fv-num2" x="1023" y="492" text-anchor="middle">{html.escape(reunioes_txt)}</text>
        <text class="fv-t fv-lbl2" x="1023" y="564" text-anchor="middle">Reuniões</text>

        <text class="fv-t fv-num3" x="1024" y="778" text-anchor="middle">{html.escape(contratos_txt)}</text>
        <text class="fv-t fv-lbl3" x="1024" y="846" text-anchor="middle">Contratos</text>

        <text class="fv-t fv-pct" x="1743" y="392" text-anchor="middle">{html.escape(p1_txt)}</text>
        <text class="fv-t fv-pct" x="1592" y="658" text-anchor="middle">{html.escape(p2_txt)}</text>

        <text class="fv-t fv-title" x="1024" y="980" text-anchor="middle">{html.escape(title)}</text>
      </svg>
    </div>
  </div>
</div>
""".strip()
