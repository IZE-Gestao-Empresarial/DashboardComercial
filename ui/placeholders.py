def placeholder_card_html(title_html: str) -> str:
    """
    Card placeholder (mesmo visual dos cards) para você ir preenchendo depois.
    title_html pode conter <br/> para quebra de linha.
    """
    return f"""
    <div class="bg-white rounded-3xl shadow-sm border border-zinc-100 h-full w-full flex items-center justify-center">
      <div class="px-8 text-center font-extrabold text-zinc-900 leading-tight"
           style="font-size: var(--fs-placeholder);">
        {title_html}
      </div>
    </div>
    """
