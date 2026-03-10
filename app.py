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

# Quantidade máxima de pessoas exibidas nos rankings (conteúdo rola dentro do card)
RANKING_MAX_ROWS = 10


# =========================
# Hide Streamlit chrome (menu/header/footer/toolbar)
# =========================
def hide_streamlit_chrome():
    st.markdown(
        """
        <style>
          /* Remove barras/menus padrão */
          #MainMenu { visibility: hidden; }
          footer { visibility: hidden; }
          header { visibility: hidden; }

          /* Streamlit "chrome" (varia por versão) */
          [data-testid="stHeader"] { display: none !important; }
          [data-testid="stToolbar"] { display: none !important; }
          [data-testid="stDecoration"] { display: none !important; }
          [data-testid="stStatusWidget"] { display: none !important; }

          /* Padding do app (deixa fullscreen de verdade) */
          .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; }
          [data-testid="stAppViewContainer"] { padding-top: 0rem !important; }

          /* Tenta esconder o badge "Hosted with Streamlit" (no Cloud pode voltar) */
          a[href*="streamlit.io"] { display: none !important; }
          iframe[title="streamlit"] { display: none !important; } /* safety */
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================
# Config
# =========================
st.set_page_config(page_title="Comercial | Indicadores", layout="wide")

# ✅ esconde UI do Streamlit (fora do iframe)
hide_streamlit_chrome()

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
fat_assinado = total_for_indicator(df_last, INDICATORS.FATURAMENTO_ASSINADO, prefer_responsavel="CLOSER")
if fat_assinado is None:
    fat_assinado = total_for_indicator(df_last, INDICATORS.FATURAMENTO_ASSINADO, exclude_responsaveis=["CLOSER"])

fat_pago = total_for_indicator(df_last, INDICATORS.FATURAMENTO_PAGO, prefer_responsavel="CLOSER")
if fat_pago is None:
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
    left_badge=pct_to_float_percent(reun_crescimento),
    mid_label="Meta de Reuniões",
    mid_value=fmt_int(reun_meta),
    right_pill=fmt_int(reun_dif) if reun_dif is not None else "0",
)

card_faturamento = kpi_card_html(
    title="Faturamento",
    percent_float=pct_to_float_percent(fat_perc),
    subtitle="Progresso",
    left_label="Faturamento Assinado",
    left_value=fmt_money_no_cents(fat_assinado),
    left_badge=pct_to_float_percent(fat_cresc),
    mid_label="Meta de Faturamento",
    mid_value=fmt_money_no_cents(fat_meta),
    right_pill=fmt_int(fat_dif),
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


def _norm_name(name: str) -> str:
    """Normaliza pra casar nomes entre indicadores (evita diferença de espaços/caixa)."""
    n = (name or "").replace("\u00A0", " ")
    n = " ".join(n.split()).strip().upper()
    return n


def _to_float_safe(v) -> float:
    """Converte valor com segurança (aceita float, '0,123', '0.123', etc.)."""
    if v is None:
        return 0.0
    try:
        if isinstance(v, (int, float)):
            return float(v)
        s = str(v).strip().replace("\u00A0", " ").replace("%", "")
        # se vier no padrão pt-BR com vírgula decimal
        if "," in s and "." in s:
            # heurística: se a última vírgula está depois do último ponto, vírgula é decimal
            if s.rfind(",") > s.rfind("."):
                s = s.replace(".", "").replace(",", ".")
            else:
                s = s.replace(",", "")
        else:
            s = s.replace(",", ".")
        return float(s)
    except Exception:
        return 0.0


# 1) Reuniões por pessoa
#    - pegamos apenas pessoas (não "SDR"/"EQUIPE")
reun_people_vals = people_values(
    df_last,
    INDICATORS.REUNIOES_REAL,
    exclude_responsaveis=["SDR", "CLOSER"],
)
reun_people_vals = [x for x in reun_people_vals if not _is_team_label(x.get("name", ""))]

# 2) Taxa de conversão por pessoa (indicador "TAXA DE CONVERSÃO")
conv_people_vals = people_values(
    df_last,
    INDICATORS.TAXA_CONVERSAO,
    exclude_responsaveis=["SDR", "CLOSER"],
)
conv_people_vals = [x for x in conv_people_vals if not _is_team_label(x.get("name", ""))]

# 3) ✅ Dinâmico: só entra no ranking quem tiver OS DOIS indicadores
#    (Reuniões + Taxa de Conversão). Se você adicionar uma nova pessoa no Sheets com ambos,
#    ela aparece automaticamente (sem precisar mexer no código).
reun_by_name = {
    _norm_name(x.get("name", "")): x
    for x in reun_people_vals
    if _norm_name(x.get("name", ""))
}
conv_by_name = {
    _norm_name(x.get("name", "")): _to_float_safe(x.get("value"))
    for x in conv_people_vals
    if _norm_name(x.get("name", ""))
}

eligible_keys = [k for k in reun_by_name.keys() if k in conv_by_name]

rank_sdr_items: list[dict] = []
for k in eligible_keys:
    it = reun_by_name[k]
    name = it.get("name")
    display_name = it.get("display_name")
    reun = _to_float_safe(it.get("value"))

    conv_raw = conv_by_name.get(k, 0.0)          # ratio (0..1) ou já % (0..100)
    conv_pct = pct_to_float_percent(conv_raw)     # normaliza para % (0..100)

    rank_sdr_items.append(
        {
            "name": name,
            "display_name": display_name,
            "reunioes": reun,
            "conversao": conv_pct,
        }
    )

# Ordenação do ranking SDR: Reuniões (desc) e, em empate, Conversão (desc)
rank_sdr_items.sort(
    key=lambda r: (_to_float_safe(r.get("reunioes")), _to_float_safe(r.get("conversao"))),
    reverse=True,
)

# Mantém um teto de itens (o conteúdo rola dentro do card)
rank_sdr_items = rank_sdr_items[:RANKING_MAX_ROWS]
card_ranking_sdr = ranking_sdr_card_html(
    title="Ranking SDR",
    items=[
        {
            "name": r["name"],
            "display_name": r.get("display_name"),
            "reunioes": r["reunioes"],
            "conversao": r["conversao"],
        }
        for r in rank_sdr_items
    ],
    limit=RANKING_MAX_ROWS,
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

    m = re.search(r"-?[\d\.,]+", s.replace("R$", "").strip())
    if not m:
        return 0.0

    num = m.group(0)

    if "." in num and "," in num:
        num = num.replace(".", "").replace(",", ".")
    elif "," in num and "." not in num:
        num = num.replace(",", ".")
    else:
        if num.count(".") > 1:
            num = num.replace(".", "")

    try:
        return float(num)
    except Exception:
        return 0.0


contratos_vals = people_values(df_last, INDICATORS.CONTRATOS_ASSINADOS, exclude_responsaveis=["CLOSER"])
fat_ass_vals = people_values(df_last, INDICATORS.FATURAMENTO_ASSINADO, exclude_responsaveis=["CLOSER"])
fat_pago_vals = people_values(df_last, INDICATORS.FATURAMENTO_PAGO, exclude_responsaveis=["CLOSER"])

# ✅ % vem do indicador PERC FATURAMENTO PAGO (sem cálculo no app.py)
perc_fat_pago_vals = people_values(df_last, INDICATORS.PERC_FATURAMENTO_PAGO, exclude_responsaveis=["CLOSER"])

def _map_norm(vals: list[dict]) -> dict[str, dict]:
    """Mapeia: NOME_NORMALIZADO -> {name, value}."""
    out: dict[str, dict] = {}
    for x in vals or []:
        nm = str(x.get("name") or "").strip()
        if not nm:
            continue
        if nm.upper() in {"CLOSER", "SDR"}:
            continue
        k = _norm_name(nm)
        if not k:
            continue
        out[k] = {
            "name": nm,
            "display_name": x.get("display_name"),
            "original_name": x.get("original_name"),
            "value": x.get("value"),
        }
    return out

m_contr = _map_norm(contratos_vals)
m_fa = _map_norm(fat_ass_vals)
m_fp = _map_norm(fat_pago_vals)
m_perc_fat_pago = _map_norm(perc_fat_pago_vals)

# ✅ Dinâmico: só entra no Ranking Closer quem tiver TODOS os 4 indicadores:
#    CONTRATOS ASSINADOS, FATURAMENTO ASSINADO, FATURAMENTO PAGO e PERC FATURAMENTO PAGO
#
# ⚠️ Importante: NÃO use set() puro aqui para não introduzir ordem não-determinística
# (o que bagunça a colocação quando há empates). Mantemos uma ordem estável.
eligible_keys = sorted(set(m_contr) & set(m_fa) & set(m_fp) & set(m_perc_fat_pago))

rows_closer: list[dict] = []
for k in eligible_keys:
    src_row = (m_fp.get(k) or m_fa.get(k) or m_contr.get(k) or m_perc_fat_pago.get(k) or {})
    name = (
        src_row.get("name")
        or (m_fp.get(k) or {}).get("name")
        or (m_fa.get(k) or {}).get("name")
        or (m_contr.get(k) or {}).get("name")
        or (m_perc_fat_pago.get(k) or {}).get("name")
        or k
    )
    display_name = src_row.get("display_name")

    perc_raw = (m_perc_fat_pago.get(k) or {}).get("value")  # pode vir 0.15, "15%", "0,15", etc.
    perc_float = pct_to_float_percent(perc_raw)               # normaliza para 0..100 (float)

    rows_closer.append(
        {
            "name": name,
            "display_name": display_name,
            "contratos": (m_contr.get(k) or {}).get("value"),
            "fat_assinado": (m_fa.get(k) or {}).get("value"),
            "fat_pago": (m_fp.get(k) or {}).get("value"),

            # ✅ chave "oficial" que o ranklist procura por padrão (pct_field)
            "PERC FATURAMENTO PAGO": perc_float,

            # ✅ opcional: mantém fallback compatível (ranklist também busca "pct")
            "pct": perc_float,
        }
    )

# Ordenação do Ranking Closer:
#  1) Faturamento ASSINADO (desc)
#  2) Em empate, Faturamento PAGO (desc)
#  3) Em novo empate, Contratos (desc)
#  4) Por fim, Nome (asc) para estabilidade total
rows_closer.sort(
    key=lambda r: (
        -float(_to_float_moneyish(r.get("fat_assinado")) or 0.0),
        -float(_to_float_moneyish(r.get("fat_pago")) or 0.0),
        -float(r.get("contratos") or 0.0),
        str(r.get("name") or "").strip().upper(),
    )
)
rows_closer = rows_closer[:RANKING_MAX_ROWS]


card_ranking_closer = podium_contracts_card_html(rows_closer, title="Ranking Closer", limit=RANKING_MAX_ROWS)


# =========================
# 5) Funil de vendas (NOVO)
# =========================
contratos_total = get_val(df_last, INDICATORS.CONTRATOS_ASSINADOS, "CLOSER")
if contratos_total is None:
    contratos_total = sum(float(x.get("value") or 0.0) for x in contratos_vals) or 0.0

tax_funil_1_raw = get_val(df_last, INDICATORS.TAX_CONV_FUNIL_1, "SDR")
tax_funil_2_raw = get_val(df_last, INDICATORS.TAX_CONV_FUNIL_2, "CLOSER")

tax_funil_1 = pct_to_float_percent(tax_funil_1_raw)
tax_funil_2 = pct_to_float_percent(tax_funil_2_raw)

card_funil_vendas = funil_vendas_card_html(
    title="Funil de Vendas",
    leads=leads_total,
    reunioes=reun_real,
    contratos=contratos_total,
    pct_leads_para_reunioes=tax_funil_1,
    pct_reunioes_para_contratos=tax_funil_2,
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

components.html(html, height=1, scrolling=False)