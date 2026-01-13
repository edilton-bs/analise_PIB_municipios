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

def formatar_valor(valor): 
    if valor < 1_000_000: 
        # até milhões 
        return f"R$ {valor/1000:.1f} mi" 
    elif valor < 1_000_000_000: 
        # até bilhões 
        return f"R$ {valor/1_000_000:.1f} bi" 
    else: 
        # trilhões 
        return f"R$ {valor/1_000_000_000:.1f} tri"


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

# Seleção de modo de visualização a depender da UF e região
if uf == "Todas":
    if regiao == "Brasil":
        modos_disponiveis = ["Agregado", "Comparar Regiões", "Comparar Estados", "Município específico", "Comparar municípios"]
    else:
        modos_disponiveis = ["Agregado", "Comparar Estados", "Município específico", "Comparar municípios"]
else:
    modos_disponiveis = ["Todos os municípios", "Município específico", "Comparar municípios"]
modo = st.sidebar.radio(
    "Modo de visualização",
    modos_disponiveis
)

# Variáveis de seleção
municipios = []
municipios_sel = []
municipios_sel_dict = {}  # Para armazenar município -> UF
ufs_sel = []  # Para armazenar UFs selecionadas
regioes_sel = []  # Para armazenar regiões selecionadas

if modo == "Comparar Regiões":
    # Obter lista de regiões
    regioes_disponiveis = ["Norte", "Nordeste", "Sudeste", "Sul", "Centro-oeste"]
    st.sidebar.markdown("**Regiões do Brasil**")
    
    regioes_sel = st.sidebar.multiselect(
        "Selecione Regiões para comparação",
        regioes_disponiveis,
        default=regioes_disponiveis[:2] if len(regioes_disponiveis) >= 2 else []
    )
    
    if regioes_sel:
        st.sidebar.caption(f"{len(regioes_sel)} região(ões) selecionada(s)")

elif modo == "Comparar Estados":
    # Obter lista de UFs baseada na região
    if regiao == "Brasil":
        ufs_disponiveis = obter_lista_ufs(df, None)
        st.sidebar.markdown("**Estados do Brasil**")
        default_count = min(3, len(ufs_disponiveis))
    else:
        ufs_disponiveis = obter_lista_ufs(df, regiao)
        st.sidebar.markdown(f"**Estados da região {regiao}**")
        default_count = min(2, len(ufs_disponiveis))
    
    ufs_sel = st.sidebar.multiselect(
        "Selecione Estados para comparação",
        ufs_disponiveis,
        default=ufs_disponiveis[:default_count] if default_count > 0 else []
    )
    
    if ufs_sel:
        st.sidebar.caption(f"{len(ufs_sel)} estado(s) selecionado(s)")

elif modo == "Município específico":
    # Obter lista de municípios baseado na seleção de região/UF
    if uf != "Todas":
        municipios = obter_lista_municipios(df, uf)
        st.sidebar.markdown(f"**Município de {uf}**")
    elif regiao != "Brasil":
        # Municípios da região
        municipios = df[df["nome_grande_regiao"] == regiao]["nome_municipio"].unique()
        municipios = sorted(municipios.tolist())
        st.sidebar.markdown(f"**Município da região {regiao}**")
    else:
        # Todos os municípios do Brasil
        municipios = df["nome_municipio"].unique()
        municipios = sorted(municipios.tolist())
        st.sidebar.markdown(f"**Município do Brasil**")
    
    municipio_sel = st.sidebar.selectbox("Selecione o município", municipios)

elif modo == "Comparar municípios":
    # Obter lista de municípios baseado na seleção de região/UF
    if uf != "Todas":
        municipios = obter_lista_municipios(df, uf)
        st.sidebar.markdown(f"**Municípios de {uf}**")
        default_count = min(2, len(municipios))
    elif regiao != "Brasil":
        # Municípios da região
        municipios = df[df["nome_grande_regiao"] == regiao]["nome_municipio"].unique()
        municipios = sorted(municipios.tolist())
        st.sidebar.markdown(f"**Municípios da região {regiao}**")
        default_count = min(3, len(municipios))
    else:
        # Todos os municípios do Brasil
        municipios = df["nome_municipio"].unique()
        municipios = sorted(municipios.tolist())
        st.sidebar.markdown(f"**Municípios do Brasil**")
        default_count = 0  # Não selecionar nenhum por padrão quando é Brasil inteiro
    
    municipios_sel = st.sidebar.multiselect(
        "Selecione municípios para comparação",
        municipios,
        default=municipios[:default_count] if default_count > 0 else []
    )
    
    if municipios_sel:
        st.sidebar.caption(f"{len(municipios_sel)} município(s) selecionado(s)")
        # Criar dicionário município -> UF
        for mun in municipios_sel:
            uf_mun = df[df["nome_municipio"] == mun]["sigla_uf"].iloc[0]
            municipios_sel_dict[mun] = uf_mun

elif modo == "Todos os municípios":
    # Validação: só funciona se uma UF específica estiver selecionada
    if uf == "Todas":
        st.sidebar.warning("⚠️ Selecione uma UF específica para este modo")
        modo = "Agregado"  # Fallback para modo agregado
    else:
        municipios = obter_lista_municipios(df, uf)
        st.sidebar.markdown(f"**Analisando {len(municipios)} municípios de {uf}**")


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
    # Obter UF do município selecionado
    uf_municipio = df[df["nome_municipio"] == municipio_sel]["sigla_uf"].iloc[0]
    st.subheader(f"📌 Indicadores-chave - {municipio_sel} ({uf_municipio})")
    
    # Calcular KPIs usando data.py
    kpis = calcular_kpis_municipio(df, municipio_sel, ano_ref)
    crescimento_periodo = calcular_crescimento_periodo(df, municipio_sel, "nome_municipio", ano_intervalo[0], ano_intervalo[1])
    
    if kpis:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        col1.metric(
            f"PIB Total ({ano_ref})",
            formatar_valor(kpis['pib_total']),
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

elif modo == "Comparar municípios" and municipios_sel and len(municipios_sel) > 0:
    # Determinar quantas UFs/regiões diferentes estão sendo comparadas
    ufs_selecionadas = df[df["nome_municipio"].isin(municipios_sel)]["sigla_uf"].unique()
    
    if len(ufs_selecionadas) == 1:
        titulo_kpi = f"📌 Comparação entre municípios de {ufs_selecionadas[0]}"
    elif uf != "Todas":
        titulo_kpi = f"📌 Comparação entre municípios de {uf}"
    elif regiao != "Brasil":
        titulo_kpi = f"📌 Comparação entre municípios da região {regiao}"
    else:
        titulo_kpi = f"📌 Comparação entre municípios ({len(ufs_selecionadas)} UFs)"
    
    st.subheader(titulo_kpi)
    
    # Calcular KPIs agregados dos municípios selecionados
    dados_selecionados = df[(df["nome_municipio"].isin(municipios_sel)) & (df["ano"] == ano_ref)]
    
    if not dados_selecionados.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        pib_total = dados_selecionados["pib_total"].sum()
        populacao_total = (dados_selecionados["pib_total"] / dados_selecionados["pib_per_capita"]).sum() * 1000
        pib_per_capita_medio = pib_total / (populacao_total / 1000) if populacao_total > 0 else 0
        
        col1.metric(
            f"PIB Total agregado ({ano_ref})",
            formatar_valor(pib_total)
        )
        
        col2.metric(
            f"População total ({ano_ref})",
            f"{int(populacao_total):,}".replace(",", ".")
        )
        
        col3.metric(
            f"PIB per capita médio ({ano_ref})",
            f"R$ {pib_per_capita_medio:,.0f}".replace(",", ".")
        )
        
        col4.metric(
            "Municípios selecionados",
            f"{len(municipios_sel)}"
        )
    else:
        st.warning("Dados não disponíveis para os municípios selecionados.")

elif modo == "Comparar Estados" and ufs_sel and len(ufs_sel) > 0:
    # Determinar título baseado na região
    if regiao == "Brasil":
        titulo_kpi = f"📌 Comparação entre Estados ({len(ufs_sel)} UFs)"
    else:
        titulo_kpi = f"📌 Comparação entre Estados da região {regiao}"
    
    st.subheader(titulo_kpi)
    
    # Calcular KPIs agregados das UFs selecionadas
    dados_selecionados = df[(df["sigla_uf"].isin(ufs_sel)) & (df["ano"] == ano_ref)]
    
    if not dados_selecionados.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        pib_total = dados_selecionados["pib_total"].sum()
        populacao_total = (dados_selecionados["pib_total"] / dados_selecionados["pib_per_capita"]).sum() * 1000
        pib_per_capita_medio = pib_total / (populacao_total / 1000) if populacao_total > 0 else 0
        num_municipios = dados_selecionados["nome_municipio"].nunique()
        
        col1.metric(
            f"PIB Total agregado ({ano_ref})",
            formatar_valor(pib_total)
        )
        
        col2.metric(
            f"População total ({ano_ref})",
            f"{int(populacao_total):,}".replace(",", ".")
        )
        
        col3.metric(
            f"PIB per capita médio ({ano_ref})",
            f"R$ {pib_per_capita_medio:,.0f}".replace(",", ".")
        )
        
        col4.metric(
            "Total de municípios",
            f"{num_municipios}"
        )
    else:
        st.warning("Dados não disponíveis para os estados selecionados.")

elif modo == "Comparar Regiões" and regioes_sel and len(regioes_sel) > 0:
    st.subheader(f"📌 Comparação entre Regiões ({len(regioes_sel)} regiões)")
    
    # Calcular KPIs agregados das regiões selecionadas
    dados_selecionados = df[(df["nome_grande_regiao"].isin(regioes_sel)) & (df["ano"] == ano_ref)]
    
    if not dados_selecionados.empty:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        pib_total = dados_selecionados["pib_total"].sum()
        populacao_total = (dados_selecionados["pib_total"] / dados_selecionados["pib_per_capita"]).sum() * 1000
        pib_per_capita_medio = pib_total / (populacao_total / 1000) if populacao_total > 0 else 0
        num_municipios = dados_selecionados["nome_municipio"].nunique()
        
        col1.metric(
            f"PIB Total agregado ({ano_ref})",
            formatar_valor(pib_total)
        )
        
        col2.metric(
            f"População total ({ano_ref})",
            f"{int(populacao_total):,}".replace(",", ".")
        )
        
        col3.metric(
            f"PIB per capita médio ({ano_ref})",
            f"R$ {pib_per_capita_medio:,.0f}".replace(",", ".")
        )

        col4.metric(
            "Total de UFs",
            f"{dados_selecionados['sigla_uf'].nunique()}"
        )
        
        col5.metric(
            "Total de municípios",
            f"{num_municipios}"
        )
    else:
        st.warning("Dados não disponíveis para as regiões selecionadas.")

elif modo == "Todos os municípios":
    st.subheader(f"📌 Indicadores-chave - {uf} (Todos os municípios)")
    
    # Calcular KPIs usando data.py
    kpis = calcular_kpis_uf(df, uf, ano_ref)
    crescimento_periodo = calcular_crescimento_periodo(df, uf, "sigla_uf", ano_intervalo[0], ano_intervalo[1])
    
    if kpis:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        col1.metric(
            f"PIB Total ({ano_ref})",
            formatar_valor(kpis['pib_total']),
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
            # f"{uf}"
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
            formatar_valor(kpis['pib_total']),
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
# st.caption("Variação do PIB ao longo do tempo, ajustada ao nível de agregação selecionado")


col5, col6 = st.columns(2)


with col5:
    st.markdown(f"**Evolução do PIB ao longo do tempo ({ano_intervalo[0]}–{ano_intervalo[1]})**")
    
    if modo == "Comparar Regiões":
        st.caption(f"Comparação da evolução econômica entre {len(regioes_sel)} regiões")
        
        if regioes_sel and len(regioes_sel) > 0:
            # Dados agregados por região
            df_filtrado = df[
                (df["nome_grande_regiao"].isin(regioes_sel)) &
                (df["ano"] >= ano_intervalo[0]) &
                (df["ano"] <= ano_intervalo[1])
            ]
            
            df_line = df_filtrado.groupby(["ano", "nome_grande_regiao"]).agg(
                pib_total=("pib_total", "sum")
            ).reset_index()
            
            if not df_line.empty:
                df_line["PIB (R$ bi)"] = df_line["pib_total"] / 1_000_000
                
                fig_line = px.line(
                    df_line,
                    x="ano",
                    y="PIB (R$ bi)",
                    color="nome_grande_regiao",
                    markers=True,
                    color_discrete_sequence=PALETA_COMPARACAO
                )
                fig_line.update_layout(xaxis_title="Ano", yaxis_title="PIB (R$ bi)", legend_title="Região")
            else:
                fig_line = px.line(title="Dados não disponíveis")
        else:
            fig_line = px.line(title="Selecione regiões para comparar")
    
    elif modo == "Comparar Estados":
        st.caption(f"Comparação da evolução econômica entre {len(ufs_sel)} estados")
        
        if ufs_sel and len(ufs_sel) > 0:
            # Dados agregados por UF
            df_filtrado = df[
                (df["sigla_uf"].isin(ufs_sel)) &
                (df["ano"] >= ano_intervalo[0]) &
                (df["ano"] <= ano_intervalo[1])
            ]
            
            df_line = df_filtrado.groupby(["ano", "sigla_uf"]).agg(
                pib_total=("pib_total", "sum")
            ).reset_index()
            
            if not df_line.empty:
                df_line["PIB (R$ bi)"] = df_line["pib_total"] / 1_000_000
                
                fig_line = px.line(
                    df_line,
                    x="ano",
                    y="PIB (R$ bi)",
                    color="sigla_uf",
                    markers=True,
                    color_discrete_sequence=PALETA_COMPARACAO
                )
                fig_line.update_layout(xaxis_title="Ano", yaxis_title="PIB (R$ bi)", legend_title="UF")
            else:
                fig_line = px.line(title="Dados não disponíveis")
        else:
            fig_line = px.line(title="Selecione estados para comparar")
    
    elif modo == "Município específico":
        st.caption(f"Visualizando apenas os top 5 maiores PIBs em {ano_intervalo[1]} para clareza")
        # Obter UF do município
        uf_municipio = df[df["nome_municipio"] == municipio_sel]["sigla_uf"].iloc[0]
        
        df_line = dados_evolucao_pib(
            df, 
            uf=uf_municipio,
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
            # Filtrar municípios com base na região/UF selecionada
            if uf != "Todas":
                df_line = dados_evolucao_pib(
                    df,
                    uf=uf,
                    municipios=municipios_sel,
                    ano_ini=ano_intervalo[0],
                    ano_fim=ano_intervalo[1]
                )
            elif regiao != "Brasil":
                df_line = dados_evolucao_pib(
                    df,
                    regiao=regiao,
                    municipios=municipios_sel,
                    ano_ini=ano_intervalo[0],
                    ano_fim=ano_intervalo[1]
                )
            else:
                # Brasil inteiro - filtrar apenas pelos municípios
                df_filtrado = df[
                    (df["nome_municipio"].isin(municipios_sel)) &
                    (df["ano"] >= ano_intervalo[0]) &
                    (df["ano"] <= ano_intervalo[1])
                ]
                df_line = df_filtrado.groupby(["ano", "nome_municipio"]).agg(
                    pib_total=("pib_total", "sum")
                ).reset_index()
            
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
                title=None,
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
    if uf == "Todas":
        st.caption(f"Evolução do valor adicionado ao longo do tempo considerando todos as UFs da região")
    else:
        st.caption(f"Evolução do valor adicionado ao longo do tempo considerando todos os municípios")
    
    if modo == "Comparar Regiões" and regioes_sel and len(regioes_sel) > 0:
        # Filtrar pelas regiões selecionadas E pelo intervalo de anos
        df_temp = df[
            (df["nome_grande_regiao"].isin(regioes_sel)) &
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
    elif modo == "Comparar Estados" and ufs_sel and len(ufs_sel) > 0:
        # Filtrar pelos estados selecionados E pelo intervalo de anos
        df_temp = df[
            (df["sigla_uf"].isin(ufs_sel)) &
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
    elif modo == "Município específico":
        df_area = dados_evolucao_valor_adicionado(
            df,
            municipio=municipio_sel,
            ano_ini=ano_intervalo[0],
            ano_fim=ano_intervalo[1]
        )
    elif modo == "Comparar municípios" and municipios_sel and len(municipios_sel) > 0:
        # Filtrar pelos municípios selecionados E pelo intervalo de anos
        df_temp = df[
            (df["nome_municipio"].isin(municipios_sel)) &
            (df["ano"] >= ano_intervalo[0]) &
            (df["ano"] <= ano_fim_vab)
        ]
        
        # Se região específica foi selecionada, aplicar filtro adicional
        if regiao != "Brasil":
            df_temp = df_temp[df_temp["nome_grande_regiao"] == regiao]
        if uf != "Todas":
            df_temp = df_temp[df_temp["sigla_uf"] == uf]
        
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
    
    # Obter UF do município
    uf_municipio = df[df["nome_municipio"] == municipio_sel]["sigla_uf"].iloc[0]

    st.markdown("---")
    
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
            f"Comparação de {municipio_sel} com municípios de {uf_municipio} com população similar. "
            f"Dados de PIB e PIB per capita referentes ao ano de {ano_ref}."
        )
        
        df_scatter = scatter_pib_vs_per_capita(df, uf_municipio, municipio_sel, ano_ref)
        
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
    # st.markdown("--REGIÕES
# ===============================
if modo == "Comparar Regiões" and regioes_sel and len(regioes_sel) > 1:
    st.markdown("---")
    st.subheader("🗺️ Comparação Detalhada entre Regiões")
    st.caption(f"Análise comparativa de {len(regioes_sel)} regiões brasileiras")
    
    ano_ref_comp = min(ano_ref, 2021)
    
    col_reg1, col_reg2 = st.columns(2)
    
    # Obter dados agregados por região
    dados_regioes = df[(df["nome_grande_regiao"].isin(regioes_sel)) & (df["ano"] == ano_ref)].groupby("nome_grande_regiao").agg({
        "pib_total": "sum",
        "pib_per_capita": "mean"
    }).reset_index()
    
    with col_reg1:
        st.markdown(f"**PIB Total por Região - {ano_ref}**")
        if not dados_regioes.empty:
            dados_regioes["PIB Total (R$ bi)"] = dados_regioes["pib_total"] / 1_000_000
            
            fig_bar_reg = px.bar(
                dados_regioes,
                x="nome_grande_regiao",
                y="PIB Total (R$ bi)",
                text_auto='.1f',
                labels={"nome_grande_regiao": "Região"}
            )
            st.plotly_chart(fig_bar_reg, use_container_width=True)
        else:
            st.warning("Dados não disponíveis")
    
    with col_reg2:
        st.markdown(f"**PIB per capita médio - {ano_ref}**")
        if not dados_regioes.empty:
            fig_bar_pc_reg = px.bar(
                dados_regioes,
                x="nome_grande_regiao",
                y="pib_per_capita",
                text_auto='.0f',
                labels={"nome_grande_regiao": "Região", "pib_per_capita": "PIB per capita (R$)"},
                color="pib_per_capita",
                color_continuous_scale="RdYlGn"
            )
            st.plotly_chart(fig_bar_pc_reg, use_container_width=True)
        else:
            st.warning("Dados não disponíveis")
    
    # Tabs para análises detalhadas
    st.markdown("---")
    tab1, tab2 = st.tabs(["📋 Tabela Comparativa", "🧩 Estrutura Setorial"])
    
    with tab1:
        st.markdown("**Indicadores Consolidados por Região**")
        st.caption(f"Dados referentes ao ano {ano_ref_comp}")
        
        # Criar tabela detalhada
        tabela_regioes = []
        dados_ano = df[(df["nome_grande_regiao"].isin(regioes_sel)) & (df["ano"] == ano_ref_comp)]
        
        for regiao_item in regioes_sel:
            dados_regiao = dados_ano[dados_ano["nome_grande_regiao"] == regiao_item]
            
            if not dados_regiao.empty:
                pib = dados_regiao["pib_total"].sum()
                pop = (dados_regiao["pib_total"] / dados_regiao["pib_per_capita"]).sum() * 1000
                ppc = pib / (pop / 1000) if pop > 0 else 0
                n_mun = dados_regiao["nome_municipio"].nunique()
                n_ufs = dados_regiao["sigla_uf"].nunique()
                
                # Calcular crescimento
                dados_ini = df[(df["nome_grande_regiao"] == regiao_item) & (df["ano"] == ano_intervalo[0])]["pib_total"].sum()
                dados_fim = df[(df["nome_grande_regiao"] == regiao_item) & (df["ano"] == ano_intervalo[1])]["pib_total"].sum()
                crescimento = ((dados_fim - dados_ini) / dados_ini) * 100 if dados_ini > 0 else None
                
                # Composição setorial
                vab_total = dados_regiao["vab_total"].sum()
                if vab_total > 0:
                    agro = (dados_regiao["vab_agropecuaria"].sum() / vab_total) * 100
                    ind = (dados_regiao["vab_industria"].sum() / vab_total) * 100
                    serv = (dados_regiao["vab_servicos"].sum() / vab_total) * 100
                    adm = (dados_regiao["vab_adm_defesa_educacao_saude"].sum() / vab_total) * 100
                else:
                    agro = ind = serv = adm = 0
                
                tabela_regioes.append({
                    "Região": regiao_item,
                    "Nº UFs": n_ufs,
                    "Nº Municípios": n_mun,
                    "População": f"{int(pop):,}".replace(",", "."),
                    "PIB Total (R$ bi)": f"{pib / 1_000_000:.1f}",
                    "PIB per capita (R$)": f"{ppc:,.0f}".replace(",", "."),
                    f"Crescimento {ano_intervalo[0]}–{ano_intervalo[1]}": f"{crescimento:.1f}%" if crescimento else "N/A",
                    "Agropecuária (%)": f"{agro:.1f}",
                    "Indústria (%)": f"{ind:.1f}",
                    "Serviços (%)": f"{serv:.1f}",
                    "Adm. Pública (%)": f"{adm:.1f}"
                })
        
        if tabela_regioes:
            df_tab_regioes = pd.DataFrame(tabela_regioes)
            st.dataframe(df_tab_regioes, use_container_width=True)
        else:
            st.warning("Dados não disponíveis")
    
    with tab2:
        col_set1, col_set2 = st.columns(2)
        
        with col_set1:
            st.markdown("**Composição Setorial Comparada**")
            st.caption(f"Participação dos setores no VAB - {ano_ref_comp}")
            
            composicoes = []
            for regiao_item in regioes_sel:
                comp = composicao_setorial_agregado(df, regiao_item, ano_ref_comp)
                if comp is not None and not comp.empty:
                    comp["Região"] = regiao_item
                    composicoes.append(comp)
            
            if composicoes:
                df_comp = pd.concat(composicoes, ignore_index=True)
                
                fig_comp = px.bar(
                    df_comp,
                    x="Região",
                    y="Participação (%)",
                    color="Setor",
                    text_auto='.1f',
                    color_discrete_map=CORES_SETORES
                )
                fig_comp.update_layout(barmode='stack')
                st.plotly_chart(fig_comp, use_container_width=True)
            else:
                st.warning("Dados não disponíveis")
        
        with col_set2:
            st.markdown("**Valores Absolutos por Setor**")
            st.caption(f"VAB em R$ bilhões - {ano_ref_comp}")
            
            dados_setores = df[(df["nome_grande_regiao"].isin(regioes_sel)) & (df["ano"] == ano_ref_comp)].groupby("nome_grande_regiao").agg({
                "vab_agropecuaria": "sum",
                "vab_industria": "sum",
                "vab_servicos": "sum",
                "vab_adm_defesa_educacao_saude": "sum"
            }).reset_index()
            
            if not dados_setores.empty:
                # Converter para bilhões e formato long
                dados_setores["Agropecuária"] = dados_setores["vab_agropecuaria"] / 1_000_000
                dados_setores["Indústria"] = dados_setores["vab_industria"] / 1_000_000
                dados_setores["Serviços"] = dados_setores["vab_servicos"] / 1_000_000
                dados_setores["Administração Pública"] = dados_setores["vab_adm_defesa_educacao_saude"] / 1_000_000
                
                df_long = dados_setores.melt(
                    id_vars=["nome_grande_regiao"],
                    value_vars=["Agropecuária", "Indústria", "Serviços", "Administração Pública"],
                    var_name="Setor",
                    value_name="VAB (R$ bi)"
                )
                
                fig_abs = px.bar(
                    df_long,
                    x="Setor",
                    y="VAB (R$ bi)",
                    color="nome_grande_regiao",
                    barmode='group',
                    text_auto='.1f',
                    color_discrete_sequence=PALETA_COMPARACAO,
                    labels={"nome_grande_regiao": "Região"}
                )
                st.plotly_chart(fig_abs, use_container_width=True)
            else:
                st.warning("Dados não disponíveis")

# ===============================
# COMPARAÇÃO ENTRE ESTADOS - Continuação da análise de "Todos os municípios"
# ===============================

# Esta seção pertence ao modo "Todos os municípios" da UF
if modo == "Todos os municípios":
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
# COMPARAÇÃO ENTRE ESTADOS
# ===============================
if modo == "Comparar Estados" and ufs_sel and len(ufs_sel) > 1:
    st.markdown("---")
    st.subheader("🗺️ Comparação Detalhada entre Estados")
    
    if regiao == "Brasil":
        st.caption(f"Análise comparativa de {len(ufs_sel)} estados brasileiros")
    else:
        st.caption(f"Análise comparativa de {len(ufs_sel)} estados da região {regiao}")
    
    ano_ref_comp = min(ano_ref, 2021)
    
    col_est1, col_est2 = st.columns(2)
    
    # Obter dados agregados por UF
    dados_ufs = df[(df["sigla_uf"].isin(ufs_sel)) & (df["ano"] == ano_ref)].groupby("sigla_uf").agg({
        "pib_total": "sum",
        "pib_per_capita": "mean"
    }).reset_index()
    
    with col_est1:
        st.markdown(f"**PIB Total por Estado - {ano_ref}**")
        if not dados_ufs.empty:
            dados_ufs["PIB Total (R$ bi)"] = dados_ufs["pib_total"] / 1_000_000
            
            fig_bar_ufs = px.bar(
                dados_ufs,
                x="sigla_uf",
                y="PIB Total (R$ bi)",
                text_auto='.1f',
                labels={"sigla_uf": "Estado"}
            )
            st.plotly_chart(fig_bar_ufs, use_container_width=True)
        else:
            st.warning("Dados não disponíveis")
    
    with col_est2:
        st.markdown(f"**PIB per capita médio - {ano_ref}**")
        if not dados_ufs.empty:
            fig_bar_pc_ufs = px.bar(
                dados_ufs,
                x="sigla_uf",
                y="pib_per_capita",
                text_auto='.0f',
                labels={"sigla_uf": "Estado", "pib_per_capita": "PIB per capita (R$)"},
                color="pib_per_capita",
                color_continuous_scale="RdYlGn"
            )
            st.plotly_chart(fig_bar_pc_ufs, use_container_width=True)
        else:
            st.warning("Dados não disponíveis")
    
    # Tabs para análises detalhadas
    st.markdown("---")
    tab1, tab2 = st.tabs(["📋 Tabela Comparativa", "🧩 Estrutura Setorial"])
    
    with tab1:
        st.markdown("**Indicadores Consolidados por Estado**")
        st.caption(f"Dados referentes ao ano {ano_ref_comp}")
        
        # Criar tabela detalhada
        tabela_ufs = []
        dados_ano = df[(df["sigla_uf"].isin(ufs_sel)) & (df["ano"] == ano_ref_comp)]
        
        for uf_item in ufs_sel:
            dados_uf = dados_ano[dados_ano["sigla_uf"] == uf_item]
            
            if not dados_uf.empty:
                pib = dados_uf["pib_total"].sum()
                pop = (dados_uf["pib_total"] / dados_uf["pib_per_capita"]).sum() * 1000
                ppc = pib / (pop / 1000) if pop > 0 else 0
                n_mun = dados_uf["nome_municipio"].nunique()
                
                # Calcular crescimento
                crescimento = calcular_crescimento_periodo(df, uf_item, "sigla_uf", ano_intervalo[0], ano_intervalo[1])
                
                # Composição setorial
                vab_total = dados_uf["vab_total"].sum()
                if vab_total > 0:
                    agro = (dados_uf["vab_agropecuaria"].sum() / vab_total) * 100
                    ind = (dados_uf["vab_industria"].sum() / vab_total) * 100
                    serv = (dados_uf["vab_servicos"].sum() / vab_total) * 100
                    adm = (dados_uf["vab_adm_defesa_educacao_saude"].sum() / vab_total) * 100
                else:
                    agro = ind = serv = adm = 0
                
                tabela_ufs.append({
                    "UF": uf_item,
                    "Nº Municípios": n_mun,
                    "População": f"{int(pop):,}".replace(",", "."),
                    "PIB Total (R$ bi)": f"{pib / 1_000_000:.1f}",
                    "PIB per capita (R$)": f"{ppc:,.0f}".replace(",", "."),
                    f"Crescimento {ano_intervalo[0]}–{ano_intervalo[1]}": f"{crescimento:.1f}%" if crescimento else "N/A",
                    "Agropecuária (%)": f"{agro:.1f}",
                    "Indústria (%)": f"{ind:.1f}",
                    "Serviços (%)": f"{serv:.1f}",
                    "Adm. Pública (%)": f"{adm:.1f}"
                })
        
        if tabela_ufs:
            df_tab_ufs = pd.DataFrame(tabela_ufs)
            st.dataframe(df_tab_ufs, use_container_width=True)
        else:
            st.warning("Dados não disponíveis")
    
    with tab2:
        col_set1, col_set2 = st.columns(2)
        
        with col_set1:
            st.markdown("**Composição Setorial Comparada**")
            st.caption(f"Participação dos setores no VAB - {ano_ref_comp}")
            
            composicoes = []
            for uf_item in ufs_sel:
                comp = composicao_setorial_uf(df, uf_item, ano_ref_comp)
                if comp is not None and not comp.empty:
                    comp["UF"] = uf_item
                    composicoes.append(comp)
            
            if composicoes:
                df_comp = pd.concat(composicoes, ignore_index=True)
                
                fig_comp = px.bar(
                    df_comp,
                    x="UF",
                    y="Participação (%)",
                    color="Setor",
                    text_auto='.1f',
                    color_discrete_map=CORES_SETORES
                )
                fig_comp.update_layout(barmode='stack')
                st.plotly_chart(fig_comp, use_container_width=True)
            else:
                st.warning("Dados não disponíveis")
        
        with col_set2:
            st.markdown("**Valores Absolutos por Setor**")
            st.caption(f"VAB em R$ bilhões - {ano_ref_comp}")
            
            dados_setores = df[(df["sigla_uf"].isin(ufs_sel)) & (df["ano"] == ano_ref_comp)].groupby("sigla_uf").agg({
                "vab_agropecuaria": "sum",
                "vab_industria": "sum",
                "vab_servicos": "sum",
                "vab_adm_defesa_educacao_saude": "sum"
            }).reset_index()
            
            if not dados_setores.empty:
                # Converter para bilhões e formato long
                dados_setores["Agropecuária"] = dados_setores["vab_agropecuaria"] / 1_000_000
                dados_setores["Indústria"] = dados_setores["vab_industria"] / 1_000_000
                dados_setores["Serviços"] = dados_setores["vab_servicos"] / 1_000_000
                dados_setores["Administração Pública"] = dados_setores["vab_adm_defesa_educacao_saude"] / 1_000_000
                
                df_long = dados_setores.melt(
                    id_vars=["sigla_uf"],
                    value_vars=["Agropecuária", "Indústria", "Serviços", "Administração Pública"],
                    var_name="Setor",
                    value_name="VAB (R$ bi)"
                )
                
                fig_abs = px.bar(
                    df_long,
                    x="Setor",
                    y="VAB (R$ bi)",
                    color="sigla_uf",
                    barmode='group',
                    text_auto='.1f',
                    color_discrete_sequence=PALETA_COMPARACAO,
                    labels={"sigla_uf": "Estado"}
                )
                st.plotly_chart(fig_abs, use_container_width=True)
            else:
                st.warning("Dados não disponíveis")

# ===============================
# COMPARAÇÃO ENTRE MUNICÍPIOS
# ===============================
if modo == "Comparar municípios" and municipios_sel and len(municipios_sel) > 1:
    st.markdown("---")
    
    # Obter UFs dos municípios selecionados
    ufs_municipios = df[df["nome_municipio"].isin(municipios_sel)]["sigla_uf"].unique()
    
    if len(ufs_municipios) == 1:
        subtitulo = f"Municípios de {ufs_municipios[0]}"
    elif uf != "Todas":
        subtitulo = f"Municípios de {uf}"
    elif regiao != "Brasil":
        subtitulo = f"Municípios da região {regiao}"
    else:
        subtitulo = f"Municípios de {len(ufs_municipios)} estados diferentes"
    
    st.subheader("🔍 Comparação Direta entre Municípios")
    st.caption(f"{subtitulo} • Análise lado a lado para identificar diferenças e padrões")

    ano_ref = min(ano_ref, 2021)
    
    col9, col10 = st.columns(2)
    
    # Obter dados dos municípios selecionados (sem filtro de UF, já que pode ser multi-UF)
    dados_comparacao = df[(df["nome_municipio"].isin(municipios_sel)) & (df["ano"] == ano_ref)]
    
    # Aplicar filtro de região se necessário
    if regiao != "Brasil":
        dados_comparacao = dados_comparacao[dados_comparacao["nome_grande_regiao"] == regiao]
    if uf != "Todas":
        dados_comparacao = dados_comparacao[dados_comparacao["sigla_uf"] == uf]
    
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
    
    # st.markdown(f"**Tabela Comparativa Consolidada - {ano_ref}**")


    # Análises Avançadas (em Tabs)
    st.markdown("---")
    tab1, tab2 = st.tabs(["📋 Tabela Detalhada", "🧩 Composição Setorial"])
    
    with tab1:
        st.markdown("**Dados Consolidados - Comparação Completa**")
        st.caption(f"Indicadores detalhados dos {len(municipios_sel)} municípios selecionados para o ano {ano_ref}")
        
        if not dados_comparacao.empty:
            # Criar tabela expandida com mais indicadores
            ano_fim = min(ano_intervalo[1], 2021)
            tabela_detalhada = []
            
            for _, row in dados_comparacao.iterrows():
                municipio = row["nome_municipio"]
                crescimento = calcular_crescimento_periodo(df, municipio, "nome_municipio", ano_intervalo[0], ano_fim)
                
                # Calcular população
                populacao = (row["pib_total"] / row["pib_per_capita"]) * 1000 if row["pib_per_capita"] > 0 else 0
                
                # Dependência pública
                dependencia = (row["vab_adm_defesa_educacao_saude"] / row["vab_total"]) * 100 if row["vab_total"] > 0 else 0
                
                item = {
                    "Município": municipio,
                    "População": f"{int(populacao):,}".replace(",", "."),
                    "PIB Total (R$ mi)": f"{row['pib_total'] / 1000:.1f}",
                    "PIB per capita (R$)": f"{row['pib_per_capita']:,.0f}".replace(",", "."),
                    "Agropecuária (%)": f"{(row['vab_agropecuaria'] / row['vab_total'] * 100):.1f}" if row['vab_total'] > 0 else "0.0",
                    "Indústria (%)": f"{(row['vab_industria'] / row['vab_total'] * 100):.1f}" if row['vab_total'] > 0 else "0.0",
                    "Serviços (%)": f"{(row['vab_servicos'] / row['vab_total'] * 100):.1f}" if row['vab_total'] > 0 else "0.0",
                    "Adm. Pública (%)": f"{dependencia:.1f}",
                    f"Crescimento {ano_intervalo[0]}–{ano_fim}": f"{crescimento:.1f}%" if crescimento else "N/A",
                    "Setor Dominante": row["atividade_maior_vab"]
                }
                
                # Adicionar coluna UF se for comparação multi-UF
                if len(ufs_municipios) > 1:
                    item = {"UF": row["sigla_uf"], **item}
                
                tabela_detalhada.append(item)
            
            df_table_detalhada = pd.DataFrame(tabela_detalhada)
            st.dataframe(df_table_detalhada, use_container_width=True)
        else:
            st.warning("Dados não disponíveis")
    
    with tab2:
        col_comp1, col_comp2 = st.columns(2)
        
        with col_comp1:
            st.markdown("**Composição Setorial - Comparação lado a lado**")
            st.caption("Participação de cada setor no Valor Adicionado Bruto - ano {}".format(ano_ref))
            
            if not dados_comparacao.empty:
                # Preparar dados para gráfico empilhado
                composicoes_munic = []
                
                for _, row in dados_comparacao.iterrows():
                    if row["vab_total"] > 0:
                        composicoes_munic.append({
                            "Município": row["nome_municipio"],
                            "Setor": "Agropecuária",
                            "Participação (%)": (row["vab_agropecuaria"] / row["vab_total"]) * 100
                        })
                        composicoes_munic.append({
                            "Município": row["nome_municipio"],
                            "Setor": "Indústria",
                            "Participação (%)": (row["vab_industria"] / row["vab_total"]) * 100
                        })
                        composicoes_munic.append({
                            "Município": row["nome_municipio"],
                            "Setor": "Serviços",
                            "Participação (%)": (row["vab_servicos"] / row["vab_total"]) * 100
                        })
                        composicoes_munic.append({
                            "Município": row["nome_municipio"],
                            "Setor": "Administração Pública",
                            "Participação (%)": (row["vab_adm_defesa_educacao_saude"] / row["vab_total"]) * 100
                        })
                
                df_comp_stacked = pd.DataFrame(composicoes_munic)
                
                fig_comp_stacked = px.bar(
                    df_comp_stacked,
                    x="Município",
                    y="Participação (%)",
                    color="Setor",
                    text_auto='.1f',
                    color_discrete_map=CORES_SETORES
                )
                fig_comp_stacked.update_layout(barmode='stack')
                st.plotly_chart(fig_comp_stacked, use_container_width=True)
            else:
                st.warning("Dados não disponíveis")
        
        with col_comp2:
            st.markdown("**Comparação por setor - Valores absolutos**")
            st.caption("Valor Adicionado Bruto (VAB) em R$ milhões - ano {}".format(ano_ref))
            
            if not dados_comparacao.empty:
                # Preparar dados para gráfico de barras agrupadas
                setores_absolutos = []
                
                for _, row in dados_comparacao.iterrows():
                    setores_absolutos.append({
                        "Município": row["nome_municipio"],
                        "Agropecuária": row["vab_agropecuaria"] / 1000,
                        "Indústria": row["vab_industria"] / 1000,
                        "Serviços": row["vab_servicos"] / 1000,
                        "Administração Pública": row["vab_adm_defesa_educacao_saude"] / 1000
                    })
                
                df_setores_abs = pd.DataFrame(setores_absolutos)
                
                # Transformar para formato long
                df_setores_long = df_setores_abs.melt(
                    id_vars=["Município"],
                    var_name="Setor",
                    value_name="VAB (R$ mi)"
                )
                
                fig_setores_grouped = px.bar(
                    df_setores_long,
                    x="Setor",
                    y="VAB (R$ mi)",
                    color="Município",
                    barmode='group',
                    text_auto='.1f',
                    color_discrete_sequence=PALETA_COMPARACAO
                )
                st.plotly_chart(fig_setores_grouped, use_container_width=True)
            else:
                st.warning("Dados não disponíveis")

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
