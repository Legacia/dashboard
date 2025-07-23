
import streamlit as st
import pandas as pd
import plotly.express as px
import os

COLAB_FILE = "Employees Forecast P&D(2025).csv"
LICENCA_FILE = "licencas.csv"

# Funções utilitárias

@st.cache_data
def carregar_colaboradores():
    try:
        df = pd.read_csv(COLAB_FILE, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(COLAB_FILE, encoding="latin1")
    df["Name"] = df["Name"].astype(str)
    df["Total Cost (month)"] = (
        df["Total Cost (month)"]
        .astype(str)
        .str.replace("R\$", "", regex=True)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )
    df["Período"] = df.get("Período", pd.Series(["Jul/2025"] * len(df)))
    df["Tipo Contrato"] = df.get("Tipo Contrato", pd.Series(["CLT"] * len(df)))
    df["Position"] = df["Position"].fillna("Não informado")
    df["Total Cost (year)"] = df["Total Cost (month)"] * 12
    df.sort_values("Name", inplace=True)
    return df

@st.cache_data
def carregar_licencas():
    if not os.path.exists(LICENCA_FILE):
        return pd.DataFrame(columns=["Nome", "Descrição", "Categoria", "Custo Mensal"])
    try:
        df = pd.read_csv(LICENCA_FILE, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(LICENCA_FILE, encoding="latin1")
    if "Custo Mensal" in df.columns:
        df["Custo Mensal"] = (
            df["Custo Mensal"]
            .astype(str)
            .str.replace("R\$", "", regex=True)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )
    return df

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Interface

st.set_page_config(layout="wide")
st.title("💼 Painel de Custos P&D")

# Carregar dados
df_colab = carregar_colaboradores()
df_lic = carregar_licencas()

# Filtros
with st.sidebar:
    st.header("🔎 Filtros")
    cargos = st.multiselect("Cargo", options=df_colab["Position"].unique(), default=df_colab["Position"].unique())
    periodos = st.multiselect("Período", options=df_colab["Período"].unique(), default=df_colab["Período"].unique())
    faixa = st.slider("Faixa de custo mensal", float(df_colab["Total Cost (month)"].min()), float(df_colab["Total Cost (month)"].max()), (float(df_colab["Total Cost (month)"].min()), float(df_colab["Total Cost (month)"].max())))

df_filtrado = df_colab[
    (df_colab["Position"].isin(cargos)) &
    (df_colab["Período"].isin(periodos)) &
    (df_colab["Total Cost (month)"] >= faixa[0]) &
    (df_colab["Total Cost (month)"] <= faixa[1])
]

# Cálculos
total_pessoas = df_filtrado["Total Cost (month)"].sum()
total_licencas = df_lic["Custo Mensal"].sum() if not df_lic.empty else 0
total_geral = total_pessoas + total_licencas

# KPIs
col1, col2, col3 = st.columns(3)
col1.subheader(f"👥 Pessoas: {formatar_moeda(total_pessoas)}")
col2.subheader(f"🔧 Licenças: {formatar_moeda(total_licencas)}")
col3.subheader(f"📊 Total: {formatar_moeda(total_geral)}")

# Gráficos
fig = px.bar(df_filtrado, x="Name", y="Total Cost (month)", title="Custos por Colaborador", labels={"Total Cost (month)": "Custo Mensal"}, template="plotly_white")
fig.update_layout(xaxis_title="Nome", yaxis_title="Custo (R$)", xaxis_tickangle=-45)
st.plotly_chart(fig, use_container_width=True)

# Exportação
col4, col5 = st.columns(2)
with col4:
    if st.download_button("📤 Exportar Colaboradores", df_filtrado.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"), file_name="colaboradores_filtrados.csv"):
        st.success("Arquivo de colaboradores exportado com sucesso!")
with col5:
    if not df_lic.empty and st.download_button("📤 Exportar Licenças", df_lic.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"), file_name="licencas.csv"):
        st.success("Arquivo de licenças exportado com sucesso!")
