
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from io import StringIO

# Arquivos de entrada e saída
COLAB_FILE = "Employees Forecast P&D(2025).csv"
LICENCA_FILE = "licencas.csv"

# Utilitários
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

@st.cache_data
def carregar_colaboradores():
    if not os.path.exists(COLAB_FILE):
        return pd.DataFrame()
    df = pd.read_csv(COLAB_FILE, encoding="utf-8", encoding_errors="ignore")
    df.columns = df.columns.str.strip()
    if "Total Cost (month)" not in df.columns:
        st.warning("A planilha de colaboradores está sem a coluna 'Total Cost (month)'.")
        return pd.DataFrame()
    for col in df.columns:
        if any(palavra in col.lower() for palavra in ["cost", "salary", "jul", "aug", "sep", "oct", "nov", "dec"]):
            df[col] = df[col].astype(str).str.replace("R\$", "", regex=True).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

@st.cache_data
def carregar_licencas():
    if not os.path.exists(LICENCA_FILE):
        return pd.DataFrame(columns=["Nome", "Descrição", "Custo Mensal", "Categoria"])
    df = pd.read_csv(LICENCA_FILE, encoding="utf-8", encoding_errors="ignore")
    if "Custo Mensal" not in df.columns:
        st.warning("A planilha de licenças está sem a coluna 'Custo Mensal'.")
        return pd.DataFrame()
    df["Custo Mensal"] = pd.to_numeric(df["Custo Mensal"], errors="coerce").fillna(0)
    return df

# Título
st.set_page_config(page_title="Painel de Custos P&D", layout="wide")
st.title("💰 Painel de Custos P&D: Pessoas + Licenças")

# Carregamento inicial
df_colab = carregar_colaboradores()
df_lic = carregar_licencas()

# Filtros
with st.sidebar:
    st.header("🔍 Filtros")
    if not df_colab.empty:
        cargos = sorted(df_colab["Position"].dropna().unique())
        filtro_cargo = st.multiselect("Filtrar por cargo", cargos, default=cargos)
        valores = st.slider("Faixa de custo mensal (R$)", 
                            min_value=0, 
                            max_value=int(df_colab["Total Cost (month)"].max()) if not df_colab.empty else 10000,
                            value=(0, int(df_colab["Total Cost (month)"].max()) if not df_colab.empty else 10000),
                            step=500)
        periodos = sorted([col for col in df_colab.columns if "/" in col])
        filtro_periodo = st.multiselect("Período (com ano)", periodos, default=periodos)

modo = st.radio("🔄 Visualizar:", ["👥 Apenas Pessoas", "🔧 Apenas Licenças", "📊 Todos os Custos"])

# Filtro e visualização de colaboradores
if modo in ["👥 Apenas Pessoas", "📊 Todos os Custos"] and not df_colab.empty:
    df_filtrado = df_colab.copy()
    if "Position" in df_colab.columns:
        df_filtrado = df_filtrado[df_filtrado["Position"].isin(filtro_cargo)]
    df_filtrado = df_filtrado[df_filtrado["Total Cost (month)"].between(valores[0], valores[1])]
    df_filtrado = df_filtrado.sort_values("Name")
    total_pessoas = df_filtrado["Total Cost (month)"].sum()
    st.subheader(f"👥 Custo mensal com pessoas: {formatar_moeda(total_pessoas)}")
    fig1 = px.bar(df_filtrado, x="Name", y="Total Cost (month)", color="Position", title="Custo por colaborador")
    st.plotly_chart(fig1, use_container_width=True)
    st.dataframe(df_filtrado)

# Visualização de licenças
if modo in ["🔧 Apenas Licenças", "📊 Todos os Custos"] and not df_lic.empty:
    total_lic = df_lic["Custo Mensal"].sum()
    st.subheader(f"🔧 Custo mensal com licenças: {formatar_moeda(total_lic)}")
    fig2 = px.bar(df_lic, x="Nome", y="Custo Mensal", color="Categoria", title="Custo por ferramenta")
    st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(df_lic)

# Custo total
if modo == "📊 Todos os Custos" and not df_colab.empty and not df_lic.empty:
    total_geral = df_filtrado["Total Cost (month)"].sum() + df_lic["Custo Mensal"].sum()
    st.success(f"💵 **Custo Total Mensal: {formatar_moeda(total_geral)}**")

# Exportação
st.markdown("---")
st.download_button("📥 Exportar colaboradores (.csv)", data=df_colab.to_csv(index=False).encode("utf-8"), file_name="colaboradores.csv")
st.download_button("📥 Exportar licenças (.csv)", data=df_lic.to_csv(index=False).encode("utf-8"), file_name="licencas.csv")

# Formulários
st.markdown("---")
with st.expander("➕ Adicionar colaborador"):
    nome = st.text_input("Nome")
    cargo = st.text_input("Cargo")
    contrato = st.selectbox("Tipo de contrato", ["CLT", "PJ"])
    custo_mensal = st.number_input("Valor mensal (R$)", step=500.0)
    custo_anual = st.number_input("Valor anual (R$)", step=5000.0)
    if st.button("Adicionar colaborador"):
        novo = pd.DataFrame([{
            "Name": nome,
            "Position": cargo,
            "Tipo Contrato": contrato,
            "Total Cost (month)": custo_mensal,
            "Total Cost (year)": custo_anual
        }])
        novo.to_csv(COLAB_FILE, mode='a', index=False, header=not os.path.exists(COLAB_FILE))
        st.success("Colaborador adicionado com sucesso. Recarregue a página.")

with st.expander("➕ Adicionar licença/ferramenta"):
    lic_nome = st.text_input("Nome da ferramenta")
    lic_desc = st.text_input("Descrição")
    lic_categoria = st.text_input("Categoria")
    lic_valor = st.number_input("Custo mensal (R$)", step=100.0)
    if st.button("Adicionar ferramenta"):
        nova_lic = pd.DataFrame([{
            "Nome": lic_nome,
            "Descrição": lic_desc,
            "Categoria": lic_categoria,
            "Custo Mensal": lic_valor
        }])
        nova_lic.to_csv(LICENCA_FILE, mode='a', index=False, header=not os.path.exists(LICENCA_FILE))
        st.success("Licença adicionada com sucesso. Recarregue a página.")
