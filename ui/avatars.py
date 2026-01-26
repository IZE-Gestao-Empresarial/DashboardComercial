from __future__ import annotations

import html
import base64
from pathlib import Path
import mimetypes

from core.people import PHOTO_FILES, PHOTO_URLS, pretty_name


# cache simples para não re-ler o arquivo toda hora
_FILE_DATAURI_CACHE: dict[str, str] = {}


def initials(name_upper: str) -> str:
    parts = [p for p in (name_upper or "").strip().split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def _file_to_data_uri(rel_path: str) -> str | None:
    if not rel_path:
        return None
    if rel_path in _FILE_DATAURI_CACHE:
        return _FILE_DATAURI_CACHE[rel_path]

    p = Path(rel_path)
    if not p.exists():
        return None

    mime, _ = mimetypes.guess_type(str(p))
    mime = mime or "image/png"

    data = p.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    uri = f"data:{mime};base64,{b64}"
    _FILE_DATAURI_CACHE[rel_path] = uri
    return uri


def photo_src(name_upper: str) -> str | None:
    """Retorna src para <img>: primeiro arquivo local, depois URL."""
    key = (name_upper or "").strip().upper()
    url = PHOTO_URLS.get(key)
    if url:
        return url
    return None


def avatar_html(name_upper: str, size_px: int = 44, ring_px: int = 2) -> str:
    """Avatar redondo com borda laranja. Se não tiver foto, usa iniciais."""
    key = (name_upper or "").strip().upper()
    src = photo_src(key)
    safe_title = html.escape(pretty_name(key))

    if src:
        return f'''
        <div class="rounded-full overflow-hidden flex items-center justify-center bg-zinc-100"
             style="width:{size_px}px;height:{size_px}px; box-shadow: 0 6px 16px rgba(0,0,0,0.12); border:{ring_px}px solid #F05914;"
             title="{safe_title}">
          <img src="{html.escape(src)}" alt="{safe_title}" class="w-full h-full object-cover" />
        </div>
        '''
    ini = html.escape(initials(key))
    font_px = max(12, int(size_px * 0.35))
    return f'''
    <div class="rounded-full overflow-hidden flex items-center justify-center bg-zinc-900 text-white font-extrabold"
         style="width:{size_px}px;height:{size_px}px; font-size:{font_px}px; border:{ring_px}px solid #F05914; box-shadow: 0 6px 16px rgba(0,0,0,0.12);"
         title="{safe_title}">
      {ini}
    </div>
    '''
