import math


def gauge_svg(
    percent: float,
    segments: int = 16,
    filled: str = "#F05914",
    empty: str = "#F5F5F5",
) -> str:
    """
    Gauge estilo 'pílulas' (retângulos arredondados), no formato do mock.

    - segments: quantidade de pílulas no arco
    - filled/empty: cores preenchido/vazio
    """
    percent = max(0.0, min(100.0, float(percent)))
    filled_count = int(round((percent / 100.0) * segments))

    # Geometria do SVG
    vb_w, vb_h = 240, 160
    cx, cy = 120, 130

    # Pílulas
    seg_w = 12.6        # "largura" (tangencial)
    seg_len = 34        # "comprimento" (radial)
    r_inner = 88        # onde começa a pílula (raio interno)

    # Arco (ângulos em graus, topo)
    arc_start = 200     # lado esquerdo
    arc_end = 340       # lado direito
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
              <rect x="{-(seg_w/2):.2f}" y="0" width="{seg_w:.2f}" height="{seg_len:.2f}"
                    rx="{(seg_w/2):.2f}" ry="{(seg_w/2):.2f}"
                    fill="{color}" />
            </g>
            """
        )

    return f"""
    <svg viewBox="0 0 {vb_w} {vb_h}" style="width: min(var(--gauge-w), 100%); height: auto; max-width: 100%; display: block; margin: 0 auto;" aria-hidden="true">
      {''.join(pills)}
    </svg>
    """
