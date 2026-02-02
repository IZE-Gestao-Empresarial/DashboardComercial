import math

_RECT56_D = (
    "M62.8002 0C71.6745 0 78.6088 7.66227 77.7257 16.4926"
    "L64.7257 146.493C63.9589 154.161 57.5065 160 49.8002 160"
    "H28.4077C20.7192 160 14.2755 154.187 13.4868 146.539"
    "L0.0805531 16.5387C-0.831684 7.69276 6.10858 0 15.0014 0"
    "L62.8002 0Z"
)


def gauge_svg(
    percent: float,
    segments: int = 13,
    filled: str = "#EA591A",
    empty: str = "#F6F6F6",
) -> str:


    percent = max(0.0, min(100.0, float(percent or 0.0)))
    segments = max(1, int(segments))
    filled_count = int(round((percent / 100.0) * segments))

    # Geometria do SVG (mantém envelope compatível com o layout existente)
    vb_w, vb_h = 240, 160
    cx, cy = 120, 130

    # Dimensões do segmento base
    base_w, base_h = 78.0, 160.0

    # Tamanho final do segmento no gauge
    seg_len = 42.0  # ajuste fino do "comprimento" radial
    scale = seg_len / base_h
    r_inner = 75.0  # raio interno onde começa o segmento

    # Arco (ângulos em graus) – mais aberto nas pontas, igual ao Frame 7
    arc_start = 185.0
    arc_end = 355.0
    step = (arc_end - arc_start) / float(segments)

    segs = []
    for i in range(segments):
        ang = arc_start + (i + 0.5) * step
        rad = math.radians(ang)

        # ponto de ancoragem (raio interno)
        x = cx + r_inner * math.cos(rad)
        y = cy + r_inner * math.sin(rad)

        color = filled if i < filled_count else empty

        segs.append(
            f"""
            <g transform="translate({x:.2f} {y:.2f}) rotate({ang + 90:.2f}) scale({scale:.4f}) translate({-base_w/2:.2f} {-base_h:.2f})">
              <path d="{_RECT56_D}" fill="{color}" />
            </g>
            """
        )

    return f"""
    <svg viewBox="0 0 {vb_w} {vb_h}" style="width: min(var(--gauge-w), 100%); height: auto; max-width: 100%; display: block; margin: 0 auto;" aria-hidden="true">
      {''.join(segs)}
    </svg>
    """
