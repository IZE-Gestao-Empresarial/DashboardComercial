import requests
import streamlit as st
import streamlit.components.v1 as components
import re
_CLEAN_INVISIBLE_RE = re.compile(r"[\u200B-\u200F\uFEFF\u00AD]")
from streamlit_autorefresh import st_autorefresh

from core.constants import CACHE_TTL_SECONDS, REFRESH_MS, INDICATORS
from core.data import _CLEAN_INVISIBLE_RE, fetch_payload, payload_to_df, latest_values, get_val
from core.metrics import (
    total_for_indicator,
    people_values,
    shares_from_values,
    top_n_with_others,
    to_percent_value,
)
from core.formatters import fmt_int, fmt_money, pct_to_float_percent, pill_text_from_ratio

from ui.cards import kpi_card_html
from ui.simple_kpis import simple_total_card_html
from ui.conversions import conversion_general_card_html, conversion_people_card_html
from ui.rings import reuniões_por_pessoa_card_html
from ui.contracts_podium import podium_contracts_card_html
from ui.render import inject_kiosk_css, render_dashboard


# =========================
# Config
# =========================
st.set_page_config(page_title="Comercial | Indicadores", layout="wide")

# ✅ Kiosk mode: sem scroll + centralizado
inject_kiosk_css()

# Auto refresh (TV)
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
# 1) Reuniões (SDR) / Faturamento (CLOSER)
# =========================
reun_real = get_val(df_last, INDICATORS.REUNIOES_REAL, "SDR")
reun_meta = get_val(df_last, INDICATORS.REUNIOES_META, "SDR")
reun_perc = get_val(df_last, INDICATORS.REUNIOES_PERC, "SDR")

fat_real = get_val(df_last, INDICATORS.FAT_REAL, "CLOSER")
if fat_real is None:
    fat_real = get_val(df_last, INDICATORS.FAT_FALLBACK_REAL, "CLOSER")
fat_meta = get_val(df_last, INDICATORS.FAT_META, "CLOSER")
fat_perc = get_val(df_last, INDICATORS.FAT_PERC, "CLOSER")

card_reunioes = kpi_card_html(
    title="Reuniões",
    percent_float=pct_to_float_percent(reun_perc),
    subtitle="Reuniões Ocorridas",
    left_label="Reuniões Realizadas",
    left_value=fmt_int(reun_real),
    left_badge="Atual",
    mid_label="Meta de Reuniões",
    mid_value=fmt_int(reun_meta),
    right_pill=pill_text_from_ratio(reun_perc),
)

card_faturamento = kpi_card_html(
    title="Faturamento",
    percent_float=pct_to_float_percent(fat_perc),
    subtitle="Faturamento alcançado",
    left_label="Faturamento Pago",
    left_value=fmt_money(fat_real),
    left_badge="Atual",
    mid_label="Meta de Faturamento",
    mid_value=fmt_money(fat_meta),
    right_pill=pill_text_from_ratio(fat_perc),
)

# =========================
# 2) Leads Criados (total)
# =========================
leads_total = total_for_indicator(df_last, INDICATORS.LEADS_CRIADOS, prefer_responsavel="SDR")
card_leads = simple_total_card_html("Leads Criados", leads_total, subtitle="Total no período")

# =========================
# 3) Taxa de Conversão (Geral) [Responsável: SDR]
# =========================
taxa_geral_raw = get_val(df_last, INDICATORS.TAXA_CONVERSAO, "SDR")
taxa_geral = to_percent_value(taxa_geral_raw)
card_taxa_geral = conversion_general_card_html("Taxa de Conversão (Geral)", taxa_geral)

# =========================
# 4) Taxa de conversão por pessoa [Responsável != SDR]
# =========================
taxa_people_raw = people_values(df_last, INDICATORS.TAXA_CONVERSAO, exclude_responsaveis=["SDR"])

def _is_team_label(name: str) -> bool:


    n = _CLEAN_INVISIBLE_RE.sub("", (name or "")).replace("\u00A0", " ")
    n = " ".join(n.split()).strip().upper()

    if not n:
        return True
    team_labels = {
        "SDR",
        "EQUIPE",
        "TIME",
        "EQUIPE SDR",
        "TIME SDR",
        "SDR (EQUIPE)",
    }
    if n in team_labels:
        return True
    # variações comuns: "SDR - ...", "... - SDR" etc.
    if n.startswith("SDR ") or n.startswith("SDR-"):
        return True
    if n.endswith(" SDR") or n.endswith("-SDR"):
        return True
    return False

taxa_people = [
    {"name": x["name"], "percent": to_percent_value(x["value"])}
    for x in taxa_people_raw
    if not _is_team_label(x.get("name", ""))
]
taxa_people.sort(key=lambda x: x["percent"], reverse=True)
taxa_people = taxa_people[:5]  # básico: top 5
card_taxa_pessoa = conversion_people_card_html("Taxa de conversão por pessoa", taxa_people)

# =========================
# 5) Reuniões por pessoa (share) [Indicador: REUNIÕES OCORRIDAS]
# =========================
reun_people_vals = people_values(
    df_last,
    INDICATORS.REUNIOES_REAL,
    exclude_responsaveis=["SDR", "SDR", "CLOSER"],
)
reun_shares = shares_from_values(reun_people_vals)
reun_shares = top_n_with_others(reun_shares, n=4, others_label="OUTROS")
card_reunioes_pessoa = reuniões_por_pessoa_card_html("Reuniões por pessoa", reun_shares)

# =========================
# 6) Contratos + Faturamento por pessoa
#     - Indicadores: CONTRATOS ASSINADOS / FATURAMENTO ASSINADO / FATURAMENTO PAGO
# =========================
contratos_vals = people_values(df_last, INDICATORS.CONTRATOS_ASSINADOS, exclude_responsaveis=["CLOSER"])
fat_ass_vals = people_values(df_last, INDICATORS.FATURAMENTO_ASSINADO, exclude_responsaveis=["CLOSER"])
fat_pago_vals = people_values(df_last, INDICATORS.FATURAMENTO_PAGO, exclude_responsaveis=["CLOSER"])

m_contr = {x["name"]: x["value"] for x in contratos_vals}
m_fa = {x["name"]: x["value"] for x in fat_ass_vals}
m_fp = {x["name"]: x["value"] for x in fat_pago_vals}

rows = []
for name in sorted(set(m_contr) | set(m_fa) | set(m_fp)):
    if name.strip().upper() == "CLOSER":
        continue
    # entra se tiver FATURAMENTO PAGO (ordenação do pódio)
    if name in m_fp:
        rows.append(
            {
                "name": name,
                "contratos": m_contr.get(name),
                "fat_assinado": m_fa.get(name),
                "fat_pago": m_fp.get(name),
            }
        )

rows.sort(key=lambda r: float(r.get("fat_pago") or 0.0), reverse=True)
rows = rows[:5]  # top 5 (ordem por Fat. Pago)
card_contratos_pessoa = podium_contracts_card_html(rows)

# =========================
# Render
# =========================
slots = {
    "CARD_REUNIOES": card_reunioes,
    "CARD_LEADS": card_leads,
    "CARD_TAXA_GERAL": card_taxa_geral,
    "CARD_REUNIOES_PESSOA": card_reunioes_pessoa,
    "CARD_FATURAMENTO": card_faturamento,
    "CARD_TAXA_PESSOA": card_taxa_pessoa,
    "CARD_CONTRATOS_PESSOA": card_contratos_pessoa,
}

html = render_dashboard(slots=slots)

# ✅ height mínimo; o CSS do kiosk fixa o iframe em 100vh/100vw
components.html(html, height=1, scrolling=False)
