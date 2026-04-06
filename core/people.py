from __future__ import annotations


def pretty_name(name_upper: str) -> str:
    """Recebe nome em UPPER (como vem do DF) e devolve um formato agradável."""
    s = (name_upper or "").strip().title()
    s = s.replace("SDR", "SDR").replace("Sdr", "SDR").replace("Closer", "CLOSER")
    return s


def dashboard_display_name(name_upper: str, original_name_upper: str | None = None) -> str:
    """Nome exibido no dashboard.

    Regra especial:
    - se o nome original vindo da base for 'MARIA EDUARDA', exibe apenas 'Eduarda';
    - caso contrário, usa o nome formatado normalmente.

    O parâmetro ``name_upper`` pode ser o nome canônico/alias usado internamente.
    O parâmetro ``original_name_upper`` deve preservar o nome original da base
    (antes da aplicação de aliases), quando disponível.
    """
    original = (original_name_upper or "").strip().upper()
    if original == "MARIA EDUARDA":
        return "Eduarda"
    base = (name_upper or original_name_upper or "").strip().upper()
    return pretty_name(base)


PHOTO_FILES: dict[str, str] = {
    #"NURY": "assets/photos/nury.png",
    #"GUILHERME": "assets/photos/guilherme.png",
    #"MARIA EDUARDA": "assets/photos/maria.png",
    # Algumas fontes podem vir sem acento (JOAO) — deixamos os 2
    #"JOÃO": "assets/photos/joao.png",
    #"JOAO": "assets/photos/joao.png",
}
PHOTO_URLS: dict[str, str] = {
    "NURY": "https://i.imgur.com/KPbuDpB.png",
    "MARIA": "https://i.imgur.com/mxT5m7g.png",
    "JOÃO": "https://i.imgur.com/wl4sktg.png",
    "JOAO": "https://i.imgur.com/wl4sktg.png",
    "VICTOR": "https://i.imgur.com/oL93SKm.png",
    "LAURA": "https://i.imgur.com/oD23A9c.png",
    "CODRI": "https://i.imgur.com/fakgDcL.png",
    "MATHEUS": "https://i.imgur.com/uKjvrb1.png",
    "RAISSA": "https://i.imgur.com/7z9lI91.jpeg",
    "ARTHUR": "https://i.imgur.com/I46ZNA2.jpeg"
}
