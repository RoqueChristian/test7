# Seu arquivo principal (ex: meu_app.py)
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


st.set_page_config(page_title="Go MED SAÚDE", page_icon=":bar_chart:", layout="wide")

from meu_app import *
from compras import *

def exibir_cabecalho(img_path, titulo):
    if os.path.exists(img_path):
        col1, col2 = st.columns([1, 12])
        with col1:
            st.image(img_path, width=80)
        with col2:
            st.title(titulo)
    else:
        st.title(titulo)

exibir_cabecalho("go_med_saude.jpeg", "Sistema de Análise")

st.write("")
st.write("")

def carregar_arquivos(tipo: str):
    caminhos = {
        "vendas": "arquivos/df_vendas.csv",
        "compras": "arquivos/df_compra.csv",
    }
    return caminhos.get(tipo, None)

def main():


    with st.sidebar:
        menu_selecionado = option_menu(
            menu_title="Navegação",
            options=["Análise de Vendas", "Análise de Compras"],
            icons=["bar-chart-line", "bar-chart-line"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#3b8c88"},
                "icon": {"color": "orange", "font-size": "25px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#e7ecd0",
                },
                "nav-link-selected": {"background-color": "red"},
            },
        )

    if menu_selecionado == "Análise de Vendas":
        caminho_arquivo = carregar_arquivos("vendas")
        if caminho_arquivo and os.path.exists(caminho_arquivo):
            try:
                df = pd.read_csv(caminho_arquivo)
                if df.empty:
                    st.warning("O arquivo CSV de vendas está vazio.")
                else:
                    tab1, tab2, tab3 = st.tabs(["Visão Geral", "Comparativo de Períodos", "Analise de tickets"])

                    with tab1:
                        renderizar_pagina_vendas(df)

                    with tab2:
                        renderizar_pagina_comparativo(df)

                    with tab3:
                        renderizar_pagina_vendedor(df)

            except Exception as e:
                st.error(f"Ocorreu um erro ao carregar o arquivo de vendas: {e}")
        else:
            st.error("Arquivo de vendas não encontrado!")

    elif menu_selecionado == "Análise de Compras":
        caminho_arquivo = carregar_arquivos("compras")
        if caminho_arquivo and os.path.exists(caminho_arquivo):
            try:
                df_compras = pd.read_csv(caminho_arquivo)
                if df_compras.empty:
                    st.warning("O arquivo CSV de compras está vazio.")
                else:
                    renderizar_pagina_compras(df_compras)

            except Exception as e:
                st.error(f"Ocorreu um erro ao carregar o arquivo de compras: {e}")
        else:
            st.error("Arquivo de compras não encontrado!")

if __name__ == "__main__":
    main()