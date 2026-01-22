from __future__ import annotations

import html

from core.people import PHOTO_URLS, pretty_name


def initials(name_upper: str) -> str:
    parts = [p for p in (name_upper or "").strip().split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def avatar_html(name_upper: str, size_px: int = 44) -> str:
    """Avatar redondo com borda laranja. Se não tiver foto, usa iniciais."""
    key = (name_upper or "").strip().upper()
    url = PHOTO_URLS.get(key)
    safe_title = html.escape(pretty_name(key))

    if url:
        return f'''
        <div class="rounded-full ring-2 ring-[#F05914] overflow-hidden flex items-center justify-center bg-zinc-100"
             style="width:{size_px}px;height:{size_px}px;" title="{safe_title}">
          <img src="{html.escape(url)}" alt="{safe_title}" class="w-full h-full object-cover" />
        </div>
        '''
    ini = html.escape(initials(key))
    font_px = max(12, int(size_px * 0.35))
    return f'''
    <div class="rounded-full ring-2 ring-[#F05914] overflow-hidden flex items-center justify-center bg-zinc-900 text-white font-extrabold"
         style="width:{size_px}px;height:{size_px}px; font-size:{font_px}px;" title="{safe_title}">
      {ini}
    </div>
    '''
