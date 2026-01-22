from __future__ import annotations

from pathlib import Path
import re
import streamlit as st


_BASE_DIR = Path(__file__).resolve().parent.parent


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@st.cache_data(show_spinner=False)
def load_asset_text(rel_path: str) -> str:
    """
    Lê arquivo texto do projeto (assets/templates) e cacheia.
    rel_path: 'assets/arquivo.css' ou 'templates/arquivo.html'
    """
    path = _BASE_DIR / rel_path
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    return _read_text(path)


def inject_kiosk_css() -> None:
    """CSS que atua no DOM do Streamlit (fora do iframe)."""
    css = load_asset_text("assets/kiosk.css")
    st.markdown(f"<style>\n{css}\n</style>", unsafe_allow_html=True)


def render_dashboard(slots: dict[str, str]) -> str:
    """
    Monta o HTML final do iframe substituindo tokens do template.
    """
    template = load_asset_text("templates/dashboard.html")
    css = load_asset_text("assets/dashboard.css")

    html = template.replace("__DASHBOARD_CSS__", css)

    for key, value in slots.items():
        html = html.replace(f"__{key}__", value)

    # Se sobrar algum token não preenchido, remove
    html = re.sub(r"__[^_]+__", "", html)
    return html
