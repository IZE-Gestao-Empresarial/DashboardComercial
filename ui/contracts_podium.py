from __future__ import annotations

import html

from core.formatters import fmt_int, fmt_money
from core.people import PHOTO_FILES
from ui.embed import file_to_data_uri
from ui.ranklist import ranklist_card_html


def _ico_doc() -> str:
    return '''
    <svg viewBox="0 0 64 64">
      <path fill="#2F80ED" d="M14 6h24l12 12v40a4 4 0 0 1-4 4H14a4 4 0 0 1-4-4V10a4 4 0 0 1 4-4z"/>
      <path fill="#fff" opacity=".95" d="M38 6v12a4 4 0 0 0 4 4h12"/>
      <path fill="#EAF3FF" d="M18 30h28v4H18zM18 40h28v4H18zM18 50h22v4H18z"/>
    </svg>
    '''


def _ico_handshake() -> str:
    return '''
    <svg viewBox="0 0 64 64">
      <path fill="#1F8A70" d="M8 24l14-8 10 10-10 10L8 26z"/>
      <path fill="#2ECC71" d="M56 24L42 16 32 26l10 10 14-10z"/>
      <path fill="#F5CBA7" d="M20 36l10-10c2-2 6-2 8 0l6 6c2 2 2 6 0 8l-4 4c-2 2-6 2-8 0l-4-4-2 2c-2-2-6-2-8 0l-2-2c-2-2-2-4 0-6z"/>
      <path fill="#E8B894" d="M28 44l-6-6 3-3 6 6z"/>
    </svg>
    '''


def _ico_moneybag() -> str:
    return '''
    <svg viewBox="0 0 64 64">
      <path fill="#2ECC71" d="M22 10c4 4 16 4 20 0l6 8-10 6H26L16 18z"/>
      <path fill="#27AE60" d="M22 24h20c8 8 10 14 10 22 0 12-10 18-20 18H32C22 64 12 58 12 46c0-8 2-14 10-22z"/>
      <circle cx="32" cy="46" r="10" fill="#1E874B" opacity=".35"/>
      <path fill="#F2F2F2" d="M28 50c0 2 2 4 6 4 3 0 6-2 6-5 0-3-3-4-6-4-3 0-6-1-6-4 0-3 3-5 6-5 4 0 6 2 6 4h-2c0-1-2-2-4-2-2 0-4 1-4 3 0 2 2 2 5 3 4 1 7 2 7 6 0 4-4 7-8 7-5 0-8-3-8-7z"/>
    </svg>
    '''


def _photo_src(name_upper: str) -> str | None:
    """Data URI (base64) a partir da foto local da pessoa."""
    key = (name_upper or "").strip().upper()
    p = PHOTO_FILES.get(key)
    if not p:
        return None
    return file_to_data_uri(p)


def _rank_card_html(
    *,
    rank_text: str,
    scale: str,
    contratos: float | None,
    fat_assinado: float | None,
    fat_pago: float | None,
    photo_src: str | None,
) -> str:
    contratos_v = fmt_int(contratos)
    fa_v = fmt_money(fat_assinado)
    fp_v = fmt_money(fat_pago)

    photo_html = (
        f'<img src="{html.escape(photo_src)}" alt="" style="width:100%;height:100%;object-fit:cover;" />'
        if photo_src
        else '<div class="avatar-placeholder"></div>'
    )

    return f'''
      <article class="rank-card" style="--scale: {scale};">
          <div class="avatar-ring">
            {photo_html}
        </div>

        <div class="info-panel">
          <div class="panel-title">Contratos Assinados</div>

          <div class="panel-body">
            <div class="row">
              <div class="ico" aria-hidden="true">{_ico_doc()}</div>
              <div class="label">Contratos Assinados</div>
              <div class="value">{contratos_v}</div>
            </div>

            <div class="divider"></div>

            <div class="row">
              <div class="ico" aria-hidden="true">{_ico_handshake()}</div>
              <div class="label">Fat. Assinado</div>
              <div class="value">{fa_v}</div>
            </div>

            <div class="divider"></div>

            <div class="row">
              <div class="ico" aria-hidden="true">{_ico_moneybag()}</div>
              <div class="label">Fat. Pago</div>
              <div class="value">{fp_v}</div>
            </div>
          </div>
        </div>
      </article>
    '''


def podium_contracts_card_html(rows: list[dict]) -> str:
    """Card de ranking por pessoa.

    A colocação é definida SOMENTE por FATURAMENTO PAGO (desc).
    """
    if not rows:
        return '''
        <div class="bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full flex items-center justify-center">
          <div class="text-zinc-500 font-semibold">Sem dados</div>
        </div>
        '''

    def _k(r: dict) -> float:
        v = r.get("fat_pago")
        try:
            return float(v) if v is not None else 0.0
        except Exception:
            return 0.0

    ordered = sorted(rows, key=_k, reverse=True)
    top = ordered[:5]

    def _value(it: dict) -> str:
        fp = fmt_money(it.get("fat_pago"))
        fp_txt = f"R$ {fp}" if fp != "-" else "-"
        return f"Fat. Pago: {fp_txt}"

    def _sub(it: dict) -> str:
        c = fmt_int(it.get("contratos"))
        fa = fmt_money(it.get("fat_assinado"))
        fa_txt = f"R$ {fa}" if fa != "-" else "-"
        # ✅ ponto de quebra “inteligente” após o bullet
        return f"Contratos: {c} •\u200b Fat. Ass.: {fa_txt}"

    return ranklist_card_html(
        title="Contratos Assinados por pessoa",
        items=top,
        value_fn=_value,
        sub_fn=_sub,
        empty_text="Sem dados",
        avatar_size_px=70,
    )
