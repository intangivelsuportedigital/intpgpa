import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ✅ Criando abas no topo
abas = ["📊 Auditoria dos Níveis", "📂 Carregar Dados"]
aba_selecionada = st.tabs(abas)

# URL do CSV no GitHub (substitua pelo caminho correto do seu repositório)
csv_url = "https://raw.githubusercontent.com/intangivelsuportedigital/intpgpa/main/edr9_salvamentos.csv"

# ✅ 🟢 ABA 1: Carregar Dados
with aba_selecionada[1]:  
    st.title("📂 Carregar e Visualizar Dados")

    # Upload do arquivo CSV
    uploaded_file = st.file_uploader("📂 Faça upload do arquivo CSV", type=["csv"])

    # Verifica se o usuário fez upload do arquivo ou deseja usar o CSV padrão
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, encoding="ISO-8859-1", sep=";", on_bad_lines="skip")
            source = "📤 **Dados carregados via upload**"
        except Exception as e:
            st.error(f"❌ Erro ao carregar o arquivo: {e}")
            st.stop()
    elif st.button("Usar CSV Padrão"):
        try:
            df = pd.read_csv(csv_url, encoding="ISO-8859-1", sep=";", on_bad_lines="skip")
            source = "🌍 **Dados carregados do repositório GitHub**"
        except Exception as e:
            st.error(f"❌ Erro ao carregar o arquivo do GitHub: {e}")
            st.stop()
    else:
        st.warning("📌 Por favor, faça upload de um CSV ou clique em 'Usar CSV Padrão'.")
        st.stop()

    # Exibe a fonte dos dados
    st.write(source)

    # Exibe os dados carregados
    st.write("📋 **Visualização dos Dados**")
    st.dataframe(df)

# ✅ 🟢 ABA 2: Auditoria dos Níveis
with aba_selecionada[0]:  
    st.title("📊 Auditoria dos Níveis de Escavação")

    # ✅ **Filtrar os registros de "controle de escavação"**
    if "branchTipoAtividade" not in df.columns:
        st.error("❌ A coluna 'branchTipoAtividade' não foi encontrada no CSV. Verifique o nome correto.")
        st.stop()

    df_controle = df[df["branchTipoAtividade"] == "controle de escavação"]

    # ✅ **Corrigir a exibição da coluna locus (remover .0000)**
    if "locus" in df_controle.columns:
        df_controle["locus"] = df_controle["locus"].apply(lambda x: int(x) if isinstance(x, (int, float)) else x)

    # ✅ **Criar tabela de auditoria dos níveis**
    colunas_necessarias = {"sitio", "locus", "UE", "nivel", "branchAtividadeControleEscavacao"}
    colunas_existentes = set(df_controle.columns)

    if not colunas_necessarias.issubset(colunas_existentes):
        st.error(f"❌ O CSV não contém todas as colunas necessárias! Encontradas: {colunas_existentes}")
        st.stop()

    df_niveis = df_controle.pivot_table(
        index=["sitio", "locus", "UE", "nivel"],
        columns="branchAtividadeControleEscavacao",
        aggfunc="size",
        fill_value=0
    ).reset_index()

    # Criar a coluna de status
    df_niveis["status"] = "Aberto e Não Fechado"  # Default

    # ✅ **Definir status baseado nos registros**
    df_niveis.loc[
        (df_niveis.get("abrir Nível", 0) > 0) & (df_niveis.get("fechar Nível", 0) > 0),
        "status"
    ] = "Aberto e Fechado"

    df_niveis.loc[
        (df_niveis.get("abrir Nível", 0) == 0) & (df_niveis.get("fechar Nível", 0) > 0),
        "status"
    ] = "Fechado Sem Registro de Abertura"

    # ✅ **Função para aplicar estilos na tabela**
    def highlight_status(val):
        color = "black"
        background = "white"
        
        if val == "Aberto e Não Fechado":
            background = "yellow"
        elif val == "Fechado Sem Registro de Abertura":
            background = "red"
        elif val == "Aberto e Fechado":
            background = "lightgray"

        return f"background-color: {background}; color: {color};"

    # Aplicar estilo na tabela
    styled_df = df_niveis.style.applymap(highlight_status, subset=["status"])

    # ✅ **Interface do Dashboard**
    st.write("📋 **Tabela de Auditoria dos Níveis Escavados**")
    st.dataframe(styled_df)

    # ✅ **Gráfico de Auditoria**
    st.write("📊 **Gráfico de Status dos Níveis**")
    fig, ax = plt.subplots()
    df_niveis["status"].value_counts().plot(kind="bar", ax=ax)
    ax.set_xlabel("Status")
    ax.set_ylabel("Quantidade")
    ax.set_title("Distribuição dos Níveis de Escavação")
    st.pyplot(fig)

    st.success("🚀 Auditoria concluída com sucesso!")
