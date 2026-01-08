import streamlit as st
import pandas as pd
import numpy as np

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Guia Streamlit", layout="wide")

# --- 2. CACHE (Para funções pesadas) ---
@st.cache_data
def carregar_dados_pesados():
    # Simula o carregamento de um DataFrame
    df = pd.DataFrame(
        np.random.randn(10, 2),
        columns=['Vendas', 'Metas']
    )
    return df

# --- 3. SESSION STATE (Memória do usuário) ---
if 'contador' not in st.session_state:
    st.session_state['contador'] = 0

# --- 4. BARRA LATERAL (Filtros e Inputs) ---
with st.sidebar:
    st.header("Configurações")
    nome_usuario = st.text_input("Qual seu nome?", "Visitante")
    
    if st.button("Incrementar Contador"):
        st.session_state['contador'] += 1
        
    st.divider()
    st.write(f"Olá, **{nome_usuario}**!")
    st.write(f"Você clicou {st.session_state['contador']} vezes.")

# --- 5. CORPO PRINCIPAL (Layout e Gráficos) ---
st.title("🚀 Painel de Controle Streamlit")

# Usando Colunas para métricas
c1, c2 = st.columns(2)
dados = carregar_dados_pesados()

with c1:
    st.metric(label="Total de Vendas", value=f"{dados['Vendas'].sum():.2f}", delta="12%")

with c2:
    st.metric(label="Meta Alcançada", value="67%", delta="-5%")

# Usando Abas para organizar o conteúdo
aba_grafico, aba_tabela = st.tabs(["📊 Visualização", "📋 Dados Brutos"])

with aba_grafico:
    st.subheader("Desempenho Semanal")
    st.line_chart(dados)

with aba_tabela:
    st.subheader("Detalhamento dos Dados")
    st.dataframe(dados, use_container_width=True)

# Dica de Debug: Mostra tudo que está na memória
with st.expander("🔍 Ver Session State (Debug)"):
    st.write(st.session_state)