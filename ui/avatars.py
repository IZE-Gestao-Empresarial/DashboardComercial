from __future__ import annotations

import html
import re

from core.people import PHOTO_FILES, PHOTO_URLS, pretty_name
from ui.embed import file_to_data_uri


_DRIVE_ID_RE = re.compile(r"(?:id=|/d/)([a-zA-Z0-9_-]{10,})")


def initials(name_upper: str) -> str:
    parts = [p for p in (name_upper or "").strip().split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def _normalize_img_url(url: str) -> str:
    """
    Converte links comuns do Drive para um formato que funciona melhor em <img>.

    Aceita:
      - ...id=FILE_ID
      - .../d/FILE_ID/...
      - ...drive.usercontent.google.com/download?id=FILE_ID...
    Retorna:
      - https://drive.google.com/uc?export=view&id=FILE_ID
    """
    u = (url or "").strip()
    if not u:
        return ""

    m = _DRIVE_ID_RE.search(u)
    if m:
        file_id = m.group(1)
        return f"https://drive.google.com/uc?export=view&id={file_id}"

    return u


def photo_src(name_upper: str) -> str | None:
    """Retorna src para <img>.

    Ordem de preferência:
      1) Foto local (PHOTO_FILES) embutida como data URI (base64) → mais estável/rápido.
      2) URL (PHOTO_URLS) normalizada (ex.: Google Drive) → pode falhar dependendo de permissão/cookies.
    """
    key = (name_upper or "").strip().upper()

    # 1) arquivo local → data URI
    local_path = PHOTO_FILES.get(key)
    if local_path:
        data_uri = file_to_data_uri(local_path)
        if data_uri:
            return data_uri

    # 2) URL (fallback)
    url = PHOTO_URLS.get(key)
    if url:
        norm = _normalize_img_url(url)
        return norm or None

    return None


def avatar_html(name_upper: str, size_px: int = 44, ring_px: int = 2) -> str:
    key = (name_upper or "").strip().upper()
    src = photo_src(key)
    safe_title = html.escape(pretty_name(key))

    ini = html.escape(initials(key))
    font_px = max(12, int(size_px * 0.35))

    size_css = f"calc({size_px}px * var(--ui-scale, 1))"
    ring_css = f"calc({ring_px}px * var(--ui-scale, 1))"
    font_css = f"calc({font_px}px * var(--ui-scale, 1))"

    # ✅ “TV-friendly”: prioriza rosto e evita artefatos feios em downscale
    img_style = (
        "width:100%;height:100%;object-fit:cover;"
        "object-position:50% 18%;"  # sobe um pouco (rosto)
        "transform:translateZ(0);"  # ajuda compositor
    )

    if src:
        ini_js = ini.replace("'", "\\'")
        return f"""
        <div class="rounded-full overflow-hidden flex items-center justify-center bg-zinc-100"
             style="width:{size_css};height:{size_css}; border:{ring_css} solid #F05914;"
             title="{safe_title}">
          <img src="{html.escape(src)}"
               alt="{safe_title}"
               style="{img_style}"
               onerror="this.remove(); this.parentElement.className='rounded-full overflow-hidden flex items-center justify-center bg-zinc-900 text-white font-extrabold'; this.parentElement.style.fontSize='{font_css}'; this.parentElement.innerText='{ini_js}';" />
        </div>
        """

    return f"""
    <div class="rounded-full overflow-hidden flex items-center justify-center bg-zinc-900 text-white font-extrabold"
         style="width:{size_css};height:{size_css}; font-size:{font_css}; border:{ring_css} solid #F05914;"
         title="{safe_title}">
      {ini}
    </div>
    """

