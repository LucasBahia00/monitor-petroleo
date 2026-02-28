"""
IRAN OIL WAR ROOM — v3.0
Dashboard principal Streamlit
"""

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import pytz

try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTOREFRESH = True
except ImportError:
    HAS_AUTOREFRESH = False

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Iran Oil · War Room",
    page_icon="🛢",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if HAS_AUTOREFRESH:
    st_autorefresh(interval=60000, key="auto_refresh")

# ─── STYLE ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@500;600;700&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif !important;
    box-sizing: border-box;
}
.stApp, .main, section[data-testid="stMain"] > div {
    background-color: #04080d !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0.8rem 1.2rem !important; max-width: 100% !important; }

.wrt-header {
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 1px solid #112233; padding-bottom: 8px; margin-bottom: 10px;
}
.wrt-logo {
    font-family: 'Share Tech Mono', monospace;
    font-size: 18px; color: #e63030; letter-spacing: 4px; text-transform: uppercase;
}
.wrt-sub { font-size: 10px; color: #2a5a7a; letter-spacing: 2px; font-family: 'Share Tech Mono', monospace; margin-top: 2px; }
.wrt-clock { font-family: 'Share Tech Mono', monospace; font-size: 12px; color: #00ff88; text-align: right; }
.live-dot {
    display: inline-block; width: 7px; height: 7px; border-radius: 50%;
    background: #00ff88; margin-right: 5px;
    animation: blink 1.4s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.15} }

.alert-ticker {
    background: linear-gradient(90deg,#1a0500,#0d0300);
    border-left: 3px solid #e63030; border: 1px solid #331100;
    padding: 6px 14px; margin-bottom: 10px;
    font-family: 'Share Tech Mono', monospace; font-size: 11px; color: #ff7750;
    letter-spacing: 1px;
}

.kpi-row { display: flex; gap: 8px; margin-bottom: 10px; }
.kpi-card {
    flex: 1; background: linear-gradient(135deg, #0a1520 0%, #060d14 100%);
    border: 1px solid #112233; border-top: 2px solid; padding: 10px 14px;
}
.kpi-lbl {
    font-family: 'Share Tech Mono', monospace; font-size: 9px; letter-spacing: 2px;
    text-transform: uppercase; color: #2a5a7a; margin-bottom: 3px;
}
.kpi-val {
    font-family: 'Share Tech Mono', monospace; font-size: 24px; font-weight: 700;
    line-height: 1; letter-spacing: 1px;
}
.kpi-chg { font-family: 'Share Tech Mono', monospace; font-size: 11px; margin-top: 3px; }
.kpi-brent { border-top-color: #00ccff; } .kpi-brent .kpi-val { color: #00ccff; }
.kpi-gold  { border-top-color: #ffd700; } .kpi-gold  .kpi-val { color: #ffd700; }
.kpi-petr4 { border-top-color: #00ff88; } .kpi-petr4 .kpi-val { color: #00ff88; }
.kpi-prio3 { border-top-color: #ff6030; } .kpi-prio3 .kpi-val { color: #ff6030; }

.sec-lbl {
    font-family: 'Share Tech Mono', monospace; font-size: 10px; letter-spacing: 3px;
    text-transform: uppercase; color: #2a5a7a; border-left: 3px solid #e63030;
    padding-left: 8px; margin: 12px 0 8px 0;
}

.it { width: 100%; border-collapse: collapse; font-family: 'Share Tech Mono', monospace; font-size: 11px; }
.it th { background:#0a1520; color:#2a5a7a; padding:7px 10px; text-align:left; font-size:9px;
         letter-spacing:1px; text-transform:uppercase; border-bottom:1px solid #112233; }
.it td { padding:6px 10px; border-bottom:1px solid #0a1520; color:#aac8d8; }
.it tr:hover td { background:#0a1520; }
.bdg { padding:2px 7px; border-radius:2px; font-size:9px; font-weight:700; letter-spacing:1px; white-space:nowrap; }
.bdg-crit { background:#2a0000; color:#ff4444; border:1px solid #ff4444; }
.bdg-high { background:#2a1500; color:#ff8c00; border:1px solid #ff8c00; }
.bdg-med  { background:#0e2200; color:#7fff00; border:1px solid #7fff00; }

.intel-wrap { border: 1px solid #112233; }
.intel-hdr {
    background: #0a1520; padding: 9px 12px; border-bottom: 1px solid #112233;
    display: flex; justify-content: space-between; align-items: center;
}
.intel-hdr-lbl { font-family:'Share Tech Mono',monospace; font-size:10px; letter-spacing:2px; color:#aac8d8; }
.src-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 8px 12px; border-bottom: 1px solid #080f16;
}
.src-row:hover { background: #0a1520; }
.src-handle { font-family:'Share Tech Mono',monospace; font-size:13px; color:#00aaff; text-decoration:none; }
.src-handle:hover { color:#00ddff; }
.src-tag { font-size:9px; color:#2a5a7a; letter-spacing:1px; text-transform:uppercase; margin-top:1px; }

.ql-link {
    display: block; padding: 7px 12px; margin-bottom: 4px;
    background: #0a1520; border: 1px solid #112233; border-left: 2px solid #00aaff;
    color: #00aaff; font-family:'Share Tech Mono',monospace; font-size:10px;
    text-decoration: none; letter-spacing: 1px;
}
.ql-link:hover { background: #0d1e30; }

.wrt-footer {
    margin-top: 14px; padding-top: 8px; border-top: 1px solid #112233;
    font-family:'Share Tech Mono',monospace; font-size:9px; color:#1a3a4a;
    display: flex; justify-content: space-between;
}
div[data-testid="column"] { padding: 0 4px !important; }
</style>
""", unsafe_allow_html=True)

# ─── DATA ─────────────────────────────────────────────────────────────────────
TKRS   = ["BZ=F", "GC=F", "PETR4.SA", "PRIO3.SA"]
NAMES  = {"BZ=F":"BRENT", "GC=F":"OURO", "PETR4.SA":"PETR4", "PRIO3.SA":"PRIO3"}
UNITS  = {"BZ=F":"USD/bbl", "GC=F":"USD/oz", "PETR4.SA":"BRL", "PRIO3.SA":"BRL"}
COLORS = {"BZ=F":"#00CCFF","GC=F":"#FFD700","PETR4.SA":"#00ff88","PRIO3.SA":"#ff6030"}
KPICLS = {"BZ=F":"kpi-brent","GC=F":"kpi-gold","PETR4.SA":"kpi-petr4","PRIO3.SA":"kpi-prio3"}

@st.cache_data(ttl=60)
def get_market_data():
    df = yf.download(TKRS, period="5d", interval="15m", progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df = df["Close"]
    df = df.ffill()
    df_norm = (df / df.iloc[0]) * 100
    df_norm["MA9"]  = df_norm["BZ=F"].rolling(9).mean()
    df_norm["MA21"] = df_norm["BZ=F"].rolling(21).mean()
    return df, df_norm

df_raw, df_plot = get_market_data()

def get_kpi(ticker):
    try:
        s    = df_raw[ticker].dropna()
        last = float(s.iloc[-1])
        pct  = (float(s.iloc[-1]) - float(s.iloc[0])) / float(s.iloc[0]) * 100
        return last, pct
    except:
        return None, None

# ─── HEADER ──────────────────────────────────────────────────────────────────
now = datetime.now(pytz.utc).strftime("%Y-%m-%d  %H:%M UTC")
st.markdown(f"""
<div class="wrt-header">
  <div>
    <div class="wrt-logo">🛢 Iran Oil · War Room Terminal</div>
    <div class="wrt-sub">GEOPOLITICAL MARKET INTELLIGENCE · 5-DAY INTRADAY · PERSIAN GULF ASSETS</div>
  </div>
  <div class="wrt-clock"><span class="live-dot"></span>LIVE &nbsp; {now}</div>
</div>
<div class="alert-ticker">
  ⚠ MONITORAMENTO ATIVO &nbsp;|&nbsp;
  Kharg Island · Strait of Hormuz · Abadan · South Pars · OPEC+ &nbsp;|&nbsp;
  Auto-refresh 60s &nbsp;|&nbsp; Telegram bot ativo &nbsp;|&nbsp; Yahoo Finance
</div>
""", unsafe_allow_html=True)

# ─── KPI ROW ─────────────────────────────────────────────────────────────────
kpi_html = '<div class="kpi-row">'
for t in TKRS:
    v, c = get_kpi(t)
    if v is not None:
        arrow = "▲" if c >= 0 else "▼"
        cc    = "#00ff88" if c >= 0 else "#ff4444"
        kpi_html += f"""
        <div class="kpi-card {KPICLS[t]}">
          <div class="kpi-lbl">{NAMES[t]} · {UNITS[t]}</div>
          <div class="kpi-val">{v:.2f}</div>
          <div class="kpi-chg" style="color:{cc}">{arrow} {c:+.2f}% (5D)</div>
        </div>"""
kpi_html += "</div>"
st.markdown(kpi_html, unsafe_allow_html=True)

# ─── MAIN LAYOUT ─────────────────────────────────────────────────────────────
col_main, col_intel = st.columns([3, 1], gap="small")

with col_main:
    st.markdown('<div class="sec-lbl">Performance Relativa 5D · Base 100 + Médias Móveis Brent</div>', unsafe_allow_html=True)

    fig = go.Figure()
    for t in TKRS:
        if t in df_plot.columns:
            fig.add_trace(go.Scatter(
                x=df_plot.index, y=df_plot[t], name=NAMES[t],
                line=dict(width=2.5 if t == "BZ=F" else 1.5, color=COLORS[t]),
                hovertemplate=f"<b>{NAMES[t]}</b> %{{y:.2f}}<extra></extra>"
            ))
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot["MA9"],  name="MA9",
        line=dict(color="#ffffff", width=1, dash="dot"),
        hovertemplate="MA9 %{y:.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot["MA21"], name="MA21",
        line=dict(color="#ff8c00", width=1.5),
        hovertemplate="MA21 %{y:.2f}<extra></extra>"))

    fig.update_layout(
        template="plotly_dark", height=380,
        margin=dict(l=0, r=0, t=6, b=0),
        paper_bgcolor="#04080d", plot_bgcolor="#04080d",
        yaxis=dict(side="right", gridcolor="#0a1520",
                   tickfont=dict(family="Share Tech Mono", size=10, color="#2a5a7a")),
        xaxis=dict(gridcolor="#0a1520",
                   tickfont=dict(family="Share Tech Mono", size=10, color="#2a5a7a")),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
                    font=dict(family="Share Tech Mono", size=10, color="#aac8d8"),
                    bgcolor="rgba(4,8,13,0.85)", bordercolor="#112233", borderwidth=1),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Infra Table ──
    st.markdown('<div class="sec-lbl">Infraestrutura Crítica · Alvos de Alto Impacto</div>', unsafe_allow_html=True)

    infra = [
        ("Estreito de Hormuz", "Rota Exportação",     "17 mn bpd",       "~20% global", "CRÍTICO"),
        ("Kharg Island",       "Terminal Exportação",  "~6 mn bpd",       "~7% global",  "CRÍTICO"),
        ("South Pars",         "Campo Gás/Petróleo",   "maior reserva",   "—",           "CRÍTICO"),
        ("Ahvaz",              "Campo Petrolífero",    "945 k bpd",        "~1% global",  "CRÍTICO"),
        ("Abadan",             "Refinaria",            "500 k bpd",        "~0.5%",       "ALTO"),
        ("Gachsaran",          "Campo Petrolífero",    "560 k bpd",        "~0.6%",       "ALTO"),
        ("Isfahan",            "Refinaria",            "375 k bpd",        "—",           "ALTO"),
        ("Bandar Abbas",       "Porto / Refinaria",    "320 k bpd",        "—",           "ALTO"),
        ("Marun",              "Campo Petrolífero",    "520 k bpd",        "—",           "MÉDIO"),
        ("Tehran Refinery",    "Refinaria",            "225 k bpd",        "—",           "MÉDIO"),
    ]

    rows = ""
    for r in infra:
        bc = "bdg-crit" if r[4] == "CRÍTICO" else ("bdg-high" if r[4] == "ALTO" else "bdg-med")
        rows += f"""<tr>
            <td style="color:#e8f4ff;font-weight:600">{r[0]}</td>
            <td>{r[1]}</td>
            <td style="color:#ffd700">{r[2]}</td>
            <td style="color:#aac8d8">{r[3]}</td>
            <td><span class="bdg {bc}">{r[4]}</span></td>
        </tr>"""

    st.markdown(f"""
    <table class="it">
      <thead><tr>
        <th>ATIVO</th><th>TIPO</th><th>CAPACIDADE</th><th>EXP. GLOBAL</th><th>IMPACTO</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """, unsafe_allow_html=True)

with col_intel:
    sources = [
        ("JavierBlas",      "Commodities · Bloomberg"),
        ("staunovo",        "Oil Market · UBS"),
        ("TankerTrackers",  "Tanker Intelligence"),
        ("Osint613",        "OSINT · Geopolítica"),
        ("sentdefender",    "Intel · Conflitos"),
        ("israelnewspulse", "Notícias · Israel"),
        ("zerohedge",       "Macro · Markets"),
        ("realDonaldTrump", "Político · EUA"),
        ("hoje_no",         "Notícias · Brasil"),
        ("cbjom",           "Análise · Energia"),
        ("DeItaone",        "Headlines · Rápido"),
    ]

    src_rows = "".join(f"""
    <div class="src-row">
      <div>
        <a class="src-handle" href="https://twitter.com/{h}" target="_blank">@{h}</a>
        <div class="src-tag">{tag}</div>
      </div>
      <span style="color:#112233;font-size:14px;">→</span>
    </div>""" for h, tag in sources)

    st.markdown(f"""
    <div class="sec-lbl">Intel Feed · 11 Fontes X/Twitter</div>
    <div class="intel-wrap">
      <div class="intel-hdr">
        <span class="intel-hdr-lbl">FONTES MONITORADAS</span>
        <span style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#00ff88;letter-spacing:1px;">
          <span class="live-dot"></span>LIVE
        </span>
      </div>
      {src_rows}
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-lbl">Acesso Rápido</div>', unsafe_allow_html=True)
    links = [
        ("🗺 TankerTrackers Map",  "https://www.tankertracker.com"),
        ("📡 MarineTraffic",        "https://www.marinetraffic.com"),
        ("📰 Reuters · Energy",     "https://www.reuters.com/business/energy/"),
        ("🛢 EIA Weekly Report",    "https://www.eia.gov/petroleum/"),
        ("📊 OPEC Newsroom",        "https://www.opec.org/opec_web/en/press_room/"),
        ("⚡ IAEA · Iran Nuclear",  "https://www.iaea.org/newscenter/focus/iran"),
    ]
    for label, url in links:
        st.markdown(f'<a class="ql-link" href="{url}" target="_blank">{label}</a>', unsafe_allow_html=True)

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="wrt-footer">
  <span>IRAN OIL WAR ROOM · v3.0 · DATA: YAHOO FINANCE</span>
  <span>BOT TELEGRAM ATIVO · AI: GEMINI 1.5-FLASH</span>
  <span>⚠ APENAS PARA FINS INFORMATIVOS</span>
</div>
""", unsafe_allow_html=True)
