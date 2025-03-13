import streamlit as st
import pandas as pd
import plotly.express as px


# Funções de Formatação
def formatar_moeda(valor, simbolo_moeda="R$"):
    """Formata um valor numérico como moeda."""
    return f"{simbolo_moeda} {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# Funções de Agregação e Cálculo
def calcular_metricas(df):
    """Calcula e retorna métricas de vendas."""
    total_nf = len(df['NF'].unique())
    total_qtd_produto = df['Qtd_Produto'].sum()
    valor_total_item = df['Valor_Total_Item'].sum()
    total_custo_compra = df['Total_Custo_Compra'].sum()
    total_lucro_venda = df['Total_Lucro_Venda_Item'].sum()
    return total_nf, total_qtd_produto, valor_total_item, total_custo_compra, total_lucro_venda

def agrupar_e_somar(df, coluna_agrupamento):
    """Agrupa e soma vendas por uma coluna específica."""
    return df.groupby(coluna_agrupamento).agg(
        {'Valor_Total_Item': 'sum', 'Total_Custo_Compra': 'sum', 'Total_Lucro_Venda_Item': 'sum'}
    ).reset_index()

def produtos_mais_vendidos(df, top_n=10, ordenar_por='Valor_Total_Item'):
    """Retorna os top N produtos mais vendidos."""
    df_agrupado = df.groupby('Descricao_produto')[ordenar_por].sum().reset_index()
    df_ordenado = df_agrupado.sort_values(by=ordenar_por, ascending=False)
    return df_ordenado.head(top_n)

# Funções de Filtro
def aplicar_filtros(df, vendedor='Todos', mes='Todos', ano='Todos', situacao='Todos'):
    """Aplica filtros ao DataFrame."""
    df_filtrado = df.copy()
    if vendedor != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Vendedor'] == vendedor]
    if mes != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Mes'] == mes]
    if ano != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Ano'] == ano]
    if situacao != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['situacao'] == situacao]
    return df_filtrado

# Funções de Gráficos
def criar_grafico_barras(df, x, y, title, labels):
    """Cria e retorna um gráfico de barras com layout aprimorado."""
    fig = px.bar(df, x=x, y=y, title=title, labels=labels, 
                 color=y, text_auto=True, template="plotly_white", 
                 hover_data={x: False, y: ":,.2f"})

    fig.update_traces(marker=dict(line=dict(color='black', width=1)), 
                      hoverlabel=dict(bgcolor="white", font_size=14, 
                                      font_family="Arial, sans-serif"))

    fig.update_layout(yaxis_title=labels.get(y, y), 
                      xaxis_title=labels.get(x, x), 
                      showlegend=False, height=400)

    return fig

# tab1, tab2 = st.tabs(["Visão Geral", "Comparativo de Períodos"])


# with tab1:
def renderizar_pagina_vendas(df):
    
    vendedores = df['Vendedor'].unique().tolist()
    mes = df['Mes'].unique().tolist()
    ano = df['Ano'].unique().tolist()
    situacao = df['situacao'].unique().tolist()
    cliente = df['Cliente'].unique().tolist()

    with st.expander("Filtros"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            vendedor_selecionado = st.selectbox("Selecionar Vendedor", options=['Todos'] + vendedores)
        with col2:
            mes_selecionado = st.selectbox("Selecionar Mes", options=['Todos'] + mes)
        with col3:
            ano_selecionado = st.selectbox("Selecionar Ano", options=['Todos'] + ano)
        with col4:
            situacao_selecionada = st.selectbox('Selecione a Situação', options=['Todos'] + situacao)

    df_filtrado = aplicar_filtros(df, vendedor_selecionado, mes_selecionado, ano_selecionado, situacao_selecionada)

    
    total_nf, total_qtd_produto, valor_total_item, total_custo_compra, total_lucro_venda = calcular_metricas(df_filtrado)
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total de Notas", f"{total_nf}")
    col2.metric("Total de Produtos", f"{total_qtd_produto}")
    col3.metric("Faturamento Total", formatar_moeda(valor_total_item))
    col4.metric("Custo Total", formatar_moeda(total_custo_compra))
    col5.metric("Lucro Total", formatar_moeda(total_lucro_venda))

    def criar_grafico_meses(df):
        df_meses = df.groupby('Mes').agg({'Valor_Total_Item': 'sum'}).reset_index()
        df_meses = df_meses.sort_values(by='Mes') 

        labels = {'Mes': 'Mês', 'Valor_Total_Item': 'Valor Total de Venda'}
        fig = criar_grafico_barras(df_meses, 'Mes', 'Valor_Total_Item', 'Vendas por Mês', labels)

        
        fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(1, 13)),
                ticktext=['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            )
        )

        return fig
    
    def criar_grafico_dias(df, mes_selecionado):
        """Cria um gráfico de vendas por dia dentro do mês selecionado."""
        if mes_selecionado == 'Todos':
            return None  # Se nenhum mês foi selecionado, não gera gráfico

        df_dias = df[df['Mes'] == mes_selecionado].groupby('Dia').agg({'Valor_Total_Item': 'sum'}).reset_index()
        df_dias = df_dias.sort_values(by='Dia')  # Ordena os dias corretamente

        labels = {'Dia': 'Dia do Mês', 'Valor_Total_Item': 'Valor Total de Venda'}
        fig = criar_grafico_barras(df_dias, 'Dia', 'Valor_Total_Item', f'Vendas por Dia - Mês {mes_selecionado}', labels)

        # Ajuste para garantir que todos os dias de 1 a 31 sejam exibidos
        fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(1, 32)),  # De 1 a 31
                ticktext=[str(i) for i in range(1, 32)]
            )
        )

        return fig

    # Verifica se um mês específico foi escolhido e gera o gráfico
    if mes_selecionado != 'Todos':
        st.subheader(f"Vendas por Dia no Mês {mes_selecionado}")
        fig_dias = criar_grafico_dias(df_filtrado, mes_selecionado)
        if fig_dias:
            st.plotly_chart(fig_dias)

    def ranking_clientes(df, top_n=20):
        """Retorna os top N clientes com maior faturamento total, incluindo o número do ranking."""
        df_clientes = df.groupby('Cliente').agg({'Valor_Total_Item': 'sum'}).reset_index()
        df_clientes = df_clientes.sort_values(by='Valor_Total_Item', ascending=False).head(top_n)
        df_clientes['Ranking'] = range(1, len(df_clientes) + 1)  # Adiciona o número do ranking
        df_clientes['Valor_Total_Item'] = df_clientes['Valor_Total_Item'].apply(formatar_moeda)  # Formatar valores
        df_clientes = df_clientes[['Ranking', 'Cliente', 'Valor_Total_Item']]  # Organiza a ordem das colunas
        return df_clientes

    


    # Adicionar o gráfico na página
    fig_meses = criar_grafico_meses(df_filtrado)
    st.plotly_chart(fig_meses)

    # Gráficos
    fig_linha = criar_grafico_barras(agrupar_e_somar(df_filtrado, 'Linha'), 'Linha', 'Valor_Total_Item',
                                    'Vendas por Linha de Produto', {'Valor_Total_Item': 'Valor Total de Venda'})
    st.plotly_chart(fig_linha)

    fig_vendedor = criar_grafico_barras(agrupar_e_somar(df_filtrado, 'Vendedor'), 'Vendedor', 'Valor_Total_Item',
                                        'Vendas por Vendedor', {'Valor_Total_Item': 'Valor Total de Venda'})
    st.plotly_chart(fig_vendedor)

    
    fig_produtos = criar_grafico_barras(produtos_mais_vendidos(df_filtrado), 'Descricao_produto', 'Valor_Total_Item',
                                        'Top 10 Produtos Mais Vendidos',
                                        {'Descricao_produto': 'Produto', 'Valor_Total_Item': 'Valor Total de Venda'})
    st.plotly_chart(fig_produtos)

    # Exibir o ranking em formato de tabela
    st.subheader("Top 20 Clientes por Faturamento Total")
    df_ranking = ranking_clientes(df_filtrado)

    # Resetar o índice do DataFrame para remover o índice padrão
    df_ranking = df_ranking.reset_index(drop=True)

    # Exibir a tabela no Streamlit
    st.dataframe(df_ranking, use_container_width=True)



def renderizar_pagina_comparativo(df):

    st.title('Dashboard de Vendas Comparativo de Períodos')

    col1, col2 = st.columns(2)

    with col1:
        data_inicio_1 = st.date_input("Início do Período 1", pd.to_datetime("2024-01-01").date())
        data_fim_1 = st.date_input("Fim do Período 1", pd.to_datetime("2024-02-28").date())

    with col2:
        data_inicio_2 = st.date_input("Início do Período 2", pd.to_datetime("2024-03-01").date())
        data_fim_2 = st.date_input("Fim do Período 2", pd.to_datetime("2024-03-31").date())

    # Converter datas para datetime64[ns]
    data_inicio_1 = pd.to_datetime(data_inicio_1)
    data_fim_1 = pd.to_datetime(data_fim_1)
    data_inicio_2 = pd.to_datetime(data_inicio_2)
    data_fim_2 = pd.to_datetime(data_fim_2)

    # Converter a coluna 'Data_Emissao' para datetime64[ns] com format='mixed'
    df['Data_Emissao'] = pd.to_datetime(df['Data_Emissao'], format='mixed', dayfirst=True)

    # Função para filtrar e calcular a soma das vendas em um período (otimizada)
    def filtrar_soma_vendas(df, data_col, valor_col, data_inicio, data_fim):
        df_filtrado = df[(df[data_col] >= data_inicio) & (df[data_col] <= data_fim)]
        return df_filtrado[valor_col].sum()

    # Função para comparar dois períodos de venda (otimizada)
    def comparar_periodos(df, data_col, valor_col, periodo1, periodo2):
        soma_periodo1 = filtrar_soma_vendas(df, data_col, valor_col, *periodo1)
        soma_periodo2 = filtrar_soma_vendas(df, data_col, valor_col, *periodo2)

        if soma_periodo1 == 0:
            variacao = "Indefinida" if soma_periodo2 != 0 else "Sem variação"
        else:
            variacao = ((soma_periodo2 - soma_periodo1) / soma_periodo1) * 100

        return soma_periodo1, soma_periodo2, variacao

    # Comparar os períodos de vendas
    soma_periodo1, soma_periodo2, variacao = comparar_periodos(df, 'Data_Emissao', 'Valor_Total_Item', (data_inicio_1, data_fim_1), (data_inicio_2, data_fim_2))

    # Exibir os resultados no Streamlit
    st.subheader("Comparação entre os períodos selecionados:")
    col3, col4, col5 = st.columns(3)
    col3.metric("Vendas Período 1", f"R$ {soma_periodo1:,.2f}")
    col4.metric("Vendas Período 2", f"R$ {soma_periodo2:,.2f}")
    col5.metric("Variação (%)", f"{variacao:.2f}%" if isinstance(variacao, (int, float)) else variacao)

    # ---------------------  GRÁFICO DE BARRAS COMPARATIVO ---------------------

    st.subheader(" Comparação de Vendas por Período")

    # Criando o gráfico de barras
    fig_bar = px.bar(
        x=["Período 1", "Período 2"],
        y=[soma_periodo1, soma_periodo2],
        text=[f"R$ {soma_periodo1:,.2f}", f"R$ {soma_periodo2:,.2f}"],
        color=["Período 1", "Período 2"],
        color_discrete_sequence=["blue", "green"]
    )

    fig_bar.update_layout(
        title="Comparação de Vendas Entre os Períodos",
        xaxis_title="Período",
        yaxis_title="Valor Total",
        showlegend=False
    )

    st.plotly_chart(fig_bar, use_container_width=True)