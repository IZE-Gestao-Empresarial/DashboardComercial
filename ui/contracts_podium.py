from __future__ import annotations

from core.formatters import fmt_int, fmt_money
from ui.ranklist import ranking_closer_card_html


def _fmt_money_br_no_symbol(v) -> str:
    """
    Retorna valor no padrão BR sem 'R$':
    - 98874 -> "98.874"
    - None/NaN -> "0,00"
    """
    try:
        s = fmt_money(v)  # ex: "R$ 98.874,00"
        s = str(s or "").strip()

        if not s or s == "-":
            return "0,00"

        # remove símbolo se vier
        s = s.replace("R$", "").strip()

        # se termina com ,00, remove para ficar compacto (igual seu layout)
        if s.endswith(",00"):
            s = s[:-3]

        if s in ("0,00", "0"):
            return "0"

        return s
    except Exception:
        return "0,00"


def podium_contracts_card_html(rows: list[dict], title: str = "Ranking Closer", limit: int = 10, avatar_size_px: int = 56) -> str:
    """Ranking Closer (layout do mock).

    A colocação é definida por:
      1) FATURAMENTO ASSINADO (desc)
      2) Em empate, FATURAMENTO PAGO (desc)
      3) Em novo empate, CONTRATOS (desc)
      4) Por fim, NOME (asc) para estabilidade
    Espera `rows` com chaves:
      - name, contratos, fat_assinado, fat_pago
      - (opcional) PERC FATURAMENTO PAGO -> percentual a exibir abaixo de "contratos"
      - (opcional) pct -> fallback/compatibilidade
    """
    if not rows:
        return '''
        <div class="bg-white rounded-xl shadow-sm border border-zinc-100 h-full w-full flex items-center justify-center">
          <div class="text-zinc-500 font-semibold">Sem dados</div>
        </div>
        '''

    def _f(v) -> float:
        try:
            return float(v or 0.0)
        except Exception:
            return 0.0

    ordered = sorted(
        rows,
        key=lambda r: (
            -_f(r.get("fat_assinado")),
            -_f(r.get("fat_pago")),
            -_f(r.get("contratos")),
            str(r.get("name") or "").strip().upper(),
        ),
    )

    formatted = []
    for r in ordered:
        name = r.get("name")
        display_name = r.get("display_name")

        # ✅ prioriza a chave "oficial" que o ranklist procura por padrão
        pct_val = r.get("PERC FATURAMENTO PAGO")
        if pct_val is None:
            pct_val = r.get("pct")

        formatted.append(
            {
                "name": name,
                "display_name": display_name,
                "contratos": fmt_int(r.get("contratos")),
                "fat_assinado": _fmt_money_br_no_symbol(r.get("fat_assinado")),
                "fat_pago": _fmt_money_br_no_symbol(r.get("fat_pago")),

                # ✅ garante que o ranklist pegue pelo pct_field="PERC FATURAMENTO PAGO"
                "PERC FATURAMENTO PAGO": pct_val,

                # ✅ mantém fallback compatível (ranklist também busca "pct")
                "pct": pct_val,
            }
        )

    return ranking_closer_card_html(
        title=title,
        rows=formatted,
        limit=limit,
        avatar_size_px=avatar_size_px,
    )