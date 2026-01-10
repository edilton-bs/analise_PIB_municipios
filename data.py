import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
    """Carrega os dados do arquivo parquet."""
    return pd.read_parquet("pib_municipios.parquet")


# ===============================
# FUNÇÕES DE FILTRAGEM BASE
# ===============================

def filtrar_dados(df, regiao=None, uf=None, municipios=None, ano_ini=None, ano_fim=None):
    """
    Filtra o DataFrame base por região, UF, municípios e intervalo de anos.
    
    Args:
        df: DataFrame base
        regiao: Nome da região (ex: "Sudeste")
        uf: Sigla da UF (ex: "SP")
        municipios: Lista de nomes de municípios
        ano_ini: Ano inicial
        ano_fim: Ano final
    
    Returns:
        DataFrame filtrado
    """
    df_filtrado = df.copy()
    
    if regiao and regiao != "Brasil":
        df_filtrado = df_filtrado[df_filtrado["nome_grande_regiao"] == regiao]
    
    if uf and uf != "Todas":
        df_filtrado = df_filtrado[df_filtrado["sigla_uf"] == uf]
    
    if municipios:
        df_filtrado = df_filtrado[df_filtrado["nome_municipio"].isin(municipios)]
    
    if ano_ini and ano_fim:
        df_filtrado = df_filtrado[(df_filtrado["ano"] >= ano_ini) & (df_filtrado["ano"] <= ano_fim)]
    
    return df_filtrado


def obter_lista_municipios(df, uf):
    """
    Retorna lista de municípios de uma UF específica.
    
    Args:
        df: DataFrame base
        uf: Sigla da UF
    
    Returns:
        Lista de nomes de municípios ordenada
    """
    if uf and uf != "Todas":
        municipios = df[df["sigla_uf"] == uf]["nome_municipio"].unique()
        return sorted(municipios.tolist())
    return []


def obter_lista_ufs(df, regiao=None):
    """
    Retorna lista de UFs de uma região específica.
    
    Args:
        df: DataFrame base
        regiao: Nome da região (opcional)
    
    Returns:
        Lista de siglas de UFs ordenada
    """
    if regiao and regiao != "Brasil":
        ufs = df[df["nome_grande_regiao"] == regiao]["sigla_uf"].unique()
    else:
        ufs = df["sigla_uf"].unique()
    
    return sorted(ufs.tolist())


# ===============================
# FUNÇÕES DE KPIs
# ===============================

def calcular_kpis_municipio(df, municipio, ano):
    """
    Calcula KPIs para um município específico em um ano.
    
    Args:
        df: DataFrame base
        municipio: Nome do município
        ano: Ano de referência
    
    Returns:
        Dict com KPIs: pib_total, populacao, pib_per_capita, crescimento_ano_anterior, dependencia_publica
    """

    ano2 = min(ano, 2021)  # Limitar ao máximo de 2021 para evitar dados inexistentes de VAB
    # Dados do ano atual
    dados_ano = df[(df["nome_municipio"] == municipio) & (df["ano"] == ano)]

    dados_ano2 = df[(df["nome_municipio"] == municipio) & (df["ano"] == ano2)]
    
    if dados_ano.empty:
        return None
    
    dados_ano = dados_ano.iloc[0]

    dados_ano2 = dados_ano2.iloc[0]
    
    # Dados do ano anterior para calcular crescimento
    dados_ano_anterior = df[(df["nome_municipio"] == municipio) & (df["ano"] == ano - 1)]
    
    crescimento = None
    if not dados_ano_anterior.empty:
        pib_anterior = dados_ano_anterior.iloc[0]["pib_total"]
        crescimento = ((dados_ano["pib_total"] - pib_anterior) / pib_anterior) * 100
    
    # Calcular população (PIB total / PIB per capita)
    populacao = dados_ano["pib_total"] / dados_ano["pib_per_capita"] if dados_ano["pib_per_capita"] > 0 else 0
    
    # Dependência pública (% do VAB de administração pública no VAB total)
    dependencia_publica = (dados_ano2["vab_adm_defesa_educacao_saude"] / dados_ano2["vab_total"]) * 100 if dados_ano2["vab_total"] > 0 else 0
    
    return {
        "pib_total": dados_ano["pib_total"],
        "populacao": int(populacao * 1000),  # Converter de milhares para unidades
        "pib_per_capita": dados_ano["pib_per_capita"],
        "crescimento_ano_anterior": crescimento,
        "dependencia_publica": dependencia_publica,
        "setor_dominante": dados_ano2["atividade_maior_vab"]
    }


def calcular_kpis_uf(df, uf, ano):
    """
    Calcula KPIs agregados para uma UF em um ano.
    
    Args:
        df: DataFrame base
        uf: Sigla da UF
        ano: Ano de referência
    
    Returns:
        Dict com KPIs agregados
    """
    dados_ano = df[(df["sigla_uf"] == uf) & (df["ano"] == ano)]
    dados_ano_anterior = df[(df["sigla_uf"] == uf) & (df["ano"] == ano - 1)]
    
    if dados_ano.empty:
        return None
    
    pib_total = dados_ano["pib_total"].sum()
    pib_total_anterior = dados_ano_anterior["pib_total"].sum() if not dados_ano_anterior.empty else None
    
    # Calcular população total
    populacao_total = (dados_ano["pib_total"] / dados_ano["pib_per_capita"]).sum() * 1000
    
    # PIB per capita médio ponderado
    pib_per_capita_medio = pib_total / (populacao_total / 1000) if populacao_total > 0 else 0
    
    # Crescimento
    crescimento = ((pib_total - pib_total_anterior) / pib_total_anterior) * 100 if pib_total_anterior else None
    
    # Número de municípios
    num_municipios = dados_ano["nome_municipio"].nunique()
    
    return {
        "pib_total": pib_total,
        "populacao_total": int(populacao_total),
        "pib_per_capita_medio": pib_per_capita_medio,
        "crescimento_ano_anterior": crescimento,
        "num_municipios": num_municipios
    }


def calcular_kpis_agregado(df, regiao, ano):
    """
    Calcula KPIs agregados para região ou Brasil.
    
    Args:
        df: DataFrame base
        regiao: Nome da região ou "Brasil"
        ano: Ano de referência
    
    Returns:
        Dict com KPIs agregados
    """
    if regiao == "Brasil":
        dados_ano = df[df["ano"] == ano]
        dados_ano_anterior = df[df["ano"] == ano - 1]
    else:
        dados_ano = df[(df["nome_grande_regiao"] == regiao) & (df["ano"] == ano)]
        dados_ano_anterior = df[(df["nome_grande_regiao"] == regiao) & (df["ano"] == ano - 1)]
    
    if dados_ano.empty:
        return None
    
    pib_total = dados_ano["pib_total"].sum()
    pib_total_anterior = dados_ano_anterior["pib_total"].sum() if not dados_ano_anterior.empty else None
    
    # Calcular população total
    populacao_total = (dados_ano["pib_total"] / dados_ano["pib_per_capita"]).sum() * 1000
    
    # PIB per capita médio
    pib_per_capita_medio = pib_total / (populacao_total / 1000) if populacao_total > 0 else 0
    
    # Crescimento
    crescimento = ((pib_total - pib_total_anterior) / pib_total_anterior) * 100 if pib_total_anterior else None
    
    # Número de municípios
    num_municipios = dados_ano["nome_municipio"].nunique()
    
    return {
        "pib_total": pib_total,
        "populacao_total": int(populacao_total),
        "pib_per_capita_medio": pib_per_capita_medio,
        "crescimento_ano_anterior": crescimento,
        "num_municipios": num_municipios
    }


def calcular_crescimento_periodo(df, entidade, entidade_col, ano_ini, ano_fim):
    """
    Calcula crescimento acumulado entre dois anos para município/UF.
    
    Args:
        df: DataFrame base
        entidade: Nome do município ou UF
        entidade_col: Nome da coluna ('nome_municipio' ou 'sigla_uf')
        ano_ini: Ano inicial
        ano_fim: Ano final
    
    Returns:
        Percentual de crescimento
    """
    dados_ini = df[(df[entidade_col] == entidade) & (df["ano"] == ano_ini)]
    dados_fim = df[(df[entidade_col] == entidade) & (df["ano"] == ano_fim)]
    
    if dados_ini.empty or dados_fim.empty:
        return None
    
    pib_ini = dados_ini["pib_total"].sum()
    pib_fim = dados_fim["pib_total"].sum()
    
    return ((pib_fim - pib_ini) / pib_ini) * 100


# ===============================
# FUNÇÕES DE EVOLUÇÃO TEMPORAL
# ===============================

def dados_evolucao_pib(df, regiao=None, uf=None, municipios=None, ano_ini=None, ano_fim=None):
    """
    Retorna dados de evolução do PIB ao longo do tempo.
    
    Args:
        df: DataFrame base
        regiao: Nome da região
        uf: Sigla da UF
        municipios: Lista de municípios
        ano_ini: Ano inicial
        ano_fim: Ano final
    
    Returns:
        DataFrame com evolução (ano, entidade, pib_total)
    """
    df_filtrado = filtrar_dados(df, regiao=regiao, uf=uf, municipios=municipios, ano_ini=ano_ini, ano_fim=ano_fim)
    
    if municipios:
        # Evolução por município
        df_agrupado = df_filtrado.groupby(["ano", "nome_municipio"]).agg(
            pib_total=("pib_total", "sum")
        ).reset_index()
    elif uf and uf != "Todas":
        # Top 5 municípios da UF
        top_municipios = df_filtrado[df_filtrado["ano"] == ano_fim].nlargest(5, "pib_total")["nome_municipio"].tolist()
        df_top = df_filtrado[df_filtrado["nome_municipio"].isin(top_municipios)]
        df_agrupado = df_top.groupby(["ano", "nome_municipio"]).agg(
            pib_total=("pib_total", "sum")
        ).reset_index()
    else:
        if regiao and regiao == "Brasil":
            top_ufs_ano_fim = df_filtrado[df_filtrado["ano"] == ano_fim].groupby("sigla_uf")["pib_total"].sum().nlargest(5).index.tolist()
        else:
            # se for região específica, pegar todas as UFs da região
            top_ufs_ano_fim = df_filtrado[df_filtrado["ano"] == ano_fim].groupby("sigla_uf")["pib_total"].sum().index.tolist()
        
        df_top_ufs = df_filtrado[df_filtrado["sigla_uf"].isin(top_ufs_ano_fim)]
        df_agrupado = df_top_ufs.groupby(["ano", "sigla_uf"]).agg(
            pib_total=("pib_total", "sum")
        ).reset_index()

    
    return df_agrupado


def dados_evolucao_valor_adicionado(df, municipio=None, uf=None, regiao=None, ano_ini=None, ano_fim=None):
    """
    Retorna evolução do valor adicionado por setor ao longo do tempo.
    
    Args:
        df: DataFrame base
        municipio: Nome do município
        uf: Sigla da UF
        regiao: Nome da região
        ano_ini: Ano inicial
        ano_fim: Ano final
    
    Returns:
        DataFrame com evolução por setor
    """


    # Garantir que o ano final não ultrapasse 2021 (limite dos dados de VAB)
    if ano_fim and ano_fim > 2021:
        ano_fim = 2021

    df_filtrado = filtrar_dados(df, regiao=regiao, uf=uf, municipios=[municipio] if municipio else None, 
                                 ano_ini=ano_ini, ano_fim=ano_fim)

    
    df_agrupado = df_filtrado.groupby("ano").agg({
        "vab_agropecuaria": "sum",
        "vab_industria": "sum",
        "vab_servicos": "sum",
        "vab_adm_defesa_educacao_saude": "sum"
    }).reset_index()
    
    # Renomear colunas para visualização
    df_agrupado = df_agrupado.rename(columns={
        "vab_agropecuaria": "Agropecuária",
        "vab_industria": "Indústria",
        "vab_servicos": "Serviços",
        "vab_adm_defesa_educacao_saude": "Administração Pública"
    })
    
    return df_agrupado


# ===============================
# FUNÇÕES DE RANKING
# ===============================

def ranking_municipios_pib(df, uf, ano, top_n=10):
    """
    Retorna ranking de municípios por PIB total.
    
    Args:
        df: DataFrame base
        uf: Sigla da UF
        ano: Ano de referência
        top_n: Número de municípios no ranking
    
    Returns:
        DataFrame com ranking
    """
    dados = df[(df["sigla_uf"] == uf) & (df["ano"] == ano)]
    ranking = dados.nlargest(top_n, "pib_total")[["nome_municipio", "pib_total"]].copy()
    ranking["pib_total_mi"] = ranking["pib_total"] / 1000  # Converter para milhões
    
    return ranking[["nome_municipio", "pib_total_mi"]].rename(columns={
        "nome_municipio": "Município",
        "pib_total_mi": "PIB Total (R$ mi)"
    })


def ranking_municipios_per_capita(df, uf, ano, top_n=10):
    """
    Retorna ranking de municípios por PIB per capita.
    
    Args:
        df: DataFrame base
        uf: Sigla da UF
        ano: Ano de referência
        top_n: Número de municípios no ranking
    
    Returns:
        DataFrame com ranking
    """
    dados = df[(df["sigla_uf"] == uf) & (df["ano"] == ano)]
    ranking = dados.nlargest(top_n, "pib_per_capita")[["nome_municipio", "pib_per_capita"]].copy()
    
    return ranking.rename(columns={
        "nome_municipio": "Município",
        "pib_per_capita": "PIB per capita (R$)"
    })


def ranking_ufs(df, ano, regiao=None, top_n=None):
    """
    Retorna ranking de UFs por PIB total.
    
    Args:
        df: DataFrame base
        ano: Ano de referência
        regiao: Nome da região (opcional)
        top_n: Número de UFs no ranking (opcional)
    
    Returns:
        DataFrame com ranking
    """
    if regiao and regiao != "Brasil":
        dados = df[(df["ano"] == ano) & (df["nome_grande_regiao"] == regiao)]
    else:
        dados = df[df["ano"] == ano]
    
    ranking = dados.groupby("sigla_uf").agg({
        "pib_total": "sum",
        "nome_municipio": "nunique"
    }).reset_index()
    
    ranking["pib_total_bi"] = ranking["pib_total"] / 1_000_000  # Converter para bilhões
    ranking = ranking.sort_values("pib_total_bi", ascending=False)
    
    if top_n:
        ranking = ranking.head(top_n)
    
    return ranking[["sigla_uf", "pib_total_bi", "nome_municipio"]].rename(columns={
        "sigla_uf": "UF",
        "pib_total_bi": "PIB Total (R$ bi)",
        "nome_municipio": "Nº Municípios"
    })


def ranking_ufs_per_capita(df, ano, regiao=None, top_n=None):
    """
    Retorna ranking de UFs por PIB per capita médio.
    
    Args:
        df: DataFrame base
        ano: Ano de referência
        regiao: Nome da região (opcional)
        top_n: Número de UFs no ranking (opcional)
    
    Returns:
        DataFrame com ranking
    """
    if regiao and regiao != "Brasil":
        dados = df[(df["ano"] == ano) & (df["nome_grande_regiao"] == regiao)]
    else:
        dados = df[df["ano"] == ano]
    
    # Calcular PIB per capita ponderado
    ranking = dados.groupby("sigla_uf").apply(
        lambda x: (x["pib_total"].sum() / ((x["pib_total"] / x["pib_per_capita"]).sum()))
    ).reset_index()
    
    ranking.columns = ["UF", "PIB per capita (R$)"]
    ranking = ranking.sort_values("PIB per capita (R$)", ascending=False)
    
    if top_n:
        ranking = ranking.head(top_n)
    
    return ranking


# ===============================
# FUNÇÕES DE COMPOSIÇÃO SETORIAL
# ===============================

def composicao_setorial_municipio(df, municipio, ano):
    """
    Retorna composição setorial de um município.
    
    Args:
        df: DataFrame base
        municipio: Nome do município
        ano: Ano de referência
    
    Returns:
        DataFrame com participação por setor
    """
    dados = df[(df["nome_municipio"] == municipio) & (df["ano"] == ano)]
    
    if dados.empty:
        return None
    
    dados = dados.iloc[0]
    
    composicao = pd.DataFrame({
        "Setor": ["Agropecuária", "Indústria", "Serviços", "Administração Pública"],
        "Valor": [
            dados["vab_agropecuaria"],
            dados["vab_industria"],
            dados["vab_servicos"],
            dados["vab_adm_defesa_educacao_saude"]
        ]
    })
    
    composicao["Participação (%)"] = (composicao["Valor"] / composicao["Valor"].sum()) * 100
    
    return composicao[["Setor", "Participação (%)"]]


def composicao_setorial_uf(df, uf, ano):
    """
    Retorna composição setorial média de uma UF.
    
    Args:
        df: DataFrame base
        uf: Sigla da UF
        ano: Ano de referência
    
    Returns:
        DataFrame com participação por setor
    """
    dados = df[(df["sigla_uf"] == uf) & (df["ano"] == ano)]
    
    total_vab = dados[["vab_agropecuaria", "vab_industria", "vab_servicos", "vab_adm_defesa_educacao_saude"]].sum()
    
    composicao = pd.DataFrame({
        "Setor": ["Agropecuária", "Indústria", "Serviços", "Administração Pública"],
        "Valor": [
            total_vab["vab_agropecuaria"],
            total_vab["vab_industria"],
            total_vab["vab_servicos"],
            total_vab["vab_adm_defesa_educacao_saude"]
        ]
    })
    
    composicao["Participação (%)"] = (composicao["Valor"] / composicao["Valor"].sum()) * 100
    
    return composicao[["Setor", "Participação (%)"]]


def composicao_setorial_agregado(df, regiao, ano):
    """
    Retorna composição setorial de região ou Brasil.
    
    Args:
        df: DataFrame base
        regiao: Nome da região ou "Brasil"
        ano: Ano de referência
    
    Returns:
        DataFrame com participação por setor
    """
    if regiao == "Brasil":
        dados = df[df["ano"] == ano]
    else:
        dados = df[(df["nome_grande_regiao"] == regiao) & (df["ano"] == ano)]
    
    total_vab = dados[["vab_agropecuaria", "vab_industria", "vab_servicos", "vab_adm_defesa_educacao_saude"]].sum()
    
    composicao = pd.DataFrame({
        "Setor": ["Agropecuária", "Indústria", "Serviços", "Administração Pública"],
        "Valor": [
            total_vab["vab_agropecuaria"],
            total_vab["vab_industria"],
            total_vab["vab_servicos"],
            total_vab["vab_adm_defesa_educacao_saude"]
        ]
    })
    
    composicao["Participação (%)"] = (composicao["Valor"] / composicao["Valor"].sum()) * 100
    
    return composicao[["Setor", "Participação (%)"]]


# ===============================
# FUNÇÕES PARA SCATTER/ANÁLISES
# ===============================

def scatter_pib_vs_per_capita(df, uf, municipio, ano):
    """
    Retorna dados para scatter PIB total vs PIB per capita.
    Retorna o município de referência + 10 municípios com população mais próxima.
    
    Args:
        df: DataFrame base
        uf: Sigla da UF
        municipio: Nome do município
        ano: Ano de referência
    
    Returns:
        DataFrame pronto para scatter plot
    """
    dados = df[(df["sigla_uf"] == uf) & (df["ano"] == ano)].copy()
    
    # Calcular população
    dados["Populacao"] = (dados["pib_total"] / dados["pib_per_capita"]) * 1000
    
    # Obter população do município de referência
    municipio_ref = dados[dados["nome_municipio"] == municipio]
    
    if municipio_ref.empty:
        return pd.DataFrame()
    
    pop_referencia = municipio_ref.iloc[0]["Populacao"]
    
    # Calcular diferença absoluta de população
    dados["Diferenca_Pop"] = (dados["Populacao"] - pop_referencia).abs()
    
    # Pegar município de referência + 10 mais próximos
    municipios_proximos = dados.nsmallest(11, "Diferenca_Pop")
    
    # Calcular dependência pública
    municipios_proximos["Dependência Pública (%)"] = (
        municipios_proximos["vab_adm_defesa_educacao_saude"] / municipios_proximos["vab_total"]
    ) * 100
    
    municipios_proximos["PIB Total (R$ mi)"] = municipios_proximos["pib_total"] / 1000
    
    # Adicionar coluna para destacar o município de referência
    municipios_proximos["É Referência"] = municipios_proximos["nome_municipio"] == municipio
    
    return municipios_proximos[[
        "nome_municipio", "PIB Total (R$ mi)", "pib_per_capita", 
        "Dependência Pública (%)", "Populacao", "É Referência"
    ]].rename(columns={
        "nome_municipio": "Município",
        "pib_per_capita": "PIB per capita (R$)",
        "Populacao": "População"
    })


def scatter_ufs_pib_vs_per_capita(df, ano, regiao=None):
    """
    Retorna dados para scatter de UFs (PIB total vs PIB per capita).
    
    Args:
        df: DataFrame base
        ano: Ano de referência
        regiao: Nome da região (opcional)
    
    Returns:
        DataFrame pronto para scatter plot
    """
    if regiao and regiao != "Brasil":
        dados = df[(df["ano"] == ano) & (df["nome_grande_regiao"] == regiao)]
    else:
        dados = df[df["ano"] == ano]
    
    scatter_data = dados.groupby("sigla_uf").apply(
        lambda x: pd.Series({
            "PIB Total (R$ bi)": x["pib_total"].sum() / 1_000_000,
            "PIB per capita (R$)": x["pib_total"].sum() / ((x["pib_total"] / x["pib_per_capita"]).sum()),
            "Nº Municípios": x["nome_municipio"].nunique()
        })
    ).reset_index()
    
    scatter_data = scatter_data.rename(columns={"sigla_uf": "UF"})
    
    return scatter_data


# ===============================
# FUNÇÕES PARA TABELAS CONSOLIDADAS
# ===============================

def tabela_municipios_completa(df, uf, ano, ano_ini):
    """
    Retorna tabela consolidada de todos os municípios da UF.
    
    Args:
        df: DataFrame base
        uf: Sigla da UF
        ano: Ano de referência
        ano_ini: Ano inicial para calcular crescimento
    
    Returns:
        DataFrame com tabela completa
    """
    dados_ano = df[(df["sigla_uf"] == uf) & (df["ano"] == ano)].copy()
    dados_ano_ini = df[(df["sigla_uf"] == uf) & (df["ano"] == ano_ini)]
    
    # Calcular crescimento
    crescimento_map = {}
    for _, row in dados_ano_ini.iterrows():
        municipio = row["nome_municipio"]
        pib_ini = row["pib_total"]
        dados_fim = dados_ano[dados_ano["nome_municipio"] == municipio]
        if not dados_fim.empty:
            pib_fim = dados_fim.iloc[0]["pib_total"]
            crescimento_map[municipio] = ((pib_fim - pib_ini) / pib_ini) * 100
    
    dados_ano["Crescimento"] = dados_ano["nome_municipio"].map(crescimento_map)
    dados_ano["Dependência Pública (%)"] = (dados_ano["vab_adm_defesa_educacao_saude"] / dados_ano["vab_total"]) * 100
    dados_ano["População"] = ((dados_ano["pib_total"] / dados_ano["pib_per_capita"]) * 1000).astype(int)
    dados_ano["PIB Total (R$ mi)"] = dados_ano["pib_total"] / 1000
    
    tabela = dados_ano[[
        "nome_municipio", "PIB Total (R$ mi)", "pib_per_capita", 
        "Dependência Pública (%)", "Crescimento", "atividade_maior_vab", "População"
    ]].copy()
    
    tabela["Crescimento"] = tabela["Crescimento"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
    tabela["Dependência Pública (%)"] = tabela["Dependência Pública (%)"].round(1)
    
    tabela = tabela.rename(columns={
        "nome_municipio": "Município",
        "pib_per_capita": "PIB per capita (R$)",
        "atividade_maior_vab": "Setor Dominante",
        "Crescimento": f"Crescimento {ano_ini}–{ano}"
    })
    
    return tabela.sort_values("PIB Total (R$ mi)", ascending=False)


def tabela_ufs_completa(df, ano, ano_ini, regiao=None):
    """
    Retorna tabela consolidada de UFs.
    
    Args:
        df: DataFrame base
        ano: Ano de referência
        ano_ini: Ano inicial para calcular crescimento
        regiao: Nome da região (opcional)
    
    Returns:
        DataFrame com tabela completa
    """
    if regiao and regiao != "Brasil":
        dados_ano = df[(df["ano"] == ano) & (df["nome_grande_regiao"] == regiao)]
        dados_ano_ini = df[(df["ano"] == ano_ini) & (df["nome_grande_regiao"] == regiao)]
    else:
        dados_ano = df[df["ano"] == ano]
        dados_ano_ini = df[df["ano"] == ano_ini]
    
    # Agregar por UF
    tabela = dados_ano.groupby("sigla_uf").apply(
        lambda x: pd.Series({
            "PIB Total (R$ bi)": x["pib_total"].sum() / 1_000_000,
            "PIB per capita (R$)": x["pib_total"].sum() / ((x["pib_total"] / x["pib_per_capita"]).sum()),
            "Nº Municípios": x["nome_municipio"].nunique(),
            "Setor Dominante": x.groupby("atividade_maior_vab")["pib_total"].sum().idxmax()
        })
    ).reset_index()
    
    # Calcular crescimento
    crescimento_map = {}
    for uf in tabela["sigla_uf"].unique():
        pib_ini = dados_ano_ini[dados_ano_ini["sigla_uf"] == uf]["pib_total"].sum()
        pib_fim = dados_ano[dados_ano["sigla_uf"] == uf]["pib_total"].sum()
        if pib_ini > 0:
            crescimento_map[uf] = ((pib_fim - pib_ini) / pib_ini) * 100
    
    tabela["Crescimento"] = tabela["sigla_uf"].map(crescimento_map)
    tabela["Crescimento"] = tabela["Crescimento"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
    
    tabela = tabela.rename(columns={
        "sigla_uf": "UF",
        "Crescimento": f"Crescimento {ano_ini}–{ano}"
    })
    
    return tabela.sort_values("PIB Total (R$ bi)", ascending=False)