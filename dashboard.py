
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

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

df_original = carregar_dados()
df = df_original.copy()

# Adição de colaborador
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

# Edição de colaborador
with st.expander("✏️ Editar colaborador existente"):
    selecionado = st.selectbox("Escolha quem editar", df["Name"].unique())
    dados = df[df["Name"] == selecionado].iloc[0]
    novo_cargo = st.text_input("Cargo", value=dados["Position"])
    novo_tipo = st.selectbox("Tipo", ["CLT", "PJ"], index=0 if dados["Hiring"] == "CLT" else 1)
    novo_salario = st.number_input("Salário mensal", value=float(dados["Salary (month)"]))
    if st.button("Salvar edição"):
        idx = df[df["Name"] == selecionado].index[0]
        novo_total = novo_salario * (2.8 if novo_tipo == "CLT" else 1.0)
        df.loc[idx, ["Position", "Hiring", "Salary (month)", "Total Cost (month)",
                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]] = [
            novo_cargo, novo_tipo, novo_salario, novo_total,
            novo_total, novo_total, novo_total, novo_total, novo_total, novo_total
        ]
        df.loc[idx, "Total Cost CLT (6 months)"] = novo_total * 6
        df.loc[idx, "Total Cost CLT (12 months)"] = novo_total * 12
        st.success(f"{selecionado} atualizado com sucesso.")

# Remoção de colaborador
with st.expander("🗑️ Remover colaborador"):
    excluir = st.selectbox("Escolha quem remover", df["Name"].unique())
    if st.button("Remover"):
        df = df[df["Name"] != excluir]
        st.success(f"{excluir} removido com sucesso.")

# Filtros
st.sidebar.header("Filtros")
cargo_filtro = st.sidebar.multiselect("Cargo", df["Position"].unique(), default=df["Position"].unique())
min_valor, max_valor = st.sidebar.slider("Custo mensal", 0.0, float(df["Total Cost (month)"].max()), (0.0, float(df["Total Cost (month)"].max())))
periodos = st.sidebar.multiselect("Períodos", ["Jul/2025", "Aug/2025", "Sep/2025", "Oct/2025", "Nov/2025", "Dec/2025"], default=["Jul/2025", "Aug/2025", "Sep/2025", "Oct/2025", "Nov/2025", "Dec/2025"])

df_filtrado = df[
    (df["Position"].isin(cargo_filtro)) &
    (df["Total Cost (month)"] >= min_valor) &
    (df["Total Cost (month)"] <= max_valor)
]

# Métricas
st.metric("Custo Total Mensal (R$)", f"{df_filtrado['Total Cost (month)'].sum():,.2f}")
st.metric("Custo Total 6 meses (R$)", f"{df_filtrado['Total Cost CLT (6 months)'].sum():,.2f}")
st.metric("Custo Total 12 meses (R$)", f"{df_filtrado['Total Cost CLT (12 months)'].sum():,.2f}")

# Gráficos
fig1 = px.bar(df_filtrado, x="Name", y="Total Cost (month)", title="Custo mensal por colaborador", color="Position")
st.plotly_chart(fig1)

df_mensal = df_filtrado[["Name", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]].copy()
df_mensal.columns = ["Name", "Jul/2025", "Aug/2025", "Sep/2025", "Oct/2025", "Nov/2025", "Dec/2025"]
df_mensal = df_mensal[["Name"] + periodos].set_index("Name").T
df_mensal_total = df_mensal.sum(axis=1).reset_index()
df_mensal_total.columns = ["Mês", "Custo Total"]
fig2 = px.line(df_mensal_total, x="Mês", y="Custo Total", markers=True, title="Custo total do time (por período)")
st.plotly_chart(fig2)

# Exportar planilha
def gerar_download(df):
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer

st.download_button("📥 Exportar planilha atualizada", data=gerar_download(df), file_name="custos_atualizados.csv", mime="text/csv")
