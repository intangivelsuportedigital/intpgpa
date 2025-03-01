import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("📊 Auditoria dos Níveis de Escavação")

# URL do CSV no GitHub (substitua pelo caminho correto do seu repositório)
csv_url = "https://raw.githubusercontent.com/intangivelsuportedigital/intpgpa/main/edr9_salvamentos.csv"

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

# ✅ **Filtrar os registros de "controle de escavação"**
if "branchTipoAtividade" not in df.columns:
    st.error("❌ A coluna 'branchTipoAtividade' não foi encontrada no CSV. Verifique o nome correto.")
    st.stop()

df_controle = df[df["branchTipoAtividade"] == "controle de escavação"]

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
    color = "white"
    background = "white"
    
    if val == "Aberto e Não Fechado":
        background = "yellow"
        color = "black"
    elif val == "Fechado Sem Registro de Abertura":
        background = "red"
        color = "black"

    return f"background-color: {background}; color: {color};"

# Aplicar estilo na tabela
styled_df = df_niveis.style.applymap(highlight_status, subset=["status"])

# ✅ **Interface do Dashboard**
st.write("📋 **Tabela de Auditoria dos Níveis Escavados**")
st.dataframe(styled_df)

# ✅ **Filtros Interativos**
sitios = df_niveis["sitio"].unique()
locus = df_niveis["locus"].unique()
ues = df_niveis["UE"].unique()  # Alterado "ue" para "UE"

filtro_sitio = st.selectbox("Filtrar por Sítio:", ["Todos"] + list(sitios))
filtro_locus = st.selectbox("Filtrar por Locus:", ["Todos"] + list(locus))
filtro_ue = st.selectbox("Filtrar por UE:", ["Todos"] + list(ues))

df_filtrado = df_niveis.copy()

if filtro_sitio != "Todos":
    df_filtrado = df_filtrado[df_filtrado["sitio"] == filtro_sitio]
if filtro_locus != "Todos":
    df_filtrado = df_filtrado[df_filtrado["locus"] == filtro_locus]
if filtro_ue != "Todos":
    df_filtrado = df_filtrado[df_filtrado["UE"] == filtro_ue]  # Alterado "ue" para "UE"

st.write("📋 **Níveis Filtrados**")
st.dataframe(df_filtrado.style.applymap(highlight_status, subset=["status"]))

# ✅ **Gráfico de Auditoria**
st.write("📊 **Gráfico de Status dos Níveis**")
fig, ax = plt.subplots()
df_niveis["status"].value_counts().plot(kind="bar", ax=ax)
ax.set_xlabel("Status")
ax.set_ylabel("Quantidade")
ax.set_title("Distribuição dos Níveis de Escavação")
st.pyplot(fig)

st.success("🚀 Auditoria concluída com sucesso!")
