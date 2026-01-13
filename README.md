# Dashboard de Análise do PIB dos Municípios Brasileiros

Dashboard interativo desenvolvido em Streamlit para análise econômica dos municípios brasileiros com dados do IBGE (2010-2023).

## Como executar

```bash
streamlit run app.py
```

## Funcionalidades

### Modos de Visualização

- **Agregado**: Análise de Brasil, regiões ou UFs completas
- **Comparar Regiões**: Comparação entre Norte, Nordeste, Sudeste, Sul e Centro-Oeste
- **Comparar Estados**: Comparação entre UFs selecionadas
- **Comparar Municípios**: Comparação lado a lado de municípios
- **Município Específico**: Análise detalhada de um município
- **Todos os Municípios**: Análise completa de todos os municípios de uma UF

### Análises Disponíveis

- **KPIs Executivos**: PIB total, PIB per capita, população, crescimento acumulado
- **Evolução Temporal**: Gráficos de linha do PIB e valor adicionado por setor
- **Composição Setorial**: Participação de Agropecuária, Indústria, Serviços e Administração Pública
- **Rankings**: Maiores PIBs e PIBs per capita por município e UF
- **Comparações**: Scatter plots, tabelas consolidadas e análises detalhadas
- **Tabelas Completas**: Dados consolidados com percentuais setoriais

## Estrutura do Projeto

```
├── app.py          # Interface Streamlit
├── data.py         # Funções de processamento de dados
├── raw/            # Dados brutos do IBGE
└── README.md       # Este arquivo
```

## Dependências

- `streamlit`
- `pandas`
- `plotly`

## Fonte dos Dados

Dados oficiais do IBGE sobre PIB dos municípios brasileiros (2010-2023).

---

**Desenvolvido com Streamlit** • Dados: IBGE