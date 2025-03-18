import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Criando abas principais na primeira linha
aba_principal = st.radio("🔹 Selecione uma seção:", ["📂 Carregar Dados", "🌎 Selecionar Sítio"], horizontal=True)

# Caminho do CSV unificado
csv_url = "/mnt/data/Dados_Unificados.csv"

# Usar sessão do Streamlit para armazenar o DataFrame entre abas
if "df" not in st.session_state:
    st.session_state.df = None  # Inicializar df na sessão
if "sitio_selecionado" not in st.session_state:
    st.session_state.sitio_selecionado = None  # Inicializar sítio

# Seção: Carregar Dados
if aba_principal == "📂 Carregar Dados":
    st.title("📂 Carregar e Visualizar Dados")

    # Upload do arquivo CSV
    uploaded_file = st.file_uploader("📂 Faça upload do arquivo CSV", type=["csv"])

    if uploaded_file is not None:
        try:
            st.session_state.df = pd.read_csv(uploaded_file, encoding="utf-8", sep=",", on_bad_lines="skip")
            source = "📤 **Dados carregados via upload**"
        except Exception as e:
            st.error(f"❌ Erro ao carregar o arquivo: {e}")
            st.stop()
    elif st.button("Usar CSV Padrão"):
        try:
            st.session_state.df = pd.read_csv(csv_url, encoding="utf-8", sep=",", on_bad_lines="skip")
            source = "🌍 **Dados carregados do arquivo unificado**"
        except Exception as e:
            st.error(f"❌ Erro ao carregar o arquivo: {e}")
            st.stop()
    else:
        st.warning("📌 Por favor, faça upload de um CSV ou clique em 'Usar CSV Padrão'.")
        st.stop()

    st.write(source)

    if st.session_state.df is not None:
        st.write("📋 **Visualização dos Dados**")
        st.dataframe(st.session_state.df)

# Seção: Selecionar Sítio
elif aba_principal == "🌎 Selecionar Sítio":
    st.title("🌎 Selecione um Sítio para Análise")

    if st.session_state.df is None:
        st.error("❌ Nenhum arquivo CSV carregado! Vá para '📂 Carregar Dados' e faça o upload.")
        st.stop()

    # Remover valores nulos e criar lista de sítios
    lista_sitios = st.session_state.df["sitio"].dropna().unique().tolist()
    st.session_state.sitio_selecionado = st.selectbox("🔍 Escolha um sítio:", ["Todos"] + lista_sitios)

    # Filtrar DataFrame
    df_filtrado = st.session_state.df.copy()
    if st.session_state.sitio_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["sitio"] == st.session_state.sitio_selecionado]

    # Aba para auditoria
    aba_sitio = st.radio("📋 Escolha uma análise:", ["📊 Auditoria"], horizontal=True)

    if aba_sitio == "📊 Auditoria":
        st.title(f"📊 Auditoria dos Níveis - {st.session_state.sitio_selecionado}")

        if "branchTipoAtividade" not in df_filtrado.columns:
            st.error("❌ A coluna 'branchTipoAtividade' não foi encontrada no CSV. Verifique o nome correto.")
            st.stop()

        df_controle = df_filtrado[df_filtrado["branchTipoAtividade"] == "controle de escavação"]

        # Corrigir exibição da coluna locus
        if "locus" in df_controle.columns:
            df_controle["locus"] = df_controle["locus"].apply(lambda x: int(x) if isinstance(x, (int, float)) else x)

        # Criar tabela de auditoria dos níveis
        colunas_necessarias = {"sitio", "locus", "UE", "nivel", "branchAtividadeControleEscavacao"}
        if not colunas_necessarias.issubset(df_controle.columns):
            st.error(f"❌ O CSV não contém todas as colunas necessárias! Encontradas: {df_controle.columns}")
            st.stop()

        df_niveis = df_controle.pivot_table(
            index=["sitio", "locus", "UE", "nivel"],
            columns="branchAtividadeControleEscavacao",
            aggfunc="size",
            fill_value=0
        ).reset_index()

        df_niveis["status"] = "Aberto e Não Fechado"
        df_niveis.loc[(df_niveis.get("abrir Nível", 0) > 0) & (df_niveis.get("fechar Nível", 0) > 0), "status"] = "Aberto e Fechado"
        df_niveis.loc[(df_niveis.get("abrir Nível", 0) == 0) & (df_niveis.get("fechar Nível", 0) > 0), "status"] = "Fechado Sem Registro de Abertura"

        # Aplicar estilos na tabela
        def highlight_status(val):
            color_map = {
                "Aberto e Não Fechado": "yellow",
                "Fechado Sem Registro de Abertura": "red",
                "Aberto e Fechado": "lightgray"
            }
            return f"background-color: {color_map.get(val, 'white')}; color: black;"

        styled_df = df_niveis.style.applymap(highlight_status, subset=["status"])
        st.write("📋 **Tabela de Auditoria dos Níveis Escavados**")
        st.dataframe(styled_df)

        # Gráfico
        st.write("📊 **Gráfico de Status dos Níveis**")
        fig, ax = plt.subplots()
        df_niveis["status"].value_counts().plot(kind="bar", ax=ax)
        ax.set_xlabel("Status")
        ax.set_ylabel("Quantidade")
        ax.set_title("Distribuição dos Níveis de Escavação")
        st.pyplot(fig)

        st.success("🚀 Auditoria concluída com sucesso!")