
import streamlit as st
import pandas as pd
import plotly.express as px
import os

CAMINHO_COLAB = "Employees Forecast P&D(2025).csv"
CAMINHO_LICENCAS = "licencas.csv"

@st.cache_data
def carregar_colaboradores():
    try:
        df = pd.read_csv(CAMINHO_COLAB, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(CAMINHO_COLAB, encoding="latin1")
    df.columns = df.columns.str.strip()
    colunas_necessarias = ["Nome", "Total Cost (month)", "Total Cost (year)", "Tipo Contrato", "Position"]
    for col in colunas_necessarias:
        if col not in df.columns:
            st.error(f"A coluna obrigatória '{col}' não está presente na planilha.")
            st.stop()
    df["Nome"] = df["Nome"].astype(str)
    df["Total Cost (month)"] = df["Total Cost (month)"].astype(str).str.replace("R\$", "").str.replace(".", "").str.replace(",", ".").astype(float)
    df["Total Cost (year)"] = df["Total Cost (year)"].astype(str).str.replace("R\$", "").str.replace(".", "").str.replace(",", ".").astype(float)
    df["Tipo Contrato"] = df["Tipo Contrato"].fillna("CLT")
    return df

@st.cache_data
def carregar_licencas():
    if not os.path.exists(CAMINHO_LICENCAS):
        return pd.DataFrame(columns=["Nome", "Descrição", "Categoria", "Custo Mensal"])
    try:
        df = pd.read_csv(CAMINHO_LICENCAS, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(CAMINHO_LICENCAS, encoding="latin1")
    df.columns = df.columns.str.strip()
    if "Custo Mensal" not in df.columns:
        st.error("A coluna 'Custo Mensal' é obrigatória no arquivo de licenças.")
        st.stop()
    df["Custo Mensal"] = df["Custo Mensal"].astype(str).str.replace("R\$", "").str.replace(".", "").str.replace(",", ".").astype(float)
    return df

df_colab = carregar_colaboradores()
df_lic = carregar_licencas()

st.title("💼 Painel de Custos da Equipe e Licenças")

# Filtros
st.sidebar.header("Filtros")
periodos = sorted(df_colab["Período"].dropna().unique())
periodo_selecionado = st.sidebar.selectbox("Selecione o período", options=["Todos"] + list(periodos))
cargos = sorted(df_colab["Position"].dropna().unique())
cargo_selecionado = st.sidebar.selectbox("Selecione o cargo", options=["Todos"] + list(cargos))
valor_min, valor_max = st.sidebar.slider("Faixa de custo mensal (R$)", 0, int(df_colab["Total Cost (month)"].max()), (0, int(df_colab["Total Cost (month)"].max())))

df_filtrado = df_colab.copy()
if periodo_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Período"] == periodo_selecionado]
if cargo_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Position"] == cargo_selecionado]
df_filtrado = df_filtrado[(df_filtrado["Total Cost (month)"] >= valor_min) & (df_filtrado["Total Cost (month)"] <= valor_max)]

# Totalizadores
total_pessoas = df_filtrado["Total Cost (month)"].sum()
total_licencas = df_lic["Custo Mensal"].sum()
total_geral = total_pessoas + total_licencas

st.subheader(f"👥 Custo mensal com pessoas: R$ {total_pessoas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
st.subheader(f"🔧 Custo mensal com licenças: R$ {total_licencas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
st.subheader(f"📊 Custo mensal total: R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

# Gráfico
fig = px.bar(df_filtrado.sort_values("Nome"), x="Nome", y="Total Cost (month)", title="Custo mensal por colaborador")
fig.update_layout(xaxis_title="Colaborador", yaxis_title="Custo (R$)", xaxis_tickangle=-45)
st.plotly_chart(fig, use_container_width=True)

# Tabela e exportação
st.markdown("### 📋 Tabela de Colaboradores")
df_export = df_filtrado.sort_values("Nome")
df_export["Total Cost (month)"] = df_export["Total Cost (month)"].map(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
df_export["Total Cost (year)"] = df_export["Total Cost (year)"].map(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
st.dataframe(df_export, use_container_width=True)
st.download_button("📥 Exportar colaboradores filtrados", data=df_export.to_csv(index=False), file_name="colaboradores_filtrados.csv", mime="text/csv")

st.markdown("### 🛠️ Tabela de Licenças")
df_lic_export = df_lic.copy()
df_lic_export["Custo Mensal"] = df_lic_export["Custo Mensal"].map(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
st.dataframe(df_lic_export, use_container_width=True)
st.download_button("📥 Exportar licenças", data=df_lic_export.to_csv(index=False), file_name="licencas.csv", mime="text/csv")
