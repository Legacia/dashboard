
import streamlit as st
import pandas as pd
import plotly.express as px

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

st.title("💰 Dashboard de Custos da Equipe P&D")

df = carregar_dados()

# --- Formulário de adição de colaborador ---
with st.expander("➕ Adicionar novo colaborador"):
    nome = st.text_input("Nome")
    cargo = st.text_input("Cargo")
    tipo = st.selectbox("Tipo de contratação", ["CLT", "PJ"])
    salario_mensal = st.number_input("Salário mensal (R$)", min_value=0.0, step=100.0)
    salario_anual = st.number_input("Salário anual (opcional)", min_value=0.0, step=1000.0)

    if st.button("Adicionar ao painel"):
        total_mensal = salario_mensal * (2.8 if tipo == "CLT" else 1.0)
        total_anual = salario_anual if salario_anual > 0 else total_mensal * 12
        novo = {
            "Name": nome,
            "Position": cargo,
            "Hiring": tipo,
            "Salary (month)": salario_mensal,
            "Total Cost (month)": total_mensal,
            "Total Cost CLT (12 months)": total_anual,
            "Jul": total_mensal, "Aug": total_mensal, "Sep": total_mensal,
            "Oct": total_mensal, "Nov": total_mensal, "Dec": total_mensal,
            "Total Cost CLT (6 months)": total_mensal * 6
        }
        df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
        st.success(f"{nome} adicionado ao painel.")

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
