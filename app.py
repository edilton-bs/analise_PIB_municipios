import streamlit as st
import plotly.express as px
import pandas as pd


# ===============================
# CONFIGURAÇÃO DA PÁGINA
# ===============================
st.set_page_config(
    page_title="PIB dos Municípios | IBGE",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ===============================
# SIDEBAR — FILTROS
# ===============================
st.sidebar.title("📊 Filtros de Análise")


ano_intervalo = st.sidebar.slider(
    "Período de análise",
    2010, 2023,
    (2010, 2023)
)


ano_ref = st.sidebar.selectbox(
    "Ano de referência (análises pontuais)",
    list(range(ano_intervalo[0], ano_intervalo[1] + 1)),
    index=len(range(ano_intervalo[0], ano_intervalo[1] + 1)) - 1
)


regiao = st.sidebar.selectbox(
    "Região",
    ["Brasil", "Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]
)

if regiao != "Brasil":
    uf = st.sidebar.selectbox(
        "UF",
        {
            "Norte": ["Todas", "AC", "AP", "AM", "PA", "RO", "RR", "TO"],
            "Nordeste": ["Todas", "AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
            "Sudeste": ["Todas", "ES", "MG", "RJ", "SP"],
            "Sul": ["Todas", "PR", "RS", "SC"],
            "Centro-Oeste": ["Todas", "DF", "GO", "MT", "MS"]
        }[regiao]
    )
else:
    uf = st.sidebar.selectbox(
        "UF",
        ["Todas", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
         "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS",
         "RO", "RR", "SC", "SP", "SE", "TO"]
    )



# ===============================
# DADOS MOCK (layout)
# ===============================
df = pd.DataFrame({
    "Município": ["Município A", "Município B", "Município C", "Município D"],
    "UF": ["SP", "RJ", "MG", "BA"]
})

# Lista de UFs para comparação
lista_ufs = ["SP", "RJ", "MG", "BA", "RS", "PR", "SC", "PE", "CE"]


# Determinar modo de visualização baseado na seleção de UF
if uf != "Todas" and len(uf) == 2:  # UF específica
    modo = st.sidebar.radio(
        "Modo de visualização",
        ["Todos os municípios", "Município único", "Comparar municípios"]
    )
    
    municipios = sorted(df["Município"].unique())
    
    if modo == "Município único":
        municipio_sel = st.sidebar.selectbox("Município", municipios)
    elif modo == "Comparar municípios":
        municipios_sel = st.sidebar.multiselect(
            "Municípios para comparação",
            municipios,
            default=municipios[:2]
        )
else:  # Todas as UFs ou região
    modo = "Agregado"


st.sidebar.markdown("---")
st.sidebar.caption("Fonte: IBGE")


# ===============================
# TÍTULO
# ===============================
st.title("📈 PIB dos Municípios Brasileiros")
st.caption("Análise econômica municipal • 2010–2023")


# ===============================
# KPIs — VISÃO EXECUTIVA
# ===============================

if modo == "Município único":
    st.subheader(f"📌 Indicadores-chave - {municipio_sel}")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric(
        f"PIB Total ({ano_ref})",
        "R$ 2,3 bi",
        "+5,2% vs ano anterior"
    )

    col2.metric(
        f"População ({ano_ref})",
        "70.000",
        "+1,5% vs ano anterior"
    )
    
    col3.metric(
        f"PIB per capita ({ano_ref})",
        "R$ 32.500",
        "+3,1% vs ano anterior"
    )
    
    col4.metric(
        "Crescimento acumulado",
        "68%",
        "2010 → 2023"
    )
    
    col5.metric(
        "Participação do Setor Público",
        "41%",
        "Alta"
    )

elif modo == "Todos os municípios":
    st.subheader(f"📌 Indicadores-chave - {uf} (Todos os municípios)")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric(
        f"PIB Total ({ano_ref})",
        "R$ 128,5 bi",
        "+4,5% vs ano anterior"
    )

    col2.metric(
        f"População total ({ano_ref})",
        "8.500.000",
        "+1,2% vs ano anterior"
    )
    
    col3.metric(
        f"PIB per capita médio ({ano_ref})",
        "R$ 35.800",
        "+3,2% vs ano anterior"
    )
    
    col4.metric(
        "Crescimento acumulado",
        "71%",
        "2010 → 2023"
    )
    
    col5.metric(
        "Número de municípios",
        f"{len(municipios)}",
        f"{uf}"
    )

elif modo == "Agregado":
    # Título dinâmico baseado na seleção
    if uf == "Todas":
        titulo_contexto = f"{regiao}"
    else:
        titulo_contexto = f"{uf}"
    
    st.subheader(f"📌 Indicadores-chave - {titulo_contexto}")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric(
        f"PIB Total ({ano_ref})",
        "R$ 457,8 bi",
        "+4,8% vs ano anterior"
    )

    col2.metric(
        f"População total ({ano_ref})",
        "55.000.000",
        "+1,3% vs ano anterior"
    )
    
    col3.metric(
        f"PIB per capita médio ({ano_ref})",
        "R$ 38.200",
        "+3,5% vs ano anterior"
    )
    
    col4.metric(
        "Crescimento acumulado",
        "72%",
        "2010 → 2023"
    )
    
    col5.metric(
        "Número de municípios",
        "5.570",
        "Brasil"
    )


# ===============================
# EVOLUÇÃO TEMPORAL
# ===============================
st.markdown("---")
st.subheader("📊 Evolução Econômica")
st.caption("Variação do PIB ao longo do tempo, ajustada ao nível de agregação selecionado")


col5, col6 = st.columns(2)


with col5:
    st.markdown("**Evolução do PIB ao longo do tempo**")
    
    if modo == "Município único":
        df_line = pd.DataFrame({
            "Ano": list(range(2010, 2024)),
            "PIB": [i * 10 for i in range(14)]
        })
        
        fig_line = px.line(
            df_line,
            x="Ano",
            y="PIB",
            markers=True
        )
        
    elif modo == "Comparar municípios":
        df_line = pd.DataFrame({
            "Ano": list(range(2010, 2024)) * len(municipios_sel),
            "Município": [m for m in municipios_sel for _ in range(14)],
            "PIB": [i * 10 * (1 + idx * 0.3)
                    for idx, m in enumerate(municipios_sel)
                    for i in range(14)]
        })
        
        fig_line = px.line(
            df_line,
            x="Ano",
            y="PIB",
            color="Município",
            markers=True
        )
    
    elif modo == "Todos os municípios":
        # Top municípios da UF (até 5)
        top_mun = municipios[:min(5, len(municipios))]
        n_mun = len(top_mun)
        
        df_line = pd.DataFrame({
            "Ano": list(range(2010, 2024)) * n_mun,
            "Município": [m for m in top_mun for _ in range(14)],
            "PIB (R$ bi)": [i * 2 * (1 + idx * 0.4)
                    for idx in range(n_mun)
                    for i in range(14)]
        })
        
        fig_line = px.line(
            df_line,
            x="Ano",
            y="PIB (R$ bi)",
            color="Município",
            markers=True,
            title=f"Top {n_mun} municípios por PIB"
        )
        
    else:  # Modo Agregado
        # Comparação entre UFs ou regiões
        df_line = pd.DataFrame({
            "Ano": list(range(2010, 2024)) * 5,
            "UF": [uf_nome for uf_nome in lista_ufs[:5] for _ in range(14)],
            "PIB (R$ bi)": [i * 15 * (1 + idx * 0.4)
                    for idx in range(5)
                    for i in range(14)]
        })
        
        fig_line = px.line(
            df_line,
            x="Ano",
            y="PIB (R$ bi)",
            color="UF",
            markers=True,
            title="Top 5 UFs por PIB"
        )
    
    st.plotly_chart(fig_line, use_container_width=True)


with col6:
    st.markdown("**Estrutura do Valor Adicionado (2010–2023)**")
    
    df_area = pd.DataFrame({
        "Ano": list(range(2010, 2024)),
        "Agropecuária": [10]*14,
        "Indústria": [20]*14,
        "Serviços": [40]*14,
        "Administração Pública": [30]*14
    })
    
    fig_area = px.area(
        df_area,
        x="Ano",
        y=df_area.columns[1:]
    )
    
    st.plotly_chart(fig_area, use_container_width=True)


# ===============================
# COMPOSIÇÃO DO PIB (ANO REF)
# ===============================
if modo == "Município único":
    st.markdown("---")
    st.subheader(f"🧩 Composição do PIB — {ano_ref}")
    st.caption("Estrutura setorial e posicionamento relativo do município")
    
    col7, col8 = st.columns(2)
    
    with col7:
        df_donut = pd.DataFrame({
            "Setor": ["Agropecuária", "Indústria", "Serviços", "Administração Pública"],
            "Participação (%)": [10, 20, 40, 30]
        })
        
        fig_donut = px.pie(
            df_donut,
            names="Setor",
            values="Participação (%)",
            hole=0.5
        )
        
        st.plotly_chart(fig_donut, use_container_width=True)
    
    with col8:
        st.markdown("### 🧠 Escala econômica vs renda")
        st.caption(
            "Comparação do município selecionado com outros municípios da mesma UF, "
            "avaliando relação entre tamanho da economia, renda média e dependência pública."
        )
        
        df_scatter = pd.DataFrame({
            "Município": municipios,
            "PIB Total": [1000, 2000, 1500, 2500],
            "PIB per capita": [28000, 32000, 30000, 35000],
            "Dependência Pública (%)": [30, 45, 40, 25]
        })
        
        fig_scatter = px.scatter(
            df_scatter,
            x="PIB Total",
            y="PIB per capita",
            size="Dependência Pública (%)",
            color="Município",
            size_max=40
        )
        
        st.plotly_chart(fig_scatter, use_container_width=True)


# ===============================
# TODOS OS MUNICÍPIOS (UF)
# ===============================
if modo == "Todos os municípios":
    st.markdown("---")
    st.subheader(f"🏙️ Análise dos Municípios de {uf}")
    st.caption("Rankings, distribuições e indicadores detalhados dos municípios da UF selecionada")
    
    col_todos1, col_todos2 = st.columns(2)
    
    with col_todos1:
        st.markdown("**Ranking: PIB Total**")
        df_ranking_mun = pd.DataFrame({
            "Município": municipios,
            "PIB Total (R$ mi)": [2500, 1800, 1500, 1200]
        }).sort_values("PIB Total (R$ mi)", ascending=True)
        
        fig_ranking_mun = px.bar(
            df_ranking_mun,
            y="Município",
            x="PIB Total (R$ mi)",
            orientation='h',
            text_auto=True
        )
        
        st.plotly_chart(fig_ranking_mun, use_container_width=True)
    
    with col_todos2:
        st.markdown("**Ranking: PIB per capita**")
        df_ranking_pc = pd.DataFrame({
            "Município": municipios,
            "PIB per capita (R$)": [45000, 38000, 32000, 28000]
        }).sort_values("PIB per capita (R$)", ascending=True)
        
        fig_ranking_pc = px.bar(
            df_ranking_pc,
            y="Município",
            x="PIB per capita (R$)",
            orientation='h',
            text_auto=True,
            color="PIB per capita (R$)",
            color_continuous_scale="Viridis"
        )
        
        st.plotly_chart(fig_ranking_pc, use_container_width=True)
    
    # Distribuição e análise
    st.markdown("---")
    col_dist1, col_dist2 = st.columns(2)
    
    with col_dist1:
        st.markdown("**Distribuição setorial média**")
        df_setores_uf = pd.DataFrame({
            "Setor": ["Agropecuária", "Indústria", "Serviços", "Administração Pública"],
            "Participação (%)": [12, 25, 42, 21]
        })
        
        fig_setores_uf = px.pie(
            df_setores_uf,
            names="Setor",
            values="Participação (%)",
            hole=0.5
        )
        
        st.plotly_chart(fig_setores_uf, use_container_width=True)
    
    with col_dist2:
        st.markdown("**Distribuição do PIB per capita**")
        df_hist = pd.DataFrame({
            "PIB per capita (R$)": [25000, 28000, 32000, 35000, 38000, 42000, 45000, 48000]
        })
        
        fig_hist = px.histogram(
            df_hist,
            x="PIB per capita (R$)",
            nbins=10,
            title="Frequência"
        )
        
        st.plotly_chart(fig_hist, use_container_width=True)
    
    # Tabela detalhada
    st.markdown("**📋 Tabela Detalhada - Municípios de {} ({} municípios)**".format(uf, len(municipios)))
    df_table_todos = pd.DataFrame({
        "Município": municipios,
        "PIB Total (R$ mi)": [2500, 1800, 1500, 1200],
        "PIB per capita (R$)": [45000, 38000, 32000, 28000],
        "Dependência Pública (%)": [28, 35, 42, 38],
        "Crescimento 2010–2023": ["75%", "68%", "72%", "65%"],
        "Setor Dominante": ["Serviços", "Indústria", "Serviços", "Administração Pública"],
        "População": ["850K", "420K", "320K", "280K"]
    })
    
    st.dataframe(df_table_todos, use_container_width=True)


# ===============================
# COMPARAÇÃO ENTRE MUNICÍPIOS
# ===============================
if modo == "Comparar municípios" and len(municipios_sel) > 1:
    st.markdown("---")
    st.subheader("🔍 Comparação Direta entre Municípios")
    st.caption("Análise lado a lado dos municípios selecionados para identificar diferenças e padrões")
    
    col9, col10 = st.columns(2)
    
    with col9:
        st.markdown("**PIB Total**")
        df_bar_pib = pd.DataFrame({
            "Município": municipios_sel,
            "PIB Total (R$ mi)": [1000 + i*600 for i in range(len(municipios_sel))]
        })
        
        fig_bar = px.bar(
            df_bar_pib,
            x="Município",
            y="PIB Total (R$ mi)",
            text_auto=True
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col10:
        st.markdown("**PIB per capita**")
        df_bar_pc = pd.DataFrame({
            "Município": municipios_sel,
            "PIB per capita (R$)": [25000 + i*5000 for i in range(len(municipios_sel))]
        })
        
        fig_bar_pc = px.bar(
            df_bar_pc,
            x="Município",
            y="PIB per capita (R$)",
            text_auto=True
        )
        
        st.plotly_chart(fig_bar_pc, use_container_width=True)
    
    st.markdown("**Tabela Comparativa Consolidada**")
    df_table = pd.DataFrame({
        "Município": municipios_sel,
        "PIB Total (R$ mi)": [1000 + i*600 for i in range(len(municipios_sel))],
        "PIB per capita (R$)": [25000 + i*5000 for i in range(len(municipios_sel))],
        "Dependência Pública (%)": [35 + i*5 for i in range(len(municipios_sel))],
        "Crescimento 2010–2023": [f"{60 + i*8}%" for i in range(len(municipios_sel))],
        "Setor Dominante": ["Serviços", "Indústria", "Administração Pública", "Agropecuária"][:len(municipios_sel)]
    })
    
    st.dataframe(df_table, use_container_width=True)


# ===============================
# VISUALIZAÇÕES AGREGADAS (UFs/REGIÕES)
# ===============================
if modo == "Agregado":
    st.markdown("---")
    st.subheader(f"🗺️ Análise Comparativa entre UFs — {ano_ref}")
    st.caption("Visão panorâmica da distribuição econômica regional e setorial")
    
    # Bloco Principal 1: Rankings
    col11, col12 = st.columns(2)
    
    with col11:
        st.markdown("**Ranking de PIB por UF**")
        df_ranking = pd.DataFrame({
            "UF": lista_ufs,
            "PIB Total (R$ bi)": [450, 380, 320, 280, 250, 220, 190, 160, 140]
        }).sort_values("PIB Total (R$ bi)", ascending=True)
        
        fig_ranking = px.bar(
            df_ranking,
            y="UF",
            x="PIB Total (R$ bi)",
            orientation='h',
            text_auto=True
        )
        
        st.plotly_chart(fig_ranking, use_container_width=True)
    
    with col12:
        st.markdown("**PIB per capita por UF**")
        df_per_capita = pd.DataFrame({
            "UF": lista_ufs,
            "PIB per capita (R$)": [52000, 48000, 42000, 38000, 35000, 33000, 31000, 28000, 25000]
        }).sort_values("PIB per capita (R$)", ascending=True)
        
        fig_per_capita = px.bar(
            df_per_capita,
            y="UF",
            x="PIB per capita (R$)",
            orientation='h',
            text_auto=True,
            color="PIB per capita (R$)",
            color_continuous_scale="Blues"
        )
        
        st.plotly_chart(fig_per_capita, use_container_width=True)
    
    # Bloco Principal 2: Análise de Relação (Scatter)
    st.markdown("---")
    st.markdown("**📊 Relação: Tamanho da Economia vs Renda Média**")
    st.caption("Cada ponto representa uma UF. Tamanho indica número de municípios.")
    
    df_scatter_ufs = pd.DataFrame({
        "UF": lista_ufs,
        "PIB Total (R$ bi)": [450, 380, 320, 280, 250, 220, 190, 160, 140],
        "PIB per capita (R$)": [52000, 48000, 42000, 38000, 35000, 33000, 31000, 28000, 25000],
        "Nº Municípios": [645, 92, 853, 417, 497, 399, 295, 185, 184]
    })
    
    fig_scatter_ufs = px.scatter(
        df_scatter_ufs,
        x="PIB Total (R$ bi)",
        y="PIB per capita (R$)",
        size="Nº Municípios",
        color="UF",
        text="UF",
        size_max=50
    )
    fig_scatter_ufs.update_traces(textposition='top center')
    st.plotly_chart(fig_scatter_ufs, use_container_width=True)
    
    # Análises Avançadas (em Tabs)
    st.markdown("---")
    tab1, tab2 = st.tabs(["📋 Tabela Detalhada", "🧩 Composição Setorial"])
    
    with tab1:
        st.markdown("**Dados Consolidados por UF**")
        df_table_ufs = pd.DataFrame({
            "UF": lista_ufs,
            "PIB Total (R$ bi)": [450, 380, 320, 280, 250, 220, 190, 160, 140],
            "PIB per capita (R$)": [52000, 48000, 42000, 38000, 35000, 33000, 31000, 28000, 25000],
            "Crescimento 2010–2023": ["78%", "72%", "68%", "65%", "70%", "73%", "69%", "64%", "62%"],
            "Setor Dominante": ["Serviços", "Serviços", "Indústria", "Serviços", "Agropecuária", 
                                "Serviços", "Indústria", "Serviços", "Adm. Pública"],
            "Nº Municípios": [645, 92, 853, 417, 497, 399, 295, 185, 184]
        })
        
        st.dataframe(df_table_ufs, use_container_width=True)
    
    with tab2:
        col_tab1, col_tab2 = st.columns(2)
        
        with col_tab1:
            st.markdown("**Distribuição setorial média**")
            df_setores_agg = pd.DataFrame({
                "Setor": ["Agropecuária", "Indústria", "Serviços", "Administração Pública"],
                "Participação (%)": [8, 22, 48, 22]
            })
            
            fig_setores = px.pie(
                df_setores_agg,
                names="Setor",
                values="Participação (%)",
                hole=0.5
            )
            
            st.plotly_chart(fig_setores, use_container_width=True)
        
        with col_tab2:
            st.markdown("**Participação setorial por UF**")
            df_stacked = pd.DataFrame({
                "UF": lista_ufs[:5] * 4,
                "Setor": ["Agropecuária"]*5 + ["Indústria"]*5 + ["Serviços"]*5 + ["Adm. Pública"]*5,
                "Valor (%)": [5, 8, 12, 15, 7, 25, 22, 18, 20, 23, 50, 48, 45, 42, 47, 20, 22, 25, 23, 23]
            })
            
            fig_stacked = px.bar(
                df_stacked,
                x="UF",
                y="Valor (%)",
                color="Setor",
                text_auto=True
            )
            
            st.plotly_chart(fig_stacked, use_container_width=True)


# ===============================
# RODAPÉ
# ===============================
st.markdown("---")
st.caption("Dashboard desenvolvido em Streamlit • Dados: IBGE")
