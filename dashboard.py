
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import csv

# Arquivos
COLAB_FILE = "Employees Forecast P&D(2025).csv"
LICENCA_FILE = "licencas.csv"

# Função robusta de leitura
@st.cache_data
def carregar_colaboradores():
    try:
        df = pd.read_csv(COLAB_FILE, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(COLAB_FILE, encoding="latin1")
    df.fillna("-", inplace=True)
    df["Nome"] = df["Nome"].astype(str)
    df["Total Cost (month)"] = (
        df["Total Cost (month)"]
        .astype(str)
        .str.replace("R\$", "", regex=True)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )
    df["Total Cost (year)"] = (
        df["Total Cost (year)"]
        .astype(str)
        .str.replace("R\$", "", regex=True)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )
    return df

@st.cache_data
def carregar_licencas():
    if not os.path.exists(LICENCA_FILE):
        df = pd.DataFrame(columns=["Nome", "Descrição", "Categoria", "Custo Mensal"])
        df.to_csv(LICENCA_FILE, index=False)
    try:
        df = pd.read_csv(LICENCA_FILE, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(LICENCA_FILE, encoding="latin1")
    df.fillna("-", inplace=True)
    df["Custo Mensal"] = (
        df["Custo Mensal"]
        .astype(str)
        .str.replace("R\$", "", regex=True)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )
    return df

# Carregamento
df_colab = carregar_colaboradores()
df_lic = carregar_licencas()

# Ordenação
df_colab = df_colab.sort_values(by="Nome")

# Interface
st.title("💼 Painel de Custos - P&D")

# Filtros
with st.sidebar:
    st.header("Filtros")
    cargos = st.multiselect("Cargo", sorted(df_colab["Position"].unique()), default=sorted(df_colab["Position"].unique()))
    periodos = st.multiselect("Período", sorted(df_colab["Período"].unique()), default=sorted(df_colab["Período"].unique()))
    min_val, max_val = df_colab["Total Cost (month)"].min(), df_colab["Total Cost (month)"].max()
    faixa = st.slider("Faixa de Valor Mensal", min_val, max_val, (min_val, max_val))

df_filtrado = df_colab[
    (df_colab["Position"].isin(cargos)) &
    (df_colab["Período"].isin(periodos)) &
    (df_colab["Total Cost (month)"].between(faixa[0], faixa[1]))
]

# Totais
total_pessoas = df_filtrado["Total Cost (month)"].sum()
total_lic = df_lic["Custo Mensal"].sum()
total_geral = total_pessoas + total_lic

st.subheader(f"👥 Custo mensal com pessoas: R$ {total_pessoas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
st.subheader(f"🔧 Custo mensal com licenças: R$ {total_lic:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
st.subheader(f"📊 Custo total mensal: R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

# Gráfico
fig = px.bar(df_filtrado, x="Nome", y="Total Cost (month)", color="Position", title="Custo por Colaborador")
st.plotly_chart(fig, use_container_width=True)

# Tabelas
st.write("### 📋 Colaboradores (Filtrados)")
st.dataframe(df_filtrado)

st.write("### 🛠️ Licenças e Ferramentas")
st.dataframe(df_lic)

# Exportação
st.download_button("📥 Exportar Colaboradores CSV", df_filtrado.to_csv(index=False, sep=";", decimal=","), file_name="colaboradores_export.csv", mime="text/csv")
st.download_button("📥 Exportar Licenças CSV", df_lic.to_csv(index=False, sep=";", decimal=","), file_name="licencas_export.csv", mime="text/csv")
