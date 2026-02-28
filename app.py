import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Configuração e Refresh (60 segundos para bater com o gráfico de 1m)
st.set_page_config(page_title="Terminal Oil Iran", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=60000, key="f5_refresh")

st.title("🛢️ Iran Oil Terminal | Alta Frequência")

# 2. Dados de Alta Frequência (1 Minuto)
# Pegamos os últimos 2 dias com intervalo de 1m para garantir liquidez no gráfico
@st.cache_data(ttl=60)
def carregar_dados():
    tickers = {"BZ=F": "Brent", "PETR4.SA": "PETR4", "PRIO3.SA": "PRIO3", "GC=F": "Ouro"}
    df = yf.download(list(tickers.keys()), period="2d", interval="1m", progress=False)['Close'].ffill()
    # Normalização Base 100 (Início do dia atual ou última sessão)
    df_norm = (df / df.iloc[0]) * 100
    return df, df_norm, tickers

df_raw, df_plot, ticker_map = carregar_dados()

# 3. Layout Principal
col_chart, col_intel = st.columns([2, 1])

with col_chart:
    st.subheader("📊 Intraday Relativo (Base 100 - High Frequency)")
    
    fig = go.Figure()
    for t, nome in ticker_map.items():
        fig.add_trace(go.Scatter(
            x=df_plot.index, 
            y=df_plot[t], 
            name=nome,
            line=dict(width=2),
            hovertemplate='%{y:.2f}%<extra></extra>'
        ))
    
    # Ajuste de Escala para "Aumentar" a percepção de variação
    ymax = df_plot.max().max() + 0.5
    ymin = df_plot.min().min() - 0.5
    
    fig.update_layout(
        template="plotly_dark",
        height=550,
        margin=dict(l=0, r=0, t=20, b=0),
        yaxis=dict(range=[ymin, ymax], side="right", gridcolor="#333"),
        xaxis=dict(showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Mini Tabela de Preços Atuais
    st.write("---")
    cols = st.columns(4)
    for i, (t, nome) in enumerate(ticker_map.items()):
        atual = df_raw[t].iloc[-1]
        var = ((atual - df_raw[t].iloc[0]) / df_raw[t].iloc[0]) * 100
        cols[i].metric(nome, f"{atual:.2f}", f"{var:.2f}%")

with col_intel:
    st.subheader("🐦 Live Intelligence (X)")
    
    # Lista de fontes que você definiu
    fontes = ["JavierBlas", "TankerTrackers", "DeItaone", "sentdefender", "staunovo", "zerohedge"]
    
    # Criando abas para não sobrecarregar o site e mostrar os tweets reais
    tabs = st.tabs([f"@{f}" for f in fontes])
    
    for i, tab in enumerate(tabs):
        with tab:
            user = fontes[i]
            # Script oficial do X para Embeds que realmente carregam
            html_code = f"""
            <div style="height: 600px; overflow-y: scroll;">
                <a class="twitter-timeline" data-theme="dark" href="https://twitter.com/{user}?ref_src=twsrc%5Etfw">
                    Carregando tweets de @{user}...
                </a>
                <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
            </div>
            """
            st.components.v1.html(html_code, height=600)
