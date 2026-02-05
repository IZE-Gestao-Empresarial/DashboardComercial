import requests
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
import re

from core.constants import CACHE_TTL_SECONDS, REFRESH_MS, INDICATORS
from core.data import fetch_payload, payload_to_df, latest_values, get_val
from core.metrics import total_for_indicator, people_values, to_percent_value
from core.formatters import fmt_int, fmt_money, pct_to_float_percent, fmt_money_no_cents

from ui.cards import kpi_card_html
from ui.leads_conversion import leads_conversion_card_html
from ui.ranklist import ranking_sdr_card_html
from ui.contracts_podium import podium_contracts_card_html
from ui.funil_vendas import funil_vendas_card_html
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
reun_crescimento = get_val(df_last, INDICATORS.REUNIOES_CRESC, "SDR")
reun_dif = (reun_real - reun_meta) if (reun_real is not None and reun_meta is not None) else None

# ✅ No seu payload existem "FATURAMENTO ASSINADO" e "FATURAMENTO PAGO".
# Antes você estava usando INDICATORS.FAT_REAL (= "FATURAMENTO PAGO") no campo "Assinado".
fat_assinado = total_for_indicator(df_last, INDICATORS.FATURAMENTO_ASSINADO, prefer_responsavel="CLOSER")
if fat_assinado is None:
    # fallback: se não existir o total do time, soma os closers individuais
    fat_assinado = total_for_indicator(df_last, INDICATORS.FATURAMENTO_ASSINADO, exclude_responsaveis=["CLOSER"])

fat_pago = total_for_indicator(df_last, INDICATORS.FATURAMENTO_PAGO, prefer_responsavel="CLOSER")
if fat_pago is None:
    # fallback: se não existir o total do time, soma os closers individuais
    fat_pago = total_for_indicator(df_last, INDICATORS.FATURAMENTO_PAGO, exclude_responsaveis=["CLOSER"])

fat_meta = get_val(df_last, INDICATORS.FAT_META, "CLOSER")
fat_perc = get_val(df_last, INDICATORS.FAT_PERC, "CLOSER")
fat_cresc = get_val(df_last, INDICATORS.FAT_CRESC, "CLOSER")
fat_dif = (fat_assinado - fat_meta) if (fat_assinado is not None and fat_meta is not None) else None
card_reunioes = kpi_card_html(
    title="Reuniões Ocorridas",
    percent_float=pct_to_float_percent(reun_perc),
    subtitle="Progresso",
    left_label="Número de Reuniões",
    left_value=fmt_int(reun_real),
    left_badge=pct_to_float_percent(reun_crescimento),          # teste badge alto
    mid_label="Meta de Reuniões",
    mid_value=fmt_int(reun_meta),
    right_pill=fmt_int(reun_dif) if reun_dif is not None else "0",          # teste badge alto no direito
)

card_faturamento = kpi_card_html(
    title="Faturamento",
    percent_float=pct_to_float_percent(fat_perc),
    subtitle="Progresso",
    left_label="Faturamento Assinado",
    left_value=fmt_money_no_cents(fat_assinado),         # ✅ Mudou aqui
    left_badge=pct_to_float_percent(fat_cresc),
    mid_label="Meta de Faturamento",
    mid_value=fmt_money_no_cents(fat_meta),              # ✅ Mudou aqui
    right_pill=fmt_int(fat_dif),              # ✅ Mudou aqui (era fmt_int)
)


# =========================
# 2) Leads + Taxa de Conversão (Geral)
# =========================
leads_total = total_for_indicator(df_last, INDICATORS.LEADS_CRIADOS, prefer_responsavel="SDR")

taxa_geral_raw = get_val(df_last, INDICATORS.TAXA_CONVERSAO, "SDR")

card_leads_taxa = leads_conversion_card_html(
    leads_total=leads_total,
    taxa_conversao=taxa_geral_raw,
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

card_ranking_sdr = ranking_sdr_card_html(
    title="Ranking SDR",
    items=[{"name": r.get("name"), "reunioes": r.get("value"), "conversao": r.get("share")} for r in rank_sdr_items],
    limit=2,
    avatar_size_px=56,
)


# =========================
# 4) Ranking Closer (por Faturamento Pago)
# =========================
def _to_float_moneyish(v) -> float:
    """Converte números/strings (incluindo '98.874,00', 'R$ 98.874,00', etc.) para float."""
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        try:
            return float(v)
        except Exception:
            return 0.0

    s = str(v).strip()
    if not s or s == "-":
        return 0.0

    # pega o primeiro bloco numérico relevante
    m = re.search(r"-?[\d\.,]+", s.replace("R$", "").strip())
    if not m:
        return 0.0

    num = m.group(0)

    # heurística BR: se tiver '.' e ',' => '.' milhar, ',' decimal
    if "." in num and "," in num:
        num = num.replace(".", "").replace(",", ".")
    elif "," in num and "." not in num:
        num = num.replace(",", ".")
    else:
        # se tiver vários '.', tende a ser milhar
        if num.count(".") > 1:
            num = num.replace(".", "")

    try:
        return float(num)
    except Exception:
        return 0.0


contratos_vals = people_values(df_last, INDICATORS.CONTRATOS_ASSINADOS, exclude_responsaveis=["CLOSER"])
fat_ass_vals = people_values(df_last, INDICATORS.FATURAMENTO_ASSINADO, exclude_responsaveis=["CLOSER"])
fat_pago_vals = people_values(df_last, INDICATORS.FATURAMENTO_PAGO, exclude_responsaveis=["CLOSER"])

m_contr = {x["name"]: x["value"] for x in contratos_vals}
m_fa = {x["name"]: x["value"] for x in fat_ass_vals}
m_fp = {x["name"]: x["value"] for x in fat_pago_vals}

# nomes que entram no ranking (tem Fat. Pago)
names_in_rank = []
for name in sorted(set(m_contr) | set(m_fa) | set(m_fp)):
    if (name or "").strip().upper() == "CLOSER":
        continue
    if name in m_fp:
        names_in_rank.append(name)

# ✅ % baseada no faturamento assinado (participação do closer no total assinado do ranking)
_total_fa = sum(_to_float_moneyish(m_fa.get(n)) for n in names_in_rank) or 0.0

rows_closer = []
for name in names_in_rank:
    fa_num = _to_float_moneyish(m_fa.get(name))
    pct_fa_share = (fa_num / _total_fa * 100.0) if _total_fa > 0 else 0.0

    rows_closer.append(
        {
            "name": name,
            "contratos": m_contr.get(name),
            "fat_assinado": m_fa.get(name),
            "fat_pago": m_fp.get(name),
            "pct": pct_fa_share,  # <- vai aparecer abaixo de "X contratos"
        }
    )

rows_closer.sort(key=lambda r: float(_to_float_moneyish(r.get("fat_pago")) or 0.0), reverse=True)
rows_closer = rows_closer[:5]

card_ranking_closer = podium_contracts_card_html(rows_closer, title="Ranking Closer")


# =========================
# 5) Funil de vendas (NOVO)
# =========================
# Totais:
# - Leads: já calculado (leads_total)
# - Reuniões: usa o total do KPI (reun_real)
# - Contratos: tenta pegar o total do time (CLOSER); se não existir, soma valores individuais
contratos_total = get_val(df_last, INDICATORS.CONTRATOS_ASSINADOS, "CLOSER")
if contratos_total is None:
    contratos_total = sum(float(x.get("value") or 0.0) for x in contratos_vals) or 0.0

card_funil_vendas = funil_vendas_card_html(
    title="Funil de Vendas",
    leads=leads_total,
    reunioes=reun_real,
    contratos=contratos_total,
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
    "CARD_FUNIL_VENDAS": card_funil_vendas,
}

html = render_dashboard(slots=slots)

# ✅ height mínimo; o CSS do kiosk fixa o iframe em 100vh/100vw
components.html(html, height=1, scrolling=False)
