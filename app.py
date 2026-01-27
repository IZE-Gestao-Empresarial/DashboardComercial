import requests
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

from core.constants import CACHE_TTL_SECONDS, REFRESH_MS, INDICATORS
from core.data import fetch_payload, payload_to_df, latest_values, get_val
from core.metrics import total_for_indicator, people_values, to_percent_value
from core.formatters import fmt_int, fmt_money, pct_to_float_percent, pill_text_from_ratio

from ui.cards import kpi_card_html
from ui.leads_conversion import leads_conversion_card_html
from ui.ranklist import ranklist_card_html, fmt_percent_br
from ui.contracts_podium import podium_contracts_card_html
from ui.fat_ass_pago import faturamento_ass_pago_card_html
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
# 1) KPI: Reuniões (SDR) / Faturamento (CLOSER)
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
    title="Reuniões Meta x Realizado",
    percent_float=pct_to_float_percent(reun_perc),
    subtitle="Reuniões ocorridas",
    left_label="Reuniões Realizadas",
    left_value=fmt_int(reun_real),
    left_badge="Atual",
    mid_label="Meta de Reuniões",
    mid_value=fmt_int(reun_meta),
    right_pill=pill_text_from_ratio(reun_perc),
)

card_faturamento = kpi_card_html(
    title="Faturamento Meta x Realizado",
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
# 2) Leads + Taxa de Conversão (Geral)
#    (observação do usuário: NÃO teremos mais o card "taxa de conversão por pessoa")
# =========================
leads_total = total_for_indicator(df_last, INDICATORS.LEADS_CRIADOS, prefer_responsavel="SDR")

taxa_geral_raw = get_val(df_last, INDICATORS.TAXA_CONVERSAO, "SDR")
taxa_geral = to_percent_value(taxa_geral_raw)

card_leads_taxa = leads_conversion_card_html(
    leads_total=leads_total,
    taxa_conversao=taxa_geral,
    title="Leads | Taxa de Conversão (Geral)",
)


# =========================
# 3) Ranking SDR (por Reuniões)
# =========================

def _is_team_label(name: str) -> bool:
    n = (name or "").replace("\u00A0", " ")
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
    if n.startswith("SDR ") or n.startswith("SDR-"):
        return True
    if n.endswith(" SDR") or n.endswith("-SDR"):
        return True
    return False


reun_people_vals = people_values(
    df_last,
    INDICATORS.REUNIOES_REAL,
    exclude_responsaveis=["SDR", "CLOSER"],
)

# remove labels de equipe
reun_people_vals = [x for x in reun_people_vals if not _is_team_label(x.get("name", ""))]

# ordena por número de reuniões
reun_people_vals.sort(key=lambda x: float(x.get("value") or 0.0), reverse=True)

_total_reun = sum(float(x.get("value") or 0.0) for x in reun_people_vals) or 0.0
_top_reun = reun_people_vals[:5]

rank_sdr_items = []
for it in _top_reun:
    v = float(it.get("value") or 0.0)
    share = (v / _total_reun * 100.0) if _total_reun > 0 else 0.0
    rank_sdr_items.append({"name": it.get("name"), "value": v, "share": share})

card_ranking_sdr = ranklist_card_html(
    title="Ranking SDR",
    items=rank_sdr_items,
    value_fn=lambda r: f"{fmt_int(r.get('value'))} reuniões",
    sub_fn=lambda r: f"{fmt_percent_br(r.get('share', 0.0))} do total",
    empty_text="Sem dados",
    avatar_size_px=50,
)


# =========================
# 4) Ranking Closer (por Faturamento Pago)
# =========================
contratos_vals = people_values(df_last, INDICATORS.CONTRATOS_ASSINADOS, exclude_responsaveis=["CLOSER"])
fat_ass_vals = people_values(df_last, INDICATORS.FATURAMENTO_ASSINADO, exclude_responsaveis=["CLOSER"])
fat_pago_vals = people_values(df_last, INDICATORS.FATURAMENTO_PAGO, exclude_responsaveis=["CLOSER"])

m_contr = {x["name"]: x["value"] for x in contratos_vals}
m_fa = {x["name"]: x["value"] for x in fat_ass_vals}
m_fp = {x["name"]: x["value"] for x in fat_pago_vals}

rows_closer = []
for name in sorted(set(m_contr) | set(m_fa) | set(m_fp)):
    if (name or "").strip().upper() == "CLOSER":
        continue
    if name in m_fp:  # só entra se tiver Fat. Pago (usado como ordenação)
        rows_closer.append(
            {
                "name": name,
                "contratos": m_contr.get(name),
                "fat_assinado": m_fa.get(name),
                "fat_pago": m_fp.get(name),
            }
        )

rows_closer.sort(key=lambda r: float(r.get("fat_pago") or 0.0), reverse=True)
rows_closer = rows_closer[:5]

card_ranking_closer = podium_contracts_card_html(rows_closer, title="Ranking Closer")


# =========================
# 5) Faturamento assinado x pago (CLOSER)
# =========================

def _daily_series_values(df_full, indicador: str, responsavel: str, limit: int = 24) -> dict[str, float]:
    if df_full is None or df_full.empty:
        return {}
    if "DATA_ATUALIZAÇÃO" not in df_full.columns:
        return {}

    ind = (indicador or "").strip().upper()
    resp = (responsavel or "").strip().upper()

    d = df_full[(df_full["INDICADORES"] == ind) & (df_full["RESPONSÁVEL"] == resp)].copy()
    if d.empty:
        return {}

    d = d.dropna(subset=["DATA_ATUALIZAÇÃO", "VALOR"]).sort_values("DATA_ATUALIZAÇÃO")

    # consolida por dia pegando o último valor do dia
    d["DIA"] = d["DATA_ATUALIZAÇÃO"].dt.date.astype(str)
    d = d.groupby("DIA", as_index=False)["VALOR"].last()

    # pega somente o final (mais recente)
    tail = d.tail(limit)
    out = {}
    for _, row in tail.iterrows():
        try:
            out[str(row["DIA"])] = float(row["VALOR"] or 0.0)
        except Exception:
            out[str(row["DIA"])] = 0.0
    return out


ass_map = _daily_series_values(df, INDICATORS.FATURAMENTO_ASSINADO, "CLOSER", limit=30)
pago_map = _daily_series_values(df, INDICATORS.FATURAMENTO_PAGO, "CLOSER", limit=30)

dates = sorted(set(ass_map.keys()) | set(pago_map.keys()))

area_vals: list[float] = []
line_vals: list[float] = []

if len(dates) >= 2:
    last_a = None
    last_p = None

    for dt in dates:
        if dt in ass_map:
            last_a = ass_map[dt]
        if dt in pago_map:
            last_p = pago_map[dt]

        # forward-fill simples
        area_vals.append(float(last_a or 0.0))
        line_vals.append(float(last_p or 0.0))

    # mantém um tamanho enxuto (pra caber bem no card)
    area_vals = area_vals[-24:]
    line_vals = line_vals[-24:]


total_ass = get_val(df_last, INDICATORS.FATURAMENTO_ASSINADO, "CLOSER")
total_pago = get_val(df_last, INDICATORS.FATURAMENTO_PAGO, "CLOSER")

card_fat_ass_pago = faturamento_ass_pago_card_html(
    title="Faturamento ass x pago",
    total_assinado=total_ass,
    total_pago=total_pago,
    assinado_series=area_vals,
    pago_series=line_vals,
)


# =========================
# Render (layout conforme estrutura.png)
# =========================
slots = {
    "CARD_REUNIOES": card_reunioes,
    "CARD_RANKING_SDR": card_ranking_sdr,
    "CARD_FATURAMENTO": card_faturamento,
    "CARD_LEADS_TAXA": card_leads_taxa,
    "CARD_RANKING_CLOSER": card_ranking_closer,
    "CARD_FAT_ASS_PAGO": card_fat_ass_pago,
}

html = render_dashboard(slots=slots)

# ✅ height mínimo; o CSS do kiosk fixa o iframe em 100vh/100vw
components.html(html, height=1, scrolling=False)
