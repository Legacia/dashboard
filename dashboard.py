
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import os

COLAB_FILE = "Employees Forecast P&D(2025).csv"
LICENCA_FILE = "licencas.csv"

@st.cache_data
def carregar_colaboradores():
    if not os.path.exists(COLAB_FILE):
        return pd.DataFrame()
    df = pd.read_csv(COLAB_FILE)
    df.columns = df.columns.str.strip()
    for col in ["Salary (month)", "Total Cost (month)", "Total Cost CLT (12 months)",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Total Cost CLT (6 months)"]:
        df[col] = df[col].replace("-", 0).astype(str).str.replace("R\$", "").str.replace(".", "").str.replace(",", ".").astype(float)
    return df

@st.cache_data
def carregar_licencas():
    if not os.path.exists(LICENCA_FILE):
        return pd.DataFrame(columns=["Nome", "Descrição", "Custo Mensal", "Categoria"])
    df = pd.read_csv(LICENCA_FILE)
    df["Custo Mensal"] = df["Custo Mensal"].astype(float)
    return df

st.title("💰 Painel Completo de Custos: Pessoas + Licenças")

df_colab = carregar_colaboradores()
df_lic = carregar_licencas()

# --- Adição de licenças ---
with st.expander("➕ Adicionar nova licença/ferramenta"):
    lic_nome = st.text_input("Nome da licença")
    lic_descricao = st.text_input("Descrição da ferramenta")
    lic_categoria = st.text_input("Categoria (Ex: Infra, Comunicação, BI, etc.)")
    lic_valor = st.number_input("Custo mensal (R$)", min_value=0.0, step=100.0)
    if st.button("Adicionar licença"):
        nova = pd.DataFrame([{
            "Nome": lic_nome,
            "Descrição": lic_descricao,
            "Categoria": lic_categoria,
            "Custo Mensal": lic_valor
        }])
        nova.to_csv(LICENCA_FILE, mode='a', header=not os.path.exists(LICENCA_FILE), index=False)
        st.success(f"Licença '{lic_nome}' adicionada com sucesso.")

# --- Alternância de visualização ---
modo = st.radio("Visualizar:", ["👥 Apenas Pessoas", "🔧 Apenas Licenças", "📊 Todos os Custos"])

if modo == "👥 Apenas Pessoas" or modo == "📊 Todos os Custos":
    df_colab = df_colab.sort_values("Name")
    total_pessoas = df_colab["Total Cost (month)"].sum()
    st.subheader(f"👥 Custo mensal com pessoas: R$ {total_pessoas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    fig1 = px.bar(df_colab, x="Name", y="Total Cost (month)", color="Position", title="Custo por colaborador")
    st.plotly_chart(fig1)

if modo == "🔧 Apenas Licenças" or modo == "📊 Todos os Custos":
    total_lic = df_lic["Custo Mensal"].sum()
    st.subheader(f"🔧 Custo mensal com licenças: R$ {total_lic:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    fig2 = px.bar(df_lic, x="Nome", y="Custo Mensal", color="Categoria", title="Custo por ferramenta")
    st.plotly_chart(fig2)

if modo == "📊 Todos os Custos":
    total_geral = total_pessoas + total_lic
    st.success(f"💵 **Custo Total Mensal: R$ {total_geral:,.2f}**".replace(",", "X").replace(".", ",").replace("X", "."))

