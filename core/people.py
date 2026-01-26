from __future__ import annotations

from pathlib import Path


def pretty_name(name_upper: str) -> str:
    """Recebe nome em UPPER (como vem do DF) e devolve um formato agradável."""
    s = (name_upper or "").strip().title()
    s = s.replace("SDR", "SDR").replace("Sdr", "SDR").replace("Closer", "CLOSER")
    return s
# Mapeamento de fotos por nome em UPPER
PHOTO_FILES: dict[str, str] = {
    "NURY": "assets/photos/nury.png",
    "GUILHERME": "assets/photos/guilherme.png",
    "MARIA EDUARDA": "assets/photos/maria.png",
    "JOÃO": "assets/photos/joao.png",
}

# (opcional) Se quiser usar URL ao invés de arquivo local
PHOTO_URLS: dict[str, str] = {

}
