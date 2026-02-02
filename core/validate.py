from __future__ import annotations

from typing import Any, Dict, Tuple

EXPECTED_ROW_KEYS = ("INDICADORES", "RESPONSÁVEL", "VALOR", "DATA_ATUALIZAÇÃO")


def validate_payload(payload: Any) -> Tuple[bool, str]:
    """
    Valida o formato do payload do Apps Script.

    Retorna:
      (ok, mensagem)

    Observação:
    - Se faltar alguma coluna esperada, isso NÃO é erro fatal: a aplicação pode preencher com None.
    """
    if not isinstance(payload, dict):
        return False, "Payload inválido: resposta não é um objeto JSON (dict)."

    if "error" in payload and "rows" not in payload:
        return False, f"Endpoint retornou erro: {payload.get('error')}"

    rows = payload.get("rows", None)
    if rows is None:
        return False, "Payload inválido: campo 'rows' ausente."
    if not isinstance(rows, list):
        return False, "Payload inválido: campo 'rows' não é uma lista."

    if len(rows) == 0:
        return True, "Payload OK (rows vazio)."

    first = rows[0]
    if not isinstance(first, dict):
        return False, "Payload inválido: items de 'rows' não são objetos."

    missing = [k for k in EXPECTED_ROW_KEYS if k not in first]
    if missing:
        return True, f"Payload OK (colunas ausentes serão preenchidas): {', '.join(missing)}"

    return True, "Payload OK."
