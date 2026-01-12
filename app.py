import streamlit as st
import plotly.express as px
import pandas as pd
from data import (
    load_data, filtrar_dados, obter_lista_municipios, obter_lista_ufs,
    calcular_kpis_municipio, calcular_kpis_uf, calcular_kpis_agregado, calcular_crescimento_periodo,
    dados_evolucao_pib, dados_evolucao_valor_adicionado,
    ranking_municipios_pib, ranking_municipios_per_capita, ranking_ufs, ranking_ufs_per_capita,
    composicao_setorial_municipio, composicao_setorial_uf, composicao_setorial_agregado,
    scatter_pib_vs_per_capita, scatter_ufs_pib_vs_per_capita,
    tabela_municipios_completa, tabela_ufs_completa
)

# Cores padronizadas para os setores econômicos (mais vibrantes para funcionar em ambos os temas)
CORES_SETORES = {
    "Agropecuária": "#4CAF50",        # Verde vibrante
    "Indústria": "#2196F3",           # Azul vibrante
    "Serviços": "#FF9800",            # Laranja vibrante
    "Administração Pública": "#F44336"  # Vermelho vibrante
}

# Paleta para gráficos de linha/comparação (cores saturadas)
PALETA_COMPARACAO = [
    "#2196F3",  # Azul vibrante
    "#FF9800",  # Laranja vibrante
    "#4CAF50",  # Verde vibrante
    "#F44336",  # Vermelho vibrante
    "#9C27B0",  # Roxo vibrante
    "#795548",  # Marrom vibrante
    "#E91E63",  # Rosa vibrante
    "#607D8B",  # Cinza-azulado
    "#CDDC39",  # Lima
    "#00BCD4"   # Ciano vibrante
]

# Cores para destaque (alto contraste)
COR_REFERENCIA = "#FF5252"    # Vermelho vibrante (destaque)
COR_SECUNDARIA = "#64B5F6"    # Azul claro (neutro)

# ===============================
# CONFIGURAÇÃO DA PÁGINA
# ===============================
st.set_page_config(
    page_title="PIB dos Municípios | IBGE",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ===============================
# CARREGAR DADOS
# ===============================
df = load_data()


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
    ["Brasil", "Norte", "Nordeste", "Sudeste", "Sul", "Centro-oeste"]
)

# Obter lista de UFs baseada na região selecionada
lista_ufs_disponiveis = obter_lista_ufs(df, regiao if regiao != "Brasil" else None)
uf = st.sidebar.selectbox(
    "UF",
    ["Todas"] + lista_ufs_disponiveis
)



# ===============================
# MODO DE VISUALIZAÇÃO E SELEÇÃO DE MUNICÍPIOS
# ===============================

# Determinar modo de visualização baseado na seleção de UF
if uf != "Todas" and len(uf) == 2:  # UF específica
    modo = st.sidebar.radio(
        "Modo de visualização",
        ["Todos os municípios", "Município específico", "Comparar municípios"]
    )
    
    # Obter lista de municípios da UF selecionada
    municipios = obter_lista_municipios(df, uf)
    
    if modo == "Município específico":
        municipio_sel = st.sidebar.selectbox("Município", municipios)
    elif modo == "Comparar municípios":
        municipios_sel = st.sidebar.multiselect(
            "Municípios para comparação",
            municipios,
            default=municipios[:min(2, len(municipios))]
        )
else:  # Todas as UFs ou região
    modo = "Agregado"
    municipios = []


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

if modo == "Município específico":
    st.subheader(f"📌 Indicadores-chave - {municipio_sel}")
    
    # Calcular KPIs usando data.py
    kpis = calcular_kpis_municipio(df, municipio_sel, ano_ref)
    crescimento_periodo = calcular_crescimento_periodo(df, municipio_sel, "nome_municipio", ano_intervalo[0], ano_intervalo[1])
    
    if kpis:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        col1.metric(
            f"PIB Total ({ano_ref})",
            f"R$ {kpis['pib_total']/1000:.1f} mi" if kpis['pib_total'] < 1_000_000 else f"R$ {kpis['pib_total']/1_000_000:.1f} bi",
            f"{kpis['crescimento_ano_anterior']:.1f}% vs ano anterior" if kpis['crescimento_ano_anterior'] else "N/A"
        )

        col2.metric(
            f"População ({ano_ref})",
            f"{kpis['populacao']:,.0f}".replace(",", "."),
            None
        )
        
        col3.metric(
            f"PIB per capita ({ano_ref})",
            f"R$ {kpis['pib_per_capita']:,.0f}".replace(",", "."),
            f"{kpis['cresc_ppc_ano_anterior']:.1f}% vs ano anterior" if kpis['cresc_ppc_ano_anterior'] else "N/A"
        )
        
        col4.metric(
            f"Crescimento acumulado ({ano_intervalo[0]}–{ano_intervalo[1]})",
            f"{crescimento_periodo:.1f}%" if crescimento_periodo else "N/A"
            # f"{ano_intervalo[1]} → {ano_intervalo[0]}" if crescimento_periodo and crescimento_periodo < 0 else f"{ano_intervalo[0]} → {ano_intervalo[1]}",
            # delta_color="normal" if crescimento_periodo and crescimento_periodo > 0 else "inverse"
        )

        ano2 = min(ano_ref, 2021)  # Limitar ao máximo de 2021 para evitar dados inexistentes de VAB
        
        col5.metric(
            f"Participação do Setor Público - {ano2}",
            f"{kpis['dependencia_publica']:.1f}%",
            kpis['setor_dominante']
        )
    else:
        st.warning("Dados não disponíveis para o município selecionado.")

elif modo == "Todos os municípios":
    st.subheader(f"📌 Indicadores-chave - {uf} (Todos os municípios)")
    
    # Calcular KPIs usando data.py
    kpis = calcular_kpis_uf(df, uf, ano_ref)
    crescimento_periodo = calcular_crescimento_periodo(df, uf, "sigla_uf", ano_intervalo[0], ano_intervalo[1])
    
    if kpis:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        col1.metric(
            f"PIB Total ({ano_ref})",
            f"R$ {kpis['pib_total']/1000:.1f} mi" if kpis['pib_total'] < 1_000_000 else f"R$ {kpis['pib_total']/1_000_000:.1f} bi",
            f"{kpis['crescimento_ano_anterior']:.1f}% vs ano anterior" if kpis['crescimento_ano_anterior'] else "N/A"
        )

        col2.metric(
            f"População total ({ano_ref})",
            f"{kpis['populacao_total']:,.0f}".replace(",", "."),
            None
        )
        
        col3.metric(
            f"PIB per capita médio ({ano_ref})",
            f"R$ {kpis['pib_per_capita_medio']:,.0f}".replace(",", "."),
            f"{kpis['cresc_ppc_ano_anterior']:.1f}% vs ano anterior" if kpis['cresc_ppc_ano_anterior'] else "N/A"
        )
        
        col4.metric(
            f"Crescimento acumulado ({ano_intervalo[0]}–{ano_intervalo[1]})",
            f"{crescimento_periodo:.1f}%" if crescimento_periodo else "N/A"
          #  f"{ano_intervalo[1]} → {ano_intervalo[0]}" if crescimento_periodo and crescimento_periodo < 0 else f"{ano_intervalo[0]} → {ano_intervalo[1]}",
          #  delta_color="normal" if crescimento_periodo and crescimento_periodo > 0 else "inverse"
        )
        
        col5.metric(
            "Número de municípios",
            f"{kpis['num_municipios']}",
            f"{uf}"
        )
    else:
        st.warning("Dados não disponíveis para a UF selecionada.")

elif modo == "Agregado":
    # Título dinâmico baseado na seleção
    if uf == "Todas":
        titulo_contexto = f"{regiao}"
    else:
        titulo_contexto = f"{uf}"
    
    st.subheader(f"📌 Indicadores-chave - {titulo_contexto}")
    
    # Calcular KPIs usando data.py
    kpis = calcular_kpis_agregado(df, regiao, ano_ref)
    
    # Calcular crescimento para região/Brasil
    if regiao == "Brasil":
        dados_ini = df[df["ano"] == ano_intervalo[0]]["pib_total"].sum()
        dados_fim = df[df["ano"] == ano_intervalo[1]]["pib_total"].sum()
    else:
        dados_ini = df[(df["nome_grande_regiao"] == regiao) & (df["ano"] == ano_intervalo[0])]["pib_total"].sum()
        dados_fim = df[(df["nome_grande_regiao"] == regiao) & (df["ano"] == ano_intervalo[1])]["pib_total"].sum()
    
    crescimento_periodo = ((dados_fim - dados_ini) / dados_ini) * 100 if dados_ini > 0 else None
    
    if kpis:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        col1.metric(
            f"PIB Total ({ano_ref})",
            f"R$ {kpis['pib_total']/1_000_000:.1f} bi",
            f"{kpis['crescimento_ano_anterior']:.1f}% vs ano anterior" if kpis['crescimento_ano_anterior'] else "N/A"
        )

        col2.metric(
            f"População total ({ano_ref})",
            f"{kpis['populacao_total']:,.0f}".replace(",", "."),
            None
        )
        
        col3.metric(
            f"PIB per capita médio ({ano_ref})",
            f"R$ {kpis['pib_per_capita_medio']:,.0f}".replace(",", "."),
            f"{kpis['cresc_ppc_ano_anterior']:.1f}% vs ano anterior" if kpis['cresc_ppc_ano_anterior'] else "N/A"
        )
        
        col4.metric(
            f"Crescimento acumulado ({ano_intervalo[0]}–{ano_intervalo[1]})",
            f"{crescimento_periodo:.1f}%" if crescimento_periodo else "N/A"
          #  f"{ano_intervalo[1]} → {ano_intervalo[0]}" if crescimento_periodo and crescimento_periodo < 0 else f"{ano_intervalo[0]} → {ano_intervalo[1]}",
          #  delta_color="normal" if crescimento_periodo and crescimento_periodo > 0 else "inverse"
        )
        
        col5.metric(
            "Número de municípios",
            f"{kpis['num_municipios']}"
            # titulo_contexto
        )
    else:
        st.warning("Dados não disponíveis para a seleção.")


# ===============================
# EVOLUÇÃO TEMPORAL
# ===============================
st.markdown("---")
st.subheader("📊 Evolução Econômica")
st.caption("Variação do PIB ao longo do tempo, ajustada ao nível de agregação selecionado")


col5, col6 = st.columns(2)


with col5:
    st.markdown(f"**Evolução do PIB ao longo do tempo ({ano_intervalo[0]}–{ano_intervalo[1]})**")
    
    if modo == "Município específico":
        df_line = dados_evolucao_pib(
            df, 
            uf=uf,
            municipios=[municipio_sel],
            ano_ini=ano_intervalo[0],
            ano_fim=ano_intervalo[1]
        )
        
        if not df_line.empty:
            # Converter para milhões/bilhões
            df_line["PIB (R$ mi)"] = df_line["pib_total"] / 1000
            
            fig_line = px.line(
                df_line,
                x="ano",
                y="PIB (R$ mi)",
                markers=True
            )
            fig_line.update_layout(xaxis_title="Ano", yaxis_title="PIB (R$ mi)")
        else:
            fig_line = px.line(title="Dados não disponíveis")
        
    elif modo == "Comparar municípios":
        if municipios_sel and len(municipios_sel) > 0:
            df_line = dados_evolucao_pib(
                df,
                uf=uf,
                municipios=municipios_sel,
                ano_ini=ano_intervalo[0],
                ano_fim=ano_intervalo[1]
            )
            
            if not df_line.empty:
                df_line["PIB (R$ mi)"] = df_line["pib_total"] / 1000
                
                fig_line = px.line(
                    df_line,
                    x="ano",
                    y="PIB (R$ mi)",
                    color="nome_municipio",
                    markers=True,
                    color_discrete_sequence=PALETA_COMPARACAO
                )
                fig_line.update_layout(xaxis_title="Ano", yaxis_title="PIB (R$ mi)", legend_title="Município")
            else:
                fig_line = px.line(title="Dados não disponíveis")
        else:
            fig_line = px.line(title="Selecione municípios para comparar")
    
    elif modo == "Todos os municípios":
        # Top 5 municípios da UF
        df_line = dados_evolucao_pib(
            df,
            uf=uf,
            ano_ini=ano_intervalo[0],
            ano_fim=ano_intervalo[1]
        )
        
        if not df_line.empty:
            df_line["PIB (R$ mi)"] = df_line["pib_total"] / 1000
            
            fig_line = px.line(
                df_line,
                x="ano",
                y="PIB (R$ mi)",
                color="nome_municipio",
                markers=True,
                title=f"Top 5 municípios por PIB",
                color_discrete_sequence=PALETA_COMPARACAO
            )
            fig_line.update_layout(xaxis_title="Ano", yaxis_title="PIB (R$ mi)", legend_title="Município")
        else:
            fig_line = px.line(title="Dados não disponíveis")
        
    else:  # Modo Agregado
        # Comparação entre UFs ou regiões
        df_line = dados_evolucao_pib(
            df,
            regiao=regiao if uf == "Todas" else None,
            ano_ini=ano_intervalo[0],
            ano_fim=ano_intervalo[1]
        )
        
        if not df_line.empty:
            df_line["PIB (R$ bi)"] = df_line["pib_total"] / 1_000_000
            
            fig_line = px.line(
                df_line,
                x="ano",
                y="PIB (R$ bi)",
                color="sigla_uf",
                markers=True,
                title="Top 5 UFs por PIB" if regiao == "Brasil" else f"UFs na região {regiao}",
                color_discrete_sequence=PALETA_COMPARACAO
            )
            fig_line.update_layout(xaxis_title="Ano", yaxis_title="PIB (R$ bi)", legend_title="UF")
        else:
            fig_line = px.line(title="Dados não disponíveis")
    
    st.plotly_chart(fig_line, use_container_width=True)


with col6:

    # Ajustar ano_fim para limite de dados de VAB (2021)
    ano_fim_vab = min(ano_intervalo[1], 2021)


    st.markdown(f"**Estrutura do Valor Adicionado ({ano_intervalo[0]}–{ano_fim_vab})**")
    
    if modo == "Município específico":
        df_area = dados_evolucao_valor_adicionado(
            df,
            municipio=municipio_sel,
            ano_ini=ano_intervalo[0],
            ano_fim=ano_intervalo[1]
        )
    elif modo == "Comparar municípios" and municipios_sel and len(municipios_sel) > 0:

        # Filtrar pelos municípios selecionados E pelo intervalo de anos
        df_temp = df[
            (df["sigla_uf"] == uf) & 
            (df["nome_municipio"].isin(municipios_sel)) &
            (df["ano"] >= ano_intervalo[0]) &
            (df["ano"] <= ano_fim_vab)
        ]
        df_area = df_temp.groupby("ano").agg({
            "vab_agropecuaria": "sum",
            "vab_industria": "sum",
            "vab_servicos": "sum",
            "vab_adm_defesa_educacao_saude": "sum"
        }).reset_index()
        df_area = df_area.rename(columns={
            "vab_agropecuaria": "Agropecuária",
            "vab_industria": "Indústria",
            "vab_servicos": "Serviços",
            "vab_adm_defesa_educacao_saude": "Administração Pública"
        })
    elif modo == "Todos os municípios":
        df_area = dados_evolucao_valor_adicionado(
            df,
            uf=uf,
            ano_ini=ano_intervalo[0],
            ano_fim=ano_intervalo[1]
        )
    else:  # Agregado
        df_area = dados_evolucao_valor_adicionado(
            df,
            regiao=regiao if uf == "Todas" else None,
            uf=uf if uf != "Todas" else None,
            ano_ini=ano_intervalo[0],
            ano_fim=ano_intervalo[1]
        )
    
    if df_area is not None and not df_area.empty:
        # Converter para bilhões para visualização
        for col in ["Agropecuária", "Indústria", "Serviços", "Administração Pública"]:
            if col in df_area.columns:
                df_area[col] = df_area[col] / 1000  # Milhares -> Milhões
        
        fig_area = px.area(
            df_area,
            x="ano",
            y=["Agropecuária", "Indústria", "Serviços", "Administração Pública"],
            color_discrete_map=CORES_SETORES
        )
        fig_area.update_layout(xaxis_title="Ano", yaxis_title="Valor Adicionado (R$ mi)", legend_title="Setor")
    else:
        fig_area = px.area(title="Dados não disponíveis")
    
    st.plotly_chart(fig_area, use_container_width=True)


# ===============================
# COMPOSIÇÃO DO PIB (ANO REF)
# ===============================
if modo == "Município específico":

    # ano_ref no máximo 2021
    ano_ref = min(ano_ref, 2021)


    st.markdown("---")
    
    
    # col7, col8 = st.columns(2)
    # colunas na proporção 1, 1.5
    col7, col8 = st.columns([1, 1.5])
    
    with col7:
        st.subheader(f"🧩 Composição do PIB — {ano_ref}")
        st.caption("Estrutura setorial e posicionamento relativo do município")

        df_donut = composicao_setorial_municipio(df, municipio_sel, ano_ref)
        
        if df_donut is not None and not df_donut.empty:
            fig_donut = px.pie(
                df_donut,
                names="Setor",
                values="Participação (%)",
                hole=0.5,
                color="Setor",
                color_discrete_map=CORES_SETORES
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.warning("Dados de composição não disponíveis")
    
    with col8:
        st.markdown("### 🧠 Escala econômica vs renda")
        st.caption(
            "Comparação do município selecionado com outros municípios da mesma UF e com população similar, "
            "avaliando relação entre tamanho da economia, renda média e dependência pública. Dados de PIB e PIB per capita referentes ao ano de {}.".format(ano_ref)
        )
        
        df_scatter = scatter_pib_vs_per_capita(df, uf, municipio_sel, ano_ref)
        
        if df_scatter is not None and not df_scatter.empty:
            # Criar coluna para cor baseada em se é referência
            df_scatter["Cor"] = df_scatter["É Referência"].map({
                True: "Município Selecionado",
                False: "Outros Municípios"
            })
            
            fig_scatter = px.scatter(
                df_scatter,
                x="PIB Total (R$ mi)",
                y="PIB per capita (R$)",
                size="Dependência Pública (%)",
                color="Cor",
                color_discrete_map={
                    "Município Selecionado": COR_REFERENCIA,  # Vermelho forte
                    "Outros Municípios": COR_SECUNDARIA       # Azul escuro
                },
                hover_data=["Município"],
                text="Município",
                size_max=40
            )
            fig_scatter.update_traces(textposition='top center', textfont_size=8)
            fig_scatter.update_layout(legend_title="Legenda")
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.warning("Dados de scatter não disponíveis")


# ===============================
# TODOS OS MUNICÍPIOS (UF)
# ===============================
if modo == "Todos os municípios":
    st.markdown("---")
    st.subheader(f"🏙️ Análise dos Municípios de {uf}")
    st.caption("Rankings, distribuições e indicadores detalhados dos municípios da UF selecionada")
    
    col_todos1, col_todos2 = st.columns(2)
    
    with col_todos1:
        st.markdown("**Ranking: PIB Total - {}**".format(ano_ref))
        df_ranking_mun = ranking_municipios_pib(df, uf, ano_ref, top_n=10)
        
        if df_ranking_mun is not None and not df_ranking_mun.empty:
            # Preparar para visualização horizontal (inverter para mostrar maior no topo)
            df_ranking_mun_sorted = df_ranking_mun.sort_values("PIB Total (R$ mi)", ascending=True)
            
            fig_ranking_mun = px.bar(
                df_ranking_mun_sorted,
                y="Município",
                x="PIB Total (R$ mi)",
                orientation='h',
                text_auto='.1f'
            )
            st.plotly_chart(fig_ranking_mun, use_container_width=True)
        else:
            st.warning("Dados de ranking não disponíveis")
    
    with col_todos2:
        st.markdown("**Ranking: PIB per capita - {}**".format(ano_ref))
        df_ranking_pc = ranking_municipios_per_capita(df, uf, ano_ref, top_n=10)
        
        if df_ranking_pc is not None and not df_ranking_pc.empty:
            df_ranking_pc_sorted = df_ranking_pc.sort_values("PIB per capita (R$)", ascending=True)
            
            fig_ranking_pc = px.bar(
                df_ranking_pc_sorted,
                y="Município",
                x="PIB per capita (R$)",
                orientation='h',
                text_auto='.0f',
                color="PIB per capita (R$)",
                color_continuous_scale="RdYlGn"  # Vermelho-Amarelo-Verde
            )
            st.plotly_chart(fig_ranking_pc, use_container_width=True)
        else:
            st.warning("Dados de ranking não disponíveis")
    
    # Distribuição e análise
    st.markdown("---")
    col_dist1, col_dist2 = st.columns(2)
    
    with col_dist1:
        ano_ref = min(ano_ref, 2021)
        st.markdown("**Distribuição setorial média - {}**".format(ano_ref))
        df_setores_uf = composicao_setorial_uf(df, uf, ano_ref)
        
        if df_setores_uf is not None and not df_setores_uf.empty:
            fig_setores_uf = px.pie(
                df_setores_uf,
                names="Setor",
                values="Participação (%)",
                hole=0.5,
                color="Setor",
                color_discrete_map=CORES_SETORES
            )
            st.plotly_chart(fig_setores_uf, use_container_width=True)
        else:
            st.warning("Dados setoriais não disponíveis")
    
    with col_dist2:
        st.markdown("**Distribuição do PIB per capita - {}**".format(ano_ref))
        # Obter dados de PIB per capita de todos os municípios da UF
        dados_uf = df[(df["sigla_uf"] == uf) & (df["ano"] == ano_ref)]
        
        if not dados_uf.empty:
            fig_hist = px.histogram(
                dados_uf,
                x="pib_per_capita",
                nbins=20,
                title="Frequência",
                labels={"pib_per_capita": "PIB per capita (R$)"}
            )
            fig_hist.update_layout(yaxis_title="Número de municípios")
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.warning("Dados de distribuição não disponíveis")
    
    # Tabela detalhada
    ano_ref = min(ano_ref, 2021)
    st.markdown("**📋 Tabela Detalhada - Municípios de {} ({} municípios)**".format(uf, len(municipios)))
    st.caption("Dados referentes ao ano de {}".format(ano_ref))
    df_table_todos = tabela_municipios_completa(df, uf, ano_ref, ano_intervalo[0])
    
    if df_table_todos is not None and not df_table_todos.empty:
        st.dataframe(df_table_todos, use_container_width=True)
    else:
        st.warning("Tabela detalhada não disponível")


# ===============================
# COMPARAÇÃO ENTRE MUNICÍPIOS
# ===============================
if modo == "Comparar municípios" and municipios_sel and len(municipios_sel) > 1:
    st.markdown("---")
    st.subheader("🔍 Comparação Direta entre Municípios")
    st.caption("Análise lado a lado dos municípios selecionados para identificar diferenças e padrões")

    ano_ref = min(ano_ref, 2021)
    
    col9, col10 = st.columns(2)
    
    # Obter dados dos municípios selecionados
    dados_comparacao = df[(df["sigla_uf"] == uf) & (df["nome_municipio"].isin(municipios_sel)) & (df["ano"] == ano_ref)]
    
    with col9:
        st.markdown(f"**PIB Total - {ano_ref}**")
        if not dados_comparacao.empty:
            df_bar_pib = dados_comparacao[["nome_municipio", "pib_total"]].copy()
            df_bar_pib["PIB Total (R$ mi)"] = df_bar_pib["pib_total"] / 1000
            
            fig_bar = px.bar(
                df_bar_pib,
                x="nome_municipio",
                y="PIB Total (R$ mi)",
                text_auto='.1f',
                labels={"nome_municipio": "Município"}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("Dados não disponíveis")
    
    with col10:
        st.markdown(f"**PIB per capita - {ano_ref}**")
        if not dados_comparacao.empty:
            fig_bar_pc = px.bar(
                dados_comparacao,
                x="nome_municipio",
                y="pib_per_capita",
                text_auto='.0f',
                labels={"nome_municipio": "Município", "pib_per_capita": "PIB per capita (R$)"}
            )
            st.plotly_chart(fig_bar_pc, use_container_width=True)
        else:
            st.warning("Dados não disponíveis")
    
    st.markdown(f"**Tabela Comparativa Consolidada - {ano_ref}**")
    if not dados_comparacao.empty:
        # Calcular métricas para tabela
        ano_fim = min(ano_intervalo[1], 2021)
        tabela_comp = []
        for _, row in dados_comparacao.iterrows():
            municipio = row["nome_municipio"]
            crescimento = calcular_crescimento_periodo(df, municipio, "nome_municipio", ano_intervalo[0], ano_fim)
            dependencia = (row["vab_adm_defesa_educacao_saude"] / row["vab_total"]) * 100 if row["vab_total"] > 0 else 0
            
            tabela_comp.append({
                "Município": municipio,
                "PIB Total (R$ mi)": row["pib_total"] / 1000,
                "PIB per capita (R$)": row["pib_per_capita"],
                "Dependência Pública (%)": dependencia,
                f"Crescimento {ano_intervalo[0]}–{ano_fim}": f"{crescimento:.1f}%" if crescimento else "N/A",
                "Setor Dominante": row["atividade_maior_vab"]
            })
        
        df_table = pd.DataFrame(tabela_comp)
        st.dataframe(df_table, use_container_width=True)
    else:
        st.warning("Tabela não disponível")


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
        df_ranking = ranking_ufs(df, ano_ref, regiao if uf == "Todas" else None)
        
        if df_ranking is not None and not df_ranking.empty:
            df_ranking_sorted = df_ranking.sort_values("PIB Total (R$ bi)", ascending=True)
            
            fig_ranking = px.bar(
                df_ranking_sorted,
                y="UF",
                x="PIB Total (R$ bi)",
                orientation='h',
                text_auto='.1f',
                color="PIB Total (R$ bi)",
                color_continuous_scale="Blues"
            )
            st.plotly_chart(fig_ranking, use_container_width=True)
        else:
            st.warning("Dados de ranking não disponíveis")
    
    with col12:
        st.markdown("**PIB per capita por UF**")
        df_per_capita = ranking_ufs_per_capita(df, ano_ref, regiao if uf == "Todas" else None)
        
        if df_per_capita is not None and not df_per_capita.empty:
            df_per_capita_sorted = df_per_capita.sort_values("PIB per capita (R$)", ascending=True)
            
            fig_per_capita = px.bar(
                df_per_capita_sorted,
                y="UF",
                x="PIB per capita (R$)",
                orientation='h',
                text_auto='.0f',
                color="PIB per capita (R$)",
                color_continuous_scale="Blues"
            )
            st.plotly_chart(fig_per_capita, use_container_width=True)
        else:
            st.warning("Dados de PIB per capita não disponíveis")
    
    # Bloco Principal 2: Análise de Relação (Scatter)
    st.markdown("---")
    st.markdown("**📊 Relação: Tamanho da Economia vs Renda Média**")
    st.caption("Cada ponto representa uma UF. Tamanho indica número de municípios.")
    
    df_scatter_ufs = scatter_ufs_pib_vs_per_capita(df, ano_ref, regiao if uf == "Todas" else None)
    
    if df_scatter_ufs is not None and not df_scatter_ufs.empty:
        fig_scatter_ufs = px.scatter(
            df_scatter_ufs,
            x="PIB Total (R$ bi)",
            y="PIB per capita (R$)",
            size="Nº Municípios",
            hover_data=["UF"],
            text="UF",
            size_max=50,
            color="PIB per capita (R$)",
            color_continuous_scale="Viridis"
        )
        fig_scatter_ufs.update_traces(textposition='top center')
        st.plotly_chart(fig_scatter_ufs, use_container_width=True)
    else:
        st.warning("Dados de scatter não disponíveis")
    
    # Análises Avançadas (em Tabs)
    st.markdown("---")
    tab1, tab2 = st.tabs(["📋 Tabela Detalhada", "🧩 Composição Setorial"])
    
    with tab1:
        # ano no máximo 2021
        ano_ref = min(ano_ref, 2021)

        st.markdown("**Dados Consolidados por UF**")
        st.caption("Tabela detalhada com principais indicadores econômicos das UFs para o ano de {}".format(ano_ref))
        df_table_ufs = tabela_ufs_completa(df, ano_ref, ano_intervalo[0], regiao if uf == "Todas" else None)
        
        if df_table_ufs is not None and not df_table_ufs.empty:
            st.dataframe(df_table_ufs, use_container_width=True)
        else:
            st.warning("Tabela não disponível")
    
    with tab2:
        col_tab1, col_tab2 = st.columns(2)
        
        with col_tab1:
            st.markdown("**Distribuição setorial média - {}**".format(ano_ref))
            df_setores_agg = composicao_setorial_agregado(df, regiao, ano_ref)
            
            if df_setores_agg is not None and not df_setores_agg.empty:
                fig_setores = px.pie(
                    df_setores_agg,
                    names="Setor",
                    values="Participação (%)",
                    hole=0.5,
                    color="Setor",
                    color_discrete_map=CORES_SETORES
                )
                st.plotly_chart(fig_setores, use_container_width=True)
            else:
                st.warning("Dados setoriais não disponíveis")
        
        with col_tab2:
            st.markdown("**Participação setorial por UF - {}**".format(ano_ref))
            # Obter composição setorial de cada UF
            if regiao == "Brasil":
                st.caption("Comparação entre as 10 UFs com maior PIB")
                pib_por_uf = df[df["ano"] == ano_ref].groupby("sigla_uf")["pib_total"].sum().sort_values(ascending=False)
                ufs_para_mostrar = pib_por_uf.head(10).index.tolist()
            else:
                ufs_para_mostrar = df[(df["nome_grande_regiao"] == regiao) & (df["ano"] == ano_ref)]["sigla_uf"].unique()
            
            composicoes_ufs = []
            for uf_item in ufs_para_mostrar:
                comp = composicao_setorial_uf(df, uf_item, ano_ref)
                if comp is not None and not comp.empty:
                    comp["UF"] = uf_item
                    composicoes_ufs.append(comp)
            
            if composicoes_ufs:
                df_stacked = pd.concat(composicoes_ufs, ignore_index=True)
                
                fig_stacked = px.bar(
                    df_stacked,
                    x="UF",
                    y="Participação (%)",
                    color="Setor",
                    text_auto='.1f',
                    color_discrete_map=CORES_SETORES
                )
                st.plotly_chart(fig_stacked, use_container_width=True)
            else:
                st.warning("Dados setoriais por UF não disponíveis")


# ===============================
# RODAPÉ
# ===============================
st.markdown("---")
st.caption("Dashboard desenvolvido em Streamlit • Dados: IBGE")
