import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Configuração e Auto-Refresh
st.set_page_config(page_title="Terminal Oil Iran", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=300000, key="f5_refresh") # Refresh a cada 5 min (ideal para 15 dias)

st.title("🛢️ Iran Oil Terminal | Análise 15 Dias")

# 2. Carregamento de Dados (15 Dias com Médias Móveis)
@st.cache_data(ttl=300)
def carregar_dados_avancados():
    tickers = {"BZ=F": "Brent", "PETR4.SA": "PETR4", "PRIO3.SA": "PRIO3", "GC=F": "Ouro"}
    # Usamos intervalo de 1h para equilibrar detalhe e performance em 15 dias
    df = yf.download(list(tickers.keys()), period="15d", interval="1h", progress=False)['Close'].ffill()
    
    # Normalização Base 100
    df_norm = (df / df.iloc[0]) * 100
    
    # Cálculo de Médias Móveis (Base 100) para o Brent como referência
    df_norm['MA9'] = df_norm['BZ=F'].rolling(window=9).mean()
    df_norm['MA21'] = df_norm['BZ=F'].rolling(window=21).mean()
    
    return df, df_norm, tickers

df_raw, df_plot, ticker_map = carregar_dados_avancados()

# 3. Layout Principal
col_chart, col_intel = st.columns([2.2, 0.8])

with col_chart:
    st.subheader("📊 Performance 15D (Base 100) + Médias Móveis")
    
    fig = go.Figure()
    
    # Ativos Principais
    for t, nome in ticker_map.items():
        fig.add_trace(go.Scatter(
            x=df_plot.index, y=df_plot[t], name=nome,
            line=dict(width=2),
            hovertemplate='%{y:.2f}%<extra></extra>'
        ))
    
    # Linhas de Médias Móveis (Foco no Brent)
    fig.add_trace(go.Scatter(
        x=df_plot.index, y=df_plot['MA9'], name="MA9 (Brent)",
        line=dict(color='rgba(255, 255, 255, 0.5)', width=1, dash='dot')
    ))
    fig.add_trace(go.Scatter(
        x=df_plot.index, y=df_plot['MA21'], name="MA21 (Brent)",
        line=dict(color='rgba(255, 165, 0, 0.6)', width=1.5)
    ))

    fig.update_layout(
        template="plotly_dark", height=600,
        margin=dict(l=0, r=0, t=30, b=0),
        yaxis=dict(side="right", gridcolor="#333", title="Variação %"),
        xaxis=dict(showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Métricas de 15 Dias
    st.write("---")
    m1, m2, m3, m4 = st.columns(4)
    for i, (t, nome) in enumerate(ticker_map.items()):
        atual = df_raw[t].iloc[-1]
        inicio = df_raw[t].iloc[0]
        var_periodo = ((atual - inicio) / inicio) * 100
        [m1, m2, m3, m4][i].metric(nome, f"{atual:.2f}", f"{var_periodo:.2f}% (15d)")

with col_intel:
    st.subheader("🐦 Intelligence (X)")
    st.info("Caso a conexão falhe, clique no link direto da fonte abaixo.")
    
    fontes = ["JavierBlas", "TankerTrackers", "DeItaone", "sentdefender"]
    escolha = st.radio("Fonte ativa:", fontes, horizontal=True)
    
    # Solução para o erro de conexão recusada
    # Usando um iframe com sandbox e script de carregamento forçado
    twitter_widget = f"""
    <div style="height: 750px; overflow-y: auto; background-color: #161a21; border-radius: 10px; padding: 10px;">
        <a class="twitter-timeline" data-theme="dark" href="https://twitter.com/{escolha}?ref_src=twsrc%5Etfw">
            Tweets by @{escolha}
        </a>
        <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
    </div>
    """
    st.components.v1.html(twitter_widget, height=800)
