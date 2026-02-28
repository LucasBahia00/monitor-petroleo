import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import pytz

# ─── CONFIG ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Iran Oil War Room",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st_autorefresh(interval=60000, key="f5_refresh")

# ─── CUSTOM CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

/* Base */
html, body, [class*="css"] {
    background-color: #060a0f !important;
    color: #c8d8e8 !important;
    font-family: 'Rajdhani', sans-serif !important;
}
.stApp { background-color: #060a0f !important; }

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; }

/* Header */
.war-room-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #1a3a4a;
    padding-bottom: 10px;
    margin-bottom: 16px;
}
.war-room-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 22px;
    color: #ff4b2b;
    letter-spacing: 3px;
    text-transform: uppercase;
}
.war-room-subtitle {
    font-size: 12px;
    color: #4a7a9b;
    letter-spacing: 2px;
    font-family: 'Share Tech Mono', monospace;
}
.war-room-time {
    font-family: 'Share Tech Mono', monospace;
    font-size: 13px;
    color: #00ff88;
    text-align: right;
}

/* KPI Cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 16px;
}
.kpi-card {
    background: linear-gradient(135deg, #0d1a24 0%, #091520 100%);
    border: 1px solid #1a3a4a;
    border-top: 2px solid;
    padding: 12px 16px;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.02) 0%, transparent 100%);
}
.kpi-label {
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #4a7a9b;
    font-family: 'Share Tech Mono', monospace;
    margin-bottom: 4px;
}
.kpi-value {
    font-size: 26px;
    font-weight: 700;
    font-family: 'Share Tech Mono', monospace;
    line-height: 1;
}
.kpi-change {
    font-size: 12px;
    font-family: 'Share Tech Mono', monospace;
    margin-top: 4px;
}
.kpi-brent { border-top-color: #00ccff; }
.kpi-brent .kpi-value { color: #00ccff; }
.kpi-gold { border-top-color: #ffd700; }
.kpi-gold .kpi-value { color: #ffd700; }
.kpi-petr4 { border-top-color: #00ff88; }
.kpi-petr4 .kpi-value { color: #00ff88; }
.kpi-prio3 { border-top-color: #ff6b35; }
.kpi-prio3 .kpi-value { color: #ff6b35; }

/* Section headers */
.section-header {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #4a7a9b;
    border-left: 3px solid #ff4b2b;
    padding-left: 10px;
    margin-bottom: 10px;
    margin-top: 8px;
}

/* Infra table */
.infra-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
}
.infra-table th {
    background: #0d1a24;
    color: #4a7a9b;
    padding: 8px 12px;
    text-align: left;
    letter-spacing: 1px;
    font-size: 10px;
    text-transform: uppercase;
    border-bottom: 1px solid #1a3a4a;
}
.infra-table td {
    padding: 7px 12px;
    border-bottom: 1px solid #0d1a24;
    color: #c8d8e8;
}
.infra-table tr:hover td { background: #0d1a24; }
.badge {
    padding: 2px 8px;
    border-radius: 2px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
}
.badge-critical { background: #3d0000; color: #ff4444; border: 1px solid #ff4444; }
.badge-high     { background: #3d1f00; color: #ff8c00; border: 1px solid #ff8c00; }
.badge-medium   { background: #1a2e00; color: #7fff00; border: 1px solid #7fff00; }

/* Intel panel */
.intel-panel {
    background: #060a0f;
    border: 1px solid #1a3a4a;
    height: 100%;
}
.intel-header {
    background: #0d1a24;
    padding: 10px 14px;
    border-bottom: 1px solid #1a3a4a;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.intel-live {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 10px;
    color: #00ff88;
    font-family: 'Share Tech Mono', monospace;
    letter-spacing: 1px;
}
.intel-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #00ff88;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}
.source-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 9px 14px;
    border-bottom: 1px solid #0d1a24;
    transition: background 0.2s;
}
.source-card:hover { background: #0d1a24; }
.source-handle {
    font-family: 'Share Tech Mono', monospace;
    font-size: 13px;
    color: #00aaff;
    text-decoration: none;
}
.source-handle:hover { color: #00ccff; }
.source-tag {
    font-size: 9px;
    color: #4a7a9b;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.source-arrow {
    color: #1a3a4a;
    font-size: 16px;
}
.alert-bar {
    background: linear-gradient(90deg, #1a0a00, #2a1000);
    border: 1px solid #ff4b2b33;
    border-left: 3px solid #ff4b2b;
    padding: 8px 14px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #ff8c60;
    letter-spacing: 1px;
    margin-bottom: 12px;
}
.ticker-scroll {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #4a7a9b;
    letter-spacing: 1px;
    padding: 6px 0;
    margin-bottom: 12px;
    border-top: 1px solid #1a3a4a;
    border-bottom: 1px solid #1a3a4a;
    white-space: nowrap;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

# ─── DATA ─────────────────────────────────────────────────────────────────────
TKRS = ["BZ=F", "GC=F", "PETR4.SA", "PRIO3.SA"]
NOMES = {"BZ=F": "BRENT", "GC=F": "OURO", "PETR4.SA": "PETR4", "PRIO3.SA": "PRIO3"}
CORES = {"BZ=F": "#00CCFF", "GC=F": "#FFD700", "PETR4.SA": "#00ff88", "PRIO3.SA": "#ff6b35"}

@st.cache_data(ttl=60)
def get_data():
    df = yf.download(TKRS, period="5d", interval="15m", progress=False)['Close'].ffill()
    df_norm = (df / df.iloc[0]) * 100
    df_norm['MA9']  = df_norm['BZ=F'].rolling(9).mean()
    df_norm['MA21'] = df_norm['BZ=F'].rolling(21).mean()
    return df, df_norm

df_raw, df_plot = get_data()

def get_kpi(ticker):
    try:
        series = df_raw[ticker].dropna()
        last  = series.iloc[-1]
        first = series.iloc[0]
        chg   = ((last - first) / first) * 100
        return last, chg
    except:
        return None, None

# ─── HEADER ──────────────────────────────────────────────────────────────────
now_utc = datetime.now(pytz.utc).strftime("%Y-%m-%d  %H:%M UTC")
st.markdown(f"""
<div class="war-room-header">
  <div>
    <div class="war-room-title">🛢 Iran Oil · War Room Terminal</div>
    <div class="war-room-subtitle">GEOPOLITICAL MARKET INTELLIGENCE · 5-DAY INTRADAY VIEW</div>
  </div>
  <div class="war-room-time">⬤ LIVE &nbsp;&nbsp; {now_utc}</div>
</div>
""", unsafe_allow_html=True)

# ─── ALERT BAR ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="alert-bar">
  ⚠ MONITORAMENTO ATIVO &nbsp;|&nbsp; Kharg Island · Strait of Hormuz · OPEC+ Headlines &nbsp;|&nbsp; 
  Auto-refresh: 60s &nbsp;|&nbsp; Fonte: Yahoo Finance / yfinance
</div>
""", unsafe_allow_html=True)

# ─── KPI CARDS ────────────────────────────────────────────────────────────────
kpi_classes = {"BZ=F": "kpi-brent", "GC=F": "kpi-gold", "PETR4.SA": "kpi-petr4", "PRIO3.SA": "kpi-prio3"}
units       = {"BZ=F": "USD/bbl", "GC=F": "USD/oz", "PETR4.SA": "BRL", "PRIO3.SA": "BRL"}

kpi_html = '<div class="kpi-grid">'
for t in TKRS:
    val, chg = get_kpi(t)
    if val is not None:
        arrow = "▲" if chg >= 0 else "▼"
        chg_color = "#00ff88" if chg >= 0 else "#ff4444"
        kpi_html += f"""
        <div class="kpi-card {kpi_classes[t]}">
            <div class="kpi-label">{NOMES[t]} · {units[t]}</div>
            <div class="kpi-value">{val:.2f}</div>
            <div class="kpi-change" style="color:{chg_color}">{arrow} {chg:+.2f}% (5D)</div>
        </div>"""
kpi_html += '</div>'
st.markdown(kpi_html, unsafe_allow_html=True)

# ─── MAIN LAYOUT ─────────────────────────────────────────────────────────────
col_main, col_intel = st.columns([3, 1])

with col_main:
    # Chart
    st.markdown('<div class="section-header">Performance Relativa 5D + Médias Móveis (Base 100)</div>', unsafe_allow_html=True)

    fig = go.Figure()
    for t in TKRS:
        if t in df_plot.columns:
            fig.add_trace(go.Scatter(
                x=df_plot.index, y=df_plot[t],
                name=NOMES[t],
                line=dict(width=2.5 if t == 'BZ=F' else 1.5, color=CORES[t]),
                hovertemplate=f"<b>{NOMES[t]}</b><br>%{{x}}<br>Base 100: %{{y:.2f}}<extra></extra>"
            ))
    fig.add_trace(go.Scatter(
        x=df_plot.index, y=df_plot['MA9'],
        name="MA9 Brent", line=dict(color='#ffffff', width=1, dash='dot'),
        hovertemplate="MA9: %{y:.2f}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=df_plot.index, y=df_plot['MA21'],
        name="MA21 Brent", line=dict(color='#ff8c00', width=1.5),
        hovertemplate="MA21: %{y:.2f}<extra></extra>"
    ))

    fig.update_layout(
        template="plotly_dark",
        height=420,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='#060a0f',
        plot_bgcolor='#060a0f',
        yaxis=dict(
            side="right", gridcolor="#0d1a24",
            tickfont=dict(family='Share Tech Mono', size=10, color='#4a7a9b')
        ),
        xaxis=dict(
            gridcolor="#0d1a24",
            tickfont=dict(family='Share Tech Mono', size=10, color='#4a7a9b')
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            font=dict(family='Share Tech Mono', size=10, color='#c8d8e8'),
            bgcolor='rgba(6,10,15,0.8)', bordercolor='#1a3a4a', borderwidth=1
        ),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Infra Table
    st.markdown('<div class="section-header">Infraestrutura Crítica · Alvos de Alto Impacto</div>', unsafe_allow_html=True)

    infra = [
        ("Kharg Island",       "Terminal de Exportação", "160mn bbl/mês", "90%",  "CRÍTICO"),
        ("Ahvaz",              "Campo Petrolífero",       "945k bpd",       "85%",  "CRÍTICO"),
        ("Abadan",             "Refinaria",               "500k bpd",       "70%",  "ALTO"),
        ("Gachsaran",          "Campo Petrolífero",       "560k bpd",       "65%",  "ALTO"),
        ("Isfahan",            "Refinaria",               "375k bpd",       "55%",  "ALTO"),
        ("Bandar Abbas",       "Refinaria",               "320k bpd",       "45%",  "MÉDIO"),
        ("Marun",              "Campo Petrolífero",       "520k bpd",       "60%",  "ALTO"),
        ("Estreito de Hormuz", "Rota de Exportação",      "17mn bpd",       "100%", "CRÍTICO"),
    ]

    table_html = """
    <table class="infra-table">
      <thead>
        <tr>
          <th>ATIVO</th><th>TIPO</th><th>CAPACIDADE</th><th>EXP. GLOBAL</th><th>IMPACTO</th>
        </tr>
      </thead>
      <tbody>
    """
    for row in infra:
        badge_class = "badge-critical" if row[4] == "CRÍTICO" else ("badge-high" if row[4] == "ALTO" else "badge-medium")
        table_html += f"""
        <tr>
          <td style="color:#e8f4ff;font-weight:600">{row[0]}</td>
          <td>{row[1]}</td>
          <td style="color:#ffd700">{row[2]}</td>
          <td>{row[3]}</td>
          <td><span class="badge {badge_class}">{row[4]}</span></td>
        </tr>"""
    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)

# ─── INTEL PANEL ─────────────────────────────────────────────────────────────
with col_intel:
    sources = [
        ("JavierBlas",       "Commodities · Bloomberg"),
        ("staunovo",         "Oil Market · UBS"),
        ("TankerTrackers",   "Tanker Intelligence"),
        ("Osint613",         "OSINT · Geopolítica"),
        ("sentdefender",     "Intel · Conflitos"),
        ("israelnewspulse",  "Notícias · Israel"),
        ("zerohedge",        "Macro · Markets"),
        ("realDonaldTrump",  "Político · EUA"),
        ("hoje_no",          "Notícias · Brasil"),
        ("cbjom",            "Análise · Energia"),
        ("DeItaone",         "Headlines · Rápido"),
    ]

    st.markdown("""
    <div class="section-header">Intel Feed · Fontes X/Twitter</div>
    <div class="intel-panel">
      <div class="intel-header">
        <span style="font-family:'Share Tech Mono',monospace;font-size:11px;letter-spacing:2px;color:#c8d8e8;">
          11 FONTES MONITORADAS
        </span>
        <span class="intel-live"><span class="intel-dot"></span>AO VIVO</span>
      </div>
    """, unsafe_allow_html=True)

    sources_html = ""
    for handle, tag in sources:
        sources_html += f"""
        <div class="source-card">
          <div>
            <a class="source-handle" href="https://twitter.com/{handle}" target="_blank">@{handle}</a>
            <div class="source-tag">{tag}</div>
          </div>
          <span class="source-arrow">→</span>
        </div>"""

    st.markdown(sources_html + "</div>", unsafe_allow_html=True)

    # Quick access buttons
    st.markdown('<div style="margin-top:12px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Acesso Rápido</div>', unsafe_allow_html=True)

    quick_links = {
        "🗺 TankerTrackers Map": "https://www.tankertracker.com",
        "📡 MarineTraffic": "https://www.marinetraffic.com",
        "📰 Reuters Oil": "https://www.reuters.com/business/energy/",
        "🛢 EIA Reports": "https://www.eia.gov/petroleum/",
        "📊 OPEC Monitor": "https://www.opec.org/opec_web/en/publications/338.htm",
    }
    for label, url in quick_links.items():
        st.markdown(
            f'<a href="{url}" target="_blank" style="display:block;padding:7px 12px;margin-bottom:4px;'
            f'background:#0d1a24;border:1px solid #1a3a4a;border-left:2px solid #00aaff;'
            f'color:#00aaff;font-family:Share Tech Mono,monospace;font-size:11px;'
            f'text-decoration:none;letter-spacing:1px;">{label}</a>',
            unsafe_allow_html=True
        )

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:20px;padding-top:10px;border-top:1px solid #1a3a4a;
     font-family:'Share Tech Mono',monospace;font-size:10px;color:#2a4a5a;
     display:flex;justify-content:space-between;">
  <span>IRAN OIL WAR ROOM · v2.0 · DADOS: YAHOO FINANCE</span>
  <span>INTEL: X/TWITTER FEEDS · ATUALIZAÇÃO: 60s</span>
  <span>⚠ APENAS PARA FINS INFORMATIVOS</span>
</div>
""", unsafe_allow_html=True)
