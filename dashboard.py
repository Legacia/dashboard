
import streamlit as st
import pandas as pd
import plotly.express as px

# Função para carregar e limpar os dados
@st.cache_data
def carregar_dados():
    df = pd.read_csv("Employees Forecast P&D(2025).csv")
    df.columns = df.columns.str.strip()
    colunas_moeda = [
        "Salary (month)", "Total Cost (month)", "Total Cost CLT (12 months)",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Total Cost CLT (6 months)"
    ]
    def limpar_moeda(valor):
        if isinstance(valor, str):
            valor = valor.strip()
            if valor in ["-", ""]:
                return 0.0
            return float(valor.replace("R$", "").replace(".", "").replace(",", "."))
        return valor
    for col in colunas_moeda:
        df[col] = df[col].apply(limpar_moeda)
    return df

df = carregar_dados()

st.title("💰 Dashboard de Custos da Equipe P&D")

# Filtro de colaboradores
colaboradores = st.multiselect("Filtrar colaboradores:", df["Name"].unique(), default=df["Name"].unique())
df_filtrado = df[df["Name"].isin(colaboradores)]

# Métricas principais
custo_total_mensal = df_filtrado["Total Cost (month)"].sum()
custo_total_6m = df_filtrado["Total Cost CLT (6 months)"].sum()
custo_total_12m = df_filtrado["Total Cost CLT (12 months)"].sum()

st.metric("Custo Total Mensal (R$)", f"{custo_total_mensal:,.2f}")
st.metric("Custo Total em 6 Meses (R$)", f"{custo_total_6m:,.2f}")
st.metric("Custo Total em 12 Meses (R$)", f"{custo_total_12m:,.2f}")

# Gráfico de custo mensal por colaborador
fig1 = px.bar(df_filtrado, x="Name", y="Total Cost (month)", title="Custo mensal por colaborador", text_auto=True)
st.plotly_chart(fig1)

# Gráfico de evolução mensal (Jul-Dez)
df_mensal = df_filtrado[["Name", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]].set_index("Name").T
df_mensal_total = df_mensal.sum(axis=1).reset_index()
df_mensal_total.columns = ["Mês", "Custo Total"]

fig2 = px.line(df_mensal_total, x="Mês", y="Custo Total", markers=True, title="Custo total do time (Jul - Dez)")
st.plotly_chart(fig2)
