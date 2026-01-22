import math


def gauge_svg(
    percent: float,
    segments: int = 12,
    filled: str = "#F05914",
    empty: str = "#EEEEEE",
) -> str:
    """
    Gauge estilo 'pílulas' (retângulos arredondados).
    - segments: quantidade de pílulas
    - filled/empty: cores preenchido/vazio
    """
    percent = max(0.0, min(100.0, float(percent)))
    filled_count = int(round((percent / 100.0) * segments))

    # Geometria do SVG
    vb_w, vb_h = 220, 160
    cx, cy = 110, 130

    # Pílulas
    seg_w = 20          # "largura" (tangencial)
    seg_len = 56        # "comprimento" (radial)
    r_inner = 62        # onde começa a pílula (raio interno)

    # Arco (ângulos em graus, topo)
    arc_start = 200     # lado esquerdo (um pouco abaixo da horizontal)
    arc_end = 340       # lado direito (um pouco abaixo da horizontal)
    step = (arc_end - arc_start) / segments

    pills = []
    for i in range(segments):
        ang = arc_start + (i + 0.5) * step
        rad = math.radians(ang)

        # ponto de ancoragem (início da pílula)
        x = cx + r_inner * math.cos(rad)
        y = cy + r_inner * math.sin(rad)

        color = filled if i < filled_count else empty

        pills.append(
            f"""
            <g transform="translate({x:.2f} {y:.2f}) rotate({ang - 90:.2f})">
              <rect x="{-(seg_w/2):.2f}" y="0" width="{seg_w}" height="{seg_len}"
                    rx="{seg_w/2:.2f}" ry="{seg_w/2:.2f}"
                    fill="{color}" />
            </g>
            """
        )

    return f"""
    <svg viewBox="0 0 {vb_w} {vb_h}" style="width: var(--gauge-w); height: auto;" aria-hidden="true">
      {''.join(pills)}
    </svg>
    """
