from __future__ import annotations


def pretty_name(name_upper: str) -> str:
    """Recebe nome em UPPER (como vem do DF) e devolve um formato agradável."""
    s = (name_upper or "").strip().title()
    s = s.replace("SDR", "SDR").replace("Sdr", "SDR").replace("Closer", "CLOSER")
    return s


# =========================
# Fotos por pessoa
# =========================
# ✅ Preferência: arquivo local (mais confiável do que URL em <img> dentro do Streamlit/components)
# Chave SEMPRE em UPPER (como vem do dataframe).
PHOTO_FILES: dict[str, str] = {
    #"NURY": "assets/photos/nury.png",
    #"GUILHERME": "assets/photos/guilherme.png",
    #"MARIA EDUARDA": "assets/photos/maria.png",
    # Algumas fontes podem vir sem acento (JOAO) — deixamos os 2
    #"JOÃO": "assets/photos/joao.png",
    #"JOAO": "assets/photos/joao.png",
}

# (opcional) Se quiser usar URL ao invés de arquivo local
# Observação: links do Google Drive às vezes retornam HTML (ou exigem permissões/cookies),
# o que faz o <img> falhar. Por isso o default do app usa PHOTO_FILES.
PHOTO_URLS: dict[str, str] = {
    "NURY": "https://aslibuujaazfedmrpytj.supabase.co/storage/v1/object/public/email_storage/nury.png",
    "MARIA": "https://aslibuujaazfedmrpytj.supabase.co/storage/v1/object/public/email_storage/maria.png",
    "JOÃO": "https://aslibuujaazfedmrpytj.supabase.co/storage/v1/object/public/email_storage/joao.png",
    "JOAO": "https://aslibuujaazfedmrpytj.supabase.co/storage/v1/object/public/email_storage/joao.png",
    "GUILHERME": "https://aslibuujaazfedmrpytj.supabase.co/storage/v1/object/public/email_storage/guilherme.png",
}
