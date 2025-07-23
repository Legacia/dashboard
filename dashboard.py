
import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata
import os

st.set_page_config(page_title="Painel de Custos", layout="wide")

COLAB_FILE = "Employees Forecast P&D(2025).csv"
LICENCA_FILE = "licencas.csv"

@st.cache_data
def carregar_colaboradores():
    try:
        df = pd.read_csv(COLAB_FILE, encoding='utf-8')
    except:
        df = pd.read_csv(COLAB_FILE, encoding='latin1')

    df.columns = [col.strip() for col in df.columns]
    df["Name"] = df["Name"].astype(str).str.strip()
    df["Total Cost (month)"] = df["Total Cost (month)"].astype(str).str.replace("R\$", "", regex=True).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    df["Total Cost (month)"] = pd.to_numeric(df["Total Cost (month)"], errors="coerce").fillna(0.0)
    df["Total Cost (year)"] = df["Total Cost CLT (12 months)"].astype(str).str.replace("R\$", "", regex=True).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    df["Total Cost (year)"] = pd.to_numeric(df["Total Cost (year)"], errors="coerce").fillna(0.0)
    return df

@st.cache_data
def carregar_licencas():
    if not os.path.exists(LICENCA_FILE):
        return pd.DataFrame(columns=["Nome", "Descrição", "Categoria", "Custo Mensal"])
    try:
        df = pd.read_csv(LICENCA_FILE, encoding='utf-8')
    except:
        df = pd.read_csv(LICENCA_FILE, encoding='latin1')
    df.columns = [col.strip() for col in df.columns]
    if "Custo Mensal" in df.columns:
        df["Custo Mensal"] = df["Custo Mensal"].astype(str).str.replace("R\$", "", regex=True).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
        df["Custo Mensal"] = pd.to_numeric(df["Custo Mensal"], errors="coerce").fillna(0.0)
    return df

df_colab = carregar_colaboradores()
df_lic = carregar_licencas()

total_pessoas = df_colab["Total Cost (month)"].sum()
total_licencas = df_lic["Custo Mensal"].sum()
total_geral = total_pessoas + total_licencas

st.title("💼 Painel de Custos - Equipe e Licenças")

col1, col2, col3 = st.columns(3)
col1.subheader(f"👥 Custo com pessoas: R$ {total_pessoas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col2.subheader(f"🔧 Custo com licenças: R$ {total_licencas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col3.subheader(f"📊 Custo total: R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

st.markdown("---")
st.header("👥 Detalhamento dos Colaboradores")
df_colab_sorted = df_colab.sort_values("Name")
st.dataframe(df_colab_sorted[["Name", "Position", "Total Cost (month)", "Total Cost (year)"]])

fig_colab = px.bar(df_colab_sorted, x="Total Cost (month)", y="Name", orientation='h', title="Custo por Colaborador", labels={"Total Cost (month)": "Custo Mensal", "Name": "Colaborador"})
st.plotly_chart(fig_colab, use_container_width=True)

st.markdown("---")
st.header("🔧 Licenças e Ferramentas")
st.dataframe(df_lic)

fig_lic = px.bar(df_lic, x="Custo Mensal", y="Nome", orientation='h', title="Custo com Licenças", labels={"Custo Mensal": "Custo Mensal", "Nome": "Licença"})
st.plotly_chart(fig_lic, use_container_width=True)
