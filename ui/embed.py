from __future__ import annotations

import base64
import mimetypes
from pathlib import Path

# raiz do projeto (ui/..)
BASE_DIR = Path(__file__).resolve().parents[1]


def file_to_data_uri(path: str | Path) -> str | None:
    """Lê um arquivo local e retorna um data URI (base64) para usar em <img src='...'>.

    - Aceita caminhos relativos (ex: 'assets/photos/nury.png') e resolve a partir da raiz do projeto.
    - Retorna None se o arquivo não existir.
    """
    p = Path(path)
    if not p.is_absolute():
        p = BASE_DIR / p

    if not p.exists() or not p.is_file():
        return None

    mime, _ = mimetypes.guess_type(str(p))
    if not mime:
        mime = "application/octet-stream"

    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"
