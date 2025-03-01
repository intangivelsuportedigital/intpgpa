import streamlit as st
import pandas as pd

st.title("📊 Dashboard Interativo com CSV")

# URL do CSV no GitHub (substitua com o caminho correto do seu repositório)
csv_url = "https://raw.githubusercontent.com/SEU-USUARIO/SEU-REPOSITORIO/main/edr9_salvamentos.csv"

# Opção de upload manual
uploaded_file = st.file_uploader("📂 Faça upload do arquivo CSV", type=["csv"])

# Verifica se o usuário fez upload do arquivo
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    source = "📤 **Dados carregados via upload**"
elif st.button("Usar CSV Padrão"):
    df = pd.read_csv(csv_url)
    source = "🌍 **Dados carregados do repositório GitHub**"
else:
    st.warning("📌 Por favor, faça upload de um CSV ou clique em 'Usar CSV Padrão'.")
    st.stop()

# Exibe a fonte dos dados
st.write(source)

# Exibir uma prévia dos dados
st.write("📋 **Visualização dos Dados:**")
st.dataframe(df)

# Informações do dataset
st.write("📊 **Informações do Dataset:**")
st.write(f"📌 **Total de Linhas:** {df.shape[0]}")
st.write(f"📌 **Total de Colunas:** {df.shape[1]}")
st.write("📌 **Tipos de Dados:**")
st.write(df.dtypes)

# Estatísticas básicas
st.write("📈 **Resumo Estatístico:**")
st.write(df.describe())

# Gráfico de barras interativo (se houver colunas numéricas)
colunas_numericas = df.select_dtypes(include=['number']).columns
if len(colunas_numericas) > 0:
    st.write("📊 **Gráfico de Barras**")
    opcao = st.selectbox("Escolha uma coluna para visualizar:", colunas_numericas)
    st.bar_chart(df[opcao])

# Gráfico de dispersão opcional
if len(colunas_numericas) > 1:
    st.write("📈 **Gráfico de Dispersão**")
    x_col = st.selectbox("Escolha a variável do eixo X:", colunas_numericas)
    y_col = st.selectbox("Escolha a variável do eixo Y:", colunas_numericas)
    st.scatter_chart(df[[x_col, y_col]])

st.success("🚀 Dashboard atualizado com sucesso!")
