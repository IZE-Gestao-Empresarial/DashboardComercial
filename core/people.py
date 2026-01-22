from __future__ import annotations

def pretty_name(name_upper: str) -> str:
    """Recebe nome em UPPER (como vem do DF) e devolve um formato agradável."""
    s = (name_upper or "").strip().title()
    s = s.replace("Sdk", "SDK").replace("Sdr", "SDR").replace("Closer", "CLOSER")
    return s


# ✅ Coloque aqui os links das fotos (você vai editar manualmente depois)
# Chave precisa estar em UPPER (igual ao DF, ex: "JOÃO", "MARIA EDUARDA")
PHOTO_URLS: dict[str, str] = {
    # "JOÃO": "https://.../joao.jpg",
    # "MARIA EDUARDA": "https://.../maria.jpg",
}
