import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import google.generativeai as genai
from streamlit_autorefresh import st_autorefresh

# Configurações de IA e Segurança
GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Layout da Página
st.set_page_config(page_title="Iran Oil Monitor", layout="wide")
st_autorefresh(interval=60000, key="f5") # Atualiza a cada 1 min

st.title("🛢️ Iran Geopolitical & Oil Terminal")

col_main, col_side = st.columns([2, 1])

with col_main:
    # Gráfico Base 100
    st.subheader("Performance Relativa (Base 100)")
    tickers = {"BZ=F": "Brent", "PETR4.SA": "PETR4", "PRIO3.SA": "PRIO3", "GC=F": "Ouro"}
    data = yf.download(list(tickers.keys()), period="5d")['Close'].ffill()
    df_norm = (data / data.iloc[0]) * 100
    
    fig = go.Figure()
    for t, nome in tickers.items():
        fig.add_trace(go.Scatter(x=df_norm.index, y=df_norm[t], name=nome))
    fig.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Tabela de Infraestrutura
    st.subheader("📍 Monitor de Ativos")
    st.dataframe(pd.read_csv("infra_iran.csv"), use_container_width=True)

with col_side:
    st.subheader("🐦 Fontes de Inteligência (X)")
    perfis = ["JavierBlas", "TankerTrackers", "DeItaone", "sentdefender"]
    user = st.selectbox("Selecione a Fonte:", perfis)
    html = f'<a class="twitter-timeline" data-height="600" data-theme="dark" href="https://twitter.com/{user}"></a> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>'
    st.components.v1.html(html, height=600, scrolling=True)
