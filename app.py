# app.py
import requests
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

from core.constants import CACHE_TTL_SECONDS, REFRESH_MS, INDICATORS
from core.data import fetch_payload, payload_to_df, latest_values, get_val
from core.formatters import fmt_int, fmt_money, pct_to_float_percent, pill_text_from_ratio
from ui.cards import kpi_card_html
from ui.render import inject_kiosk_css, render_dashboard


# =========================
# Config
# =========================
st.set_page_config(page_title="Comercial | Indicadores", layout="wide")

# ✅ Kiosk mode: sem scroll + centralizado (CSS em /assets/kiosk.css)
inject_kiosk_css()

# Auto refresh (mantém a página viva na TV)
st_autorefresh(interval=REFRESH_MS, key="auto_refresh_main")

# Secrets
URL = st.secrets.get("SHEETS_WEBAPP_URL", "")
TOKEN = st.secrets.get("SHEETS_WEBAPP_TOKEN", "")

if not (URL and TOKEN):
    st.error("Defina SHEETS_WEBAPP_URL e SHEETS_WEBAPP_TOKEN em .streamlit/secrets.toml")
    st.stop()

# =========================
# Data
# =========================
try:
    payload = fetch_payload(URL, TOKEN, ttl_seconds=CACHE_TTL_SECONDS)
except requests.HTTPError as e:
    st.error(f"Erro HTTP ao buscar dados: {e}")
    st.stop()
except Exception as e:
    st.error(f"Erro ao buscar dados: {e}")
    st.stop()

if "error" in payload and "rows" not in payload:
    st.error(f"Endpoint retornou erro: {payload}")
    st.stop()

df, updated_at, sheet = payload_to_df(payload)
df_last = latest_values(df)

# =========================
# KPIs
# =========================
# SDR
reun_real = get_val(df_last, INDICATORS.REUNIOES_REAL, "SDR")
reun_meta = get_val(df_last, INDICATORS.REUNIOES_META, "SDR")
reun_perc = get_val(df_last, INDICATORS.REUNIOES_PERC, "SDR")
reun_dif  = get_val(df_last, INDICATORS.REUNIOES_DIF,  "SDR")

# CLOSER
fat_real = get_val(df_last, INDICATORS.FAT_REAL, "CLOSER")
if fat_real is None:
    fat_real = get_val(df_last, INDICATORS.FAT_FALLBACK_REAL, "CLOSER")
fat_meta = get_val(df_last, INDICATORS.FAT_META, "CLOSER")
fat_perc = get_val(df_last, INDICATORS.FAT_PERC, "CLOSER")
fat_dif  = get_val(df_last, INDICATORS.FAT_DIF,  "CLOSER")

badge_reun = "Atual"
badge_fat = "Atual"

card1 = kpi_card_html(
    title="Reuniões",
    percent_float=pct_to_float_percent(reun_perc),
    subtitle="Reuniões Ocorridas",
    left_label="Reuniões<br/>Realizadas",
    left_value=fmt_int(reun_real),
    left_badge=badge_reun,
    mid_label="Meta de<br/>Reuniões",
    mid_value=fmt_int(reun_meta),
    right_pill=pill_text_from_ratio(reun_perc),
)

card2 = kpi_card_html(
    title="Faturamento",
    percent_float=pct_to_float_percent(fat_perc),
    subtitle="Faturamento alcançado",
    left_label="Faturamento<br/>Pago",
    left_value=fmt_money(fat_real),
    left_badge=badge_fat,
    mid_label="Meta de<br/>Faturamento",
    mid_value=fmt_money(fat_meta),
    right_pill=pill_text_from_ratio(fat_perc),
)

# Render final (HTML + CSS em arquivos /templates e /assets)
html = render_dashboard(cards_html=card1 + card2)

# ✅ Ajuste da altura: use 1080 para 1080p; se sua TV for 4K, pode colocar 2160.
components.html(html, height=1080, scrolling=False)
