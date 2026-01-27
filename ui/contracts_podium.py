from __future__ import annotations

from core.formatters import fmt_int, fmt_money
from ui.ranklist import ranking_closer_card_html


def _fmt_money_br_no_symbol(v) -> str:
    """
    Retorna valor no padrão BR sem 'R$':
    - 98874 -> "98.874,00"
    - None/NaN -> "0,00"
    """
    # fmt_money no seu projeto geralmente retorna "98.874,00" (sem R$)
    # Mas como pode retornar "-" dependendo da implementação, aqui garantimos fallback.
    try:
        s = fmt_money(v)  # esperado: "98.874,00"
        if not s or str(s).strip() == "-":
            return "0,00"
        return str(s).strip()
    except Exception:
        return "0,00"


def podium_contracts_card_html(rows: list[dict], title: str = "Ranking Closer") -> str:
    """Ranking Closer (layout do mock).

    A colocação é definida SOMENTE por FATURAMENTO PAGO (desc).
    Espera `rows` com chaves: name, contratos, fat_assinado, fat_pago.
    """
    if not rows:
        return '''
        <div class="bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full flex items-center justify-center">
          <div class="text-zinc-500 font-semibold">Sem dados</div>
        </div>
        '''

    def _k(r: dict) -> float:
        try:
            return float(r.get("fat_pago") or 0.0)
        except Exception:
            return 0.0

    ordered = sorted(rows, key=_k, reverse=True)

    # Formata os campos para exibição no card
    formatted = []
    for r in ordered:
        name = r.get("name")
        formatted.append(
            {
                "name": name,
                "contratos": fmt_int(r.get("contratos")),
                # ✅ agora fica "98.874,00"
                "fat_assinado": _fmt_money_br_no_symbol(r.get("fat_assinado")),
                "fat_pago": _fmt_money_br_no_symbol(r.get("fat_pago")),
            }
        )

    return ranking_closer_card_html(
        title=title,
        rows=formatted,
        limit=2,
        avatar_size_px=56,
    )
