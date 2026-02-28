import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Setup da Página
st.set_page_config(page_title="Terminal Oil Iran", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=60000, key="f5_refresh") # Refresh a cada 1 min

st.title("🛢️ Iran Oil Terminal | 5-Day Analysis")

# 2. Carregamento de Dados (5 Dias - Alta Resolução)
@st.cache_data(ttl=60)
def get_market_data():
    # Lista completa de ativos
    tickers = {"BZ=F": "Brent", "GC=F": "Ouro", "PETR4.SA": "PETR4", "PRIO3.SA": "PRIO3"}
    # Usamos 15m para 5 dias para ter um gráfico fluido
    df = yf.download(list(tickers.keys()), period="5d", interval="15m", progress=False)['Close'].ffill()
    
    # Normalização Base 100
    df_norm = (df / df.iloc[0]) * 100
    
    # Médias Móveis para o Brent (Referência de tendência)
    if 'BZ=F' in df_norm.columns:
        df_norm['MA9'] = df_norm['BZ=F'].rolling(window=9).mean()
        df_norm['MA21'] = df_norm['BZ=F'].rolling(window=21).mean()
    
    return df, df_norm, tickers

df_raw, df_plot, ticker_map = get_market_data()

# 3. Layout Principal
col_main, col_x = st.columns([2, 1])

with col_main:
    st.subheader("📊 Performance Relativa 5D + Médias Móveis")
    
    fig = go.Figure()
    
    # Plotar cada ativo que foi baixado com sucesso
    for t in df_plot.columns:
        if t in ticker_map:
            fig.add_trace(go.Scatter(
                x=df_plot.index, y=df_plot[t], name=ticker_map[t],
                line=dict(width=2.5 if t == 'BZ=F' else 1.5)
            ))
    
    # Adicionar Médias Móveis se existirem
    if 'MA9' in df_plot.columns:
        fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MA9'], name="MA9 (Brent)", line=dict(color='gray', dash='dot')))
        fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MA21'], name="MA21 (Brent)", line=dict(color='orange', width=1)))

    fig.update_layout(
        template="plotly_dark", height=500, margin=dict(l=0, r=0, t=30, b=0),
        yaxis=dict(side="right", gridcolor="#333"),
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tabela de Ativos Irã (Baseado na sua foto)
    st.subheader("📍 Infraestrutura Monitorada")
    st.table(pd.read_csv("infra_iran.csv"))

with col_x:
    st.subheader("🐦 Resumo de Inteligência (X)")
    
    # Lista completa das 11 fontes
    fontes = [
        "JavierBlas", "Osint613", "staunovo", "sentdefender", "zerohedge", 
        "realDonaldTrump", "israelnewspulse", "hoje_no", "TankerTrackers", "cbjom", "DeItaone"
    ]
    
    # Aba Resumo Unificado (Scroll infinito com todas as fontes)
    st.info("Role para baixo para ver tweets de todas as fontes.")
    
    # Gerando o HTML para as 11 fontes de uma vez
    html_all_sources = '<div style="height: 800px; overflow-y: scroll; padding: 10px; background-color: #0e1117;">'
    for f in fontes:
        html_all_sources += f"""
        <div style="margin-bottom: 20px; border-bottom: 1px solid #333;">
            <p style="color: #1DA1F2; font-weight: bold;">@ {f}</p>
            <a class="twitter-timeline" data-theme="dark" data-height="400" href="https://twitter.com/{f}?ref_src=twsrc%5Etfw"></a>
        </div>
        """
    html_all_sources += '<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script></div>'
    
    st.components.v1.html(html_all_sources, height=850)
