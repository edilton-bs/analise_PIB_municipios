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

uf = st.sidebar.selectbox(
    "UF",
    ["Todas", "SP", "RJ", "MG", "BA"]
)

if uf != "Todas":
    modo = st.sidebar.radio(
        "Modo de visualização",
        ["Município único", "Comparar municípios"]
    )

    # ===============================
    # DADOS MOCK (layout)
    # ===============================
    df = pd.DataFrame({
        "Município": ["Município A", "Município B", "Município C", "Município D"],
        "UF": ["SP", "RJ", "MG", "BA"]
    })

    municipios = sorted(df["Município"].unique())

    if modo == "Município único":
        municipio_sel = st.sidebar.selectbox("Município", municipios)
    else:
        municipios_sel = st.sidebar.multiselect(
            "Municípios para comparação",
            municipios,
            default=municipios[:2]
        )
else:
    modo = "UFs"

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

if modo == "Município único" or modo == "UFs":
    st.subheader(f"📌 Indicadores-chave - {municipio_sel}")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        f"PIB Total ({ano_ref})",
        "R$ 2,3 bi",
        "+5,2% vs ano anterior"
    )

    col2.metric(
        f"PIB per capita ({ano_ref})",
        "R$ 32.500",
        "+3,1% vs ano anterior"
    )

    col3.metric(
        "Crescimento acumulado",
        "68%",
        "2010 → 2023"
    )

    col4.metric(
        "Participação do Setor Público",
        "41%",
        "Alta"
    )

# ===============================
# EVOLUÇÃO TEMPORAL
# ===============================
st.markdown("---")
st.subheader("📊 Evolução Econômica")

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
    else:
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
# COMPARAÇÃO ENTRE MUNICÍPIOS
# ===============================
if modo == "Comparar municípios" and len(municipios_sel) > 1:
    st.markdown("---")
    st.subheader("🔍 Comparação Direta entre Municípios")

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
# RODAPÉ
# ===============================
st.markdown("---")
st.caption("Dashboard desenvolvido em Streamlit • Dados: IBGE")
