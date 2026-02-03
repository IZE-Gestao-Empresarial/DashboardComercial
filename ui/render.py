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
    Lê arquivo texto do projeto e cacheia.
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


def _try_load(rel_path: str) -> str:
    """Carrega asset se existir, senão retorna string vazia (não quebra o app)."""
    try:
        return load_asset_text(rel_path)
    except FileNotFoundError:
        return ""
    except Exception:
        return ""


def render_dashboard(slots: dict[str, str]) -> str:
    """
    Monta o HTML final do iframe substituindo tokens do template.
    - Injeta CSS do dashboard + ranklist (se existir) no __DASHBOARD_CSS__
    """
    template = load_asset_text("templates/dashboard.html")

    dashboard_css = load_asset_text("assets/dashboard.css")
    ranklist_css = _try_load("assets/ranklist.css")  # <-- CSS separado do ranking

    css_final = dashboard_css
    if ranklist_css.strip():
        css_final = f"{dashboard_css}\n\n/* ===== Ranklist CSS (assets/ranklist.css) ===== */\n{ranklist_css}\n"

    html_out = template.replace("__DASHBOARD_CSS__", css_final)

    for key, value in slots.items():
        html_out = html_out.replace(f"__{key}__", value)

    html_out = re.sub(r"__[^_]+__", "", html_out)
    return html_out
