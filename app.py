import math
from typing import Any, Dict, Optional, Tuple

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh


# =========================
# Config
# =========================
st.set_page_config(page_title="Comercial | Indicadores", layout="wide")

REFRESH_MS = 30_000          # 1 minuto
CACHE_TTL_SECONDS = 25       # renova antes do refresh

# Indicadores (normalizamos pra UPPER)
IND_REUNIOES_REAL = "REUNIÕES OCORRIDAS"
IND_REUNIOES_META = "REUNIÕES OCORRIDAS - META"
IND_REUNIOES_PERC = "PERC META REUNIÕES OCORRIDAS"
IND_REUNIOES_DIF  = "DIF META REUNIÕES OCORRIDAS"

IND_FAT_REAL = "FATURAMENTO PAGO"         # preferimos pago
IND_FAT_FALLBACK_REAL = "FATURAMENTO"     # fallback
IND_FAT_META = "FATURAMENTO - META"
IND_FAT_PERC = "PERC META FATURAMENTO"
IND_FAT_DIF  = "DIF META FATURAMENTO"


# =========================
# Utils: formatação BR
# =========================
def fmt_int(v: Optional[float]) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "-"
    return f"{int(round(float(v)))}"

def fmt_money(v: Optional[float]) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "-"
    s = f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s

def fmt_pct_from_ratio(r: Optional[float]) -> str:
    if r is None or (isinstance(r, float) and math.isnan(r)):
        return "-"
    return f"{(float(r) * 100):.1f}".replace(".", ",") + " %"

def pct_to_float_percent(r: Optional[float]) -> float:
    if r is None or (isinstance(r, float) and math.isnan(r)):
        return 0.0
    return max(0.0, min(100.0, float(r) * 100.0))

def pill_text_from_ratio(r: Optional[float]) -> str:
    if r is None or (isinstance(r, float) and math.isnan(r)):
        return "Sem\ndados"
    r = float(r)
    if r >= 1.0:
        return "Meta\nbatida"
    if r >= 0.85:
        return "Falta\npouco"
    if r >= 0.6:
        return "Em\nandamento"
    return "Atenção"


# =========================
# Fetch + parse
# =========================
def _safe_json(resp: requests.Response) -> Dict[str, Any]:
    try:
        return resp.json()
    except Exception:
        return {"error": "Resposta não-JSON do endpoint", "status_code": resp.status_code, "text": resp.text[:400]}

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def fetch_payload(url: str, token: str) -> Dict[str, Any]:
    r = requests.get(url, params={"token": token}, timeout=25)
    r.raise_for_status()
    return _safe_json(r)

def payload_to_df(payload: Dict[str, Any]) -> Tuple[pd.DataFrame, Optional[str], Optional[str]]:
    updated_at = payload.get("updatedAt")
    sheet = payload.get("sheet")

    rows = payload.get("rows", [])
    df = pd.DataFrame(rows)

    if df.empty:
        return df, updated_at, sheet

    for col in ["INDICADORES", "RESPONSÁVEL"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()

    if "VALOR" in df.columns:
        df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce")

    if "DATA_ATUALIZAÇÃO" in df.columns:
        df["DATA_ATUALIZAÇÃO"] = pd.to_datetime(df["DATA_ATUALIZAÇÃO"], errors="coerce", utc=True)

    return df, updated_at, sheet

def latest_values(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    d = df.copy()
    if "DATA_ATUALIZAÇÃO" in d.columns and d["DATA_ATUALIZAÇÃO"].notna().any():
        d = d.sort_values("DATA_ATUALIZAÇÃO")
    d = d.drop_duplicates(subset=["RESPONSÁVEL", "INDICADORES"], keep="last")
    return d

def get_val(df_latest: pd.DataFrame, indicador: str, responsavel: Optional[str] = None) -> Optional[float]:
    indicador = indicador.strip().upper()
    d = df_latest[df_latest["INDICADORES"] == indicador]
    if responsavel:
        responsavel = responsavel.strip().upper()
        d = d[d["RESPONSÁVEL"] == responsavel]
    if d.empty:
        return None
    return d.iloc[-1]["VALOR"]


# =========================
# Gauge SVG + Cards (Tailwind)
# =========================
def _polar(cx, cy, r, ang_deg):
    a = math.radians(ang_deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)

def _arc_path(cx, cy, r, a0, a1):
    x0, y0 = _polar(cx, cy, r, a0)
    x1, y1 = _polar(cx, cy, r, a1)
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 1
    return f"M {x0:.2f} {y0:.2f} A {r:.2f} {r:.2f} 0 {large} {sweep} {x1:.2f} {y1:.2f}"

def gauge_svg(percent: float, segments: int = 12, stroke: int = 18,
              filled="#F05914", empty="#CFCFCF"):
    percent = max(0.0, min(100.0, percent))
    filled_count = int(round((percent / 100.0) * segments))

    arc_start = 200
    arc_end = 340

    cx, cy, r = 110, 105, 78
    seg_step = (arc_end - arc_start) / segments
    gap = seg_step * 0.28
    span = seg_step - gap

    paths = []
    for i in range(segments):
        a0 = arc_start + i * seg_step + gap / 2
        a1 = a0 + span
        color = filled if i < filled_count else empty
        d = _arc_path(cx, cy, r, a0, a1)
        paths.append(
            f'<path d="{d}" stroke="{color}" stroke-width="{stroke}" fill="none" stroke-linecap="round" />'
        )

    return f"""
    <svg width="220" height="150" viewBox="0 0 220 150" aria-hidden="true">
      {''.join(paths)}
    </svg>
    """

def kpi_card_html(
    title: str,
    percent_float: float,
    subtitle: str,
    left_label: str,
    left_value: str,
    left_badge: str,
    mid_label: str,
    mid_value: str,
    right_pill: str,
):
    svg = gauge_svg(percent_float, segments=12)

    # ✅ evita \n dentro de expressão do f-string
    right_pill_html = right_pill.replace("\n", "<br/>")

    return f"""
    <div class="bg-white rounded-3xl p-6 shadow-sm border border-zinc-100">
      <div class="text-3xl font-extrabold text-zinc-900">{title}</div>

      <div class="relative mt-2 flex justify-center">
        {svg}
        <div class="absolute top-[58px] left-1/2 -translate-x-1/2 text-center">
          <div class="text-3xl font-extrabold text-zinc-900">{percent_float:.1f}%</div>
          <div class="text-sm text-zinc-500 -mt-1">{subtitle}</div>
        </div>
      </div>

      <div class="mt-3 grid grid-cols-3 gap-3">
        <div class="relative bg-zinc-100 rounded-2xl p-3">
          <div class="text-xs text-zinc-500 leading-4">{left_label}</div>
          <div class="text-2xl font-extrabold text-zinc-900 mt-2">{left_value}</div>
          <span class="absolute top-3 right-3 bg-[#F05914] text-white text-xs px-2 py-1 rounded-full font-semibold">
            {left_badge}
          </span>
        </div>

        <div class="bg-zinc-100 rounded-2xl p-3">
          <div class="text-xs text-zinc-500 leading-4">{mid_label}</div>
          <div class="text-2xl font-extrabold text-zinc-900 mt-2">{mid_value}</div>
        </div>

        <div class="bg-[#F05914] text-white rounded-2xl p-3 flex items-center justify-center text-center font-extrabold leading-4">
          {right_pill_html}
        </div>
      </div>
    </div>
    """

def dashboard_html(cards_html: str) -> str:
    return f"""
    <script src="https://cdn.tailwindcss.com"></script>
    <div class="bg-zinc-200 rounded-[28px] p-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        {cards_html}
      </div>
    </div>
    """


# =========================
# App
# =========================
st_autorefresh(interval=REFRESH_MS, key="auto_refresh_1min")

URL = st.secrets.get("SHEETS_WEBAPP_URL", "")
TOKEN = st.secrets.get("SHEETS_WEBAPP_TOKEN", "")

with st.sidebar:
    st.markdown("### Config")
    st.write("Endpoint:", "✅" if URL else "❌")
    st.write("Token:", "✅" if TOKEN else "❌")
    st.caption("Atualiza a cada 1 minuto.")

if not (URL and TOKEN):
    st.error("Defina SHEETS_WEBAPP_URL e SHEETS_WEBAPP_TOKEN em Secrets.")
    st.stop()

try:
    payload = fetch_payload(URL, TOKEN)
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

st.markdown("## 📊 Indicadores Comerciais")
st.caption(f"Aba: {sheet or '-'} | updatedAt: {updated_at or '-'}")

tab1, tab2, tab3 = st.tabs(["Dashboard", "Tabela", "Por responsável"])

with tab1:
    # SDR
    reun_real = get_val(df_last, IND_REUNIOES_REAL, "SDR")
    reun_meta = get_val(df_last, IND_REUNIOES_META, "SDR")
    reun_perc = get_val(df_last, IND_REUNIOES_PERC, "SDR")
    reun_dif  = get_val(df_last, IND_REUNIOES_DIF,  "SDR")

    # CLOSER
    fat_real = get_val(df_last, IND_FAT_REAL, "CLOSER")
    if fat_real is None:
        fat_real = get_val(df_last, IND_FAT_FALLBACK_REAL, "CLOSER")
    fat_meta = get_val(df_last, IND_FAT_META, "CLOSER")
    fat_perc = get_val(df_last, IND_FAT_PERC, "CLOSER")
    fat_dif  = get_val(df_last, IND_FAT_DIF,  "CLOSER")

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

    components.html(dashboard_html(card1 + card2), height=420)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### SDR")
        st.write("Dif meta reuniões:", fmt_int(reun_dif))
        st.write("Perc meta reuniões:", fmt_pct_from_ratio(reun_perc))
    with c2:
        st.markdown("### CLOSER")
        st.write("Dif meta faturamento:", fmt_money(fat_dif))
        st.write("Perc meta faturamento:", fmt_pct_from_ratio(fat_perc))

with tab2:
    if df.empty:
        st.info("Sem dados.")
    else:
        show = df.copy()
        if "DATA_ATUALIZAÇÃO" in show.columns:
            show = show.sort_values("DATA_ATUALIZAÇÃO", ascending=False)
        st.dataframe(show, use_container_width=True, hide_index=True)

with tab3:
    if df.empty:
        st.info("Sem dados.")
    else:
        d = df_last.copy()
        pivot = d.pivot(index="RESPONSÁVEL", columns="INDICADORES", values="VALOR")
        st.dataframe(pivot, use_container_width=True)

        st.markdown("### Ranking (Reuniões Ocorridas)")
        if IND_REUNIOES_REAL in pivot.columns:
            rank = pivot[IND_REUNIOES_REAL].dropna().sort_values(ascending=False).reset_index()
            rank.columns = ["RESPONSÁVEL", "REUNIÕES OCORRIDAS"]
            st.dataframe(rank, use_container_width=True, hide_index=True)
        else:
            st.caption("Indicador 'REUNIÕES OCORRIDAS' não encontrado no pivot.")
