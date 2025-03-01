# Instalar bibliotecas necessárias
!pip install streamlit pandas

# Criar um arquivo Python para o dashboard
code = """
import streamlit as st
import pandas as pd

# Configuração do título
st.title('📊 Dashboard de CSV no Streamlit')

# Upload do arquivo CSV
uploaded_file = st.file_uploader("Faça upload do arquivo CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("📋 **Visualização dos Dados:**")
    st.dataframe(df)

    # Estatísticas rápidas
    st.write("📊 **Resumo Estatístico:**")
    st.write(df.describe())

    # Gráfico de barras (caso tenha colunas numéricas)
    if df.select_dtypes(include=['number']).shape[1] > 0:
        st.write("📈 **Gráfico de Barras**")
        colunas_numericas = df.select_dtypes(include=['number']).columns
        opcao = st.selectbox("Escolha uma coluna para visualizar:", colunas_numericas)
        st.bar_chart(df[opcao])
"""

# Salvar código em um arquivo Python
with open("app.py", "w") as f:
    f.write(code)

print("Arquivo app.py criado! Agora vá para o próximo passo.")    
