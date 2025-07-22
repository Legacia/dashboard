
import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(layout="wide")
st.title("💼 Painel de Custos - P&D")

# Constantes
COLAB_FILE = "Employees Forecast P&D(2025).csv"
LICENCA_FILE = "licencas.csv"

# Funções de carregamento
@st.cache_data
def carregar_colaboradores():
    encodings = ["utf-8", "latin1", "utf-16"]
    for enc in encodings:
        try:
            df = pd.read_csv(COLAB_FILE, encoding=enc)
            break
        except:
            continue
    df.fillna("-", inplace=True)
    df["Nome"] = df["Nome"].astype(str)
    df["Total Cost (month)"] = df["Total Cost (month)"].astype(str).str.replace("R\$", "", regex=True).str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)
    df["Total Cost (year)"] = df["Total Cost (year)"].astype(str).str.replace("R\$", "", regex=True).str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)
    df = df.sort_values("Nome")
    return df

@st.cache_data
def carregar_licencas():
    if not os.path.exists(LICENCA_FILE):
        pd.DataFrame(columns=["Licença", "Descrição", "Categoria", "Custo Mensal"]).to_csv(LICENCA_FILE, index=False)
    df = pd.read_csv(LICENCA_FILE, encoding="utf-8")
    df["Custo Mensal"] = df["Custo Mensal"].astype(str).str.replace("R\$", "", regex=True).str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)
    return df

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Carregamento
df_colab = carregar_colaboradores()
df_lic = carregar_licencas()

# Filtros
with st.sidebar:
    st.header("🎯 Filtros")
    periodos = sorted(df_colab["Período"].unique())
    filtro_periodo = st.multiselect("Período", periodos, default=periodos)
    cargos = sorted(df_colab["Position"].unique())
    filtro_cargo = st.multiselect("Cargo", cargos, default=cargos)
    min_val, max_val = df_colab["Total Cost (month)"].min(), df_colab["Total Cost (month)"].max()
    filtro_valor = st.slider("Faixa de Custo Mensal", float(min_val), float(max_val), (float(min_val), float(max_val)))

df_filtrado = df_colab[
    (df_colab["Período"].isin(filtro_periodo)) &
    (df_colab["Position"].isin(filtro_cargo)) &
    (df_colab["Total Cost (month)"] >= filtro_valor[0]) &
    (df_colab["Total Cost (month)"] <= filtro_valor[1])
]

# Métricas
total_pessoas = df_filtrado["Total Cost (month)"].sum()
total_licencas = df_lic["Custo Mensal"].sum()
total_geral = total_pessoas + total_licencas

col1, col2, col3 = st.columns(3)
col1.metric("👥 Custo mensal com pessoas", formatar_moeda(total_pessoas))
col2.metric("🔧 Custo mensal com licenças", formatar_moeda(total_licencas))
col3.metric("📊 Custo mensal total", formatar_moeda(total_geral))

# Gráficos
fig = px.bar(df_filtrado, x="Nome", y="Total Cost (month)", title="Custo Mensal por Colaborador", labels={"Total Cost (month)": "Custo Mensal (R$)"})
fig.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig, use_container_width=True)

# Tabela de colaboradores
st.subheader("📋 Colaboradores")
st.dataframe(df_filtrado, use_container_width=True)

# Tabela de licenças
st.subheader("🔧 Licenças")
st.dataframe(df_lic, use_container_width=True)
