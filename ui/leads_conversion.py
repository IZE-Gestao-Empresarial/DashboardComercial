from __future__ import annotations

import html
import math

from core.formatters import fmt_int
from ui.ranklist import fmt_percent_br


def _dot_ring_svg(percent: float, *, size: int = 360) -> str:
    """Anel de pontos idêntico ao visual 'Taxa de Conversão (3)'.
    
    - Total de 15 pontos.
    - Preenchimento sentido horário.
    - Ponto de partida ajustado para o canto inferior esquerdo (~145 graus).
    """
    pct = max(0.0, min(100.0, float(percent or 0.0)))
    
    # Na imagem referência: 15 pontos no total.
    # 7,8% acende 3 pontos. A lógica visual parece ser um "step" fixo ou teto.
    # Vamos manter proporcional:
    dots_total = 15
    on = int(math.ceil((pct / 100.0) * dots_total))
    
    # Garante visual mínimo se houver valor positivo (como na imagem)
    if pct > 0 and on < 1: 
        on = 1
    on = max(0, min(dots_total, on))

    on_idx: set[int] = set()
    for k in range(on):
        on_idx.add(k)

    cx = cy = size / 2
    # Raio do anel
    r = size * 0.42 
    # Raio de cada ponto (ajustado visualmente)
    dot_r = size * 0.048

    circles: list[str] = []
    
    # Ajuste de ângulo:
    # 0 rad = 3h (Direita).
    # SVG y cresce para baixo. Sentido horário = aumenta ângulo.
    # Queremos começar em ~8h. Isso é aprox 135 a 150 graus (conversão visual).
    # Math.pi = 180 (9h). Vamos começar um pouco antes.
    start_angle = math.radians(150) 

    step = (2 * math.pi) / dots_total

    for i in range(dots_total):
        # Calcula posição
        ang = start_angle + (step * i)
        x = cx + r * math.cos(ang)
        y = cy + r * math.sin(ang)
        
        # Cores exatas da imagem
        # Ativo = Laranja (#F4561F)
        # Inativo = Cinza Escuro (#403D38 - tom retirado da imagem/CSS)
        fill = "#F4561F" if i in on_idx else "#403D38"
        
        circles.append(f"<circle cx='{x:.2f}' cy='{y:.2f}' r='{dot_r:.2f}' fill='{fill}' />")

    return f"""<svg class='lc-ring' viewBox='0 0 {size} {size}' aria-hidden='true'>
      {''.join(circles)}
    </svg>"""

def leads_conversion_card_html(
    *,
    leads_total: float | int | None,
    taxa_conversao: float | None,
    title: str = "Leads | Taxa de Conversão (Geral)",
) -> str:
    """Card 'Taxa de Conversão | Leads' (Design Prototipo 3)."""
    
    leads_txt = fmt_int(leads_total)
    pct = float(taxa_conversao or 0.0)

    if taxa_conversao is None:
        pct_txt = "-"
    else:
        # Formato "7,8 %" (com espaço antes do %)
        pct_txt = fmt_percent_br(pct).replace("%", " %")

    # Gera o anel
    ring = _dot_ring_svg(pct, size=300)

    return f"""<div class='lc-card' aria-label='{html.escape(title)}'>
      
      <div class='lc-gauge-side'>
        <div class='lc-ring-wrap'>
          {ring}
          <div class='lc-ring-text'>
            <div class='lc-pct'>{html.escape(pct_txt)}</div>
            <div class='lc-label'>Taxa de Conversão</div>
          </div>
        </div>
      </div>

      <div class='lc-data-side'>
        <div class='lc-pill'>
          {html.escape(leads_txt)}
        </div>
        <div class='lc-data-label'>Leads Criados</div>
      </div>

    </div>"""