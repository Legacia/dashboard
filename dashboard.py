
import streamlit as st
import pandas as pd
import plotly.express as px
import os

COLAB_FILE = "Employees Forecast P&D(2025).csv"
LICENCA_FILE = "licencas.csv"

@st.cache_data
def carregar_colaboradores():
    if not os.path.exists(COLAB_FILE):
        return pd.DataFrame()
    df = pd.read_csv(COLAB_FILE, encoding="utf-8", encoding_errors="ignore")
    df.columns = df.columns.str.strip()

    # Verificação de coluna obrigatória
    if "Total Cost (month)" not in df.columns:
        st.warning("A planilha de colaboradores está sem a coluna 'Total Cost (month)'. Verifique o arquivo.")
        return pd.DataFrame()

    # Conversão segura de colunas financeiras
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
        st.warning("A planilha de licenças está sem a coluna 'Custo Mensal'. Verifique o arquivo.")
        return pd.DataFrame()
    df["Custo Mensal"] = pd.to_numeric(df["Custo Mensal"], errors="coerce").fillna(0)
    return df

st.title("💰 Painel de Custos P&D: Pessoas + Licenças")

df_colab = carregar_colaboradores()
df_lic = carregar_licencas()

# Formulário para adicionar licenças
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

# Alternância de visualização
modo = st.radio("Visualizar:", ["👥 Apenas Pessoas", "🔧 Apenas Licenças", "📊 Todos os Custos"])

if modo in ["👥 Apenas Pessoas", "📊 Todos os Custos"] and not df_colab.empty:
    df_colab = df_colab.sort_values("Name")
    total_pessoas = df_colab["Total Cost (month)"].sum()
    if pd.notna(total_pessoas) and total_pessoas > 0:
        valor_formatado = f"{total_pessoas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        st.subheader(f"👥 Custo mensal com pessoas: R$ {valor_formatado}")
        fig1 = px.bar(df_colab, x="Name", y="Total Cost (month)", color="Position", title="Custo por colaborador")
        st.plotly_chart(fig1)
    else:
        st.warning("Custo mensal com pessoas não disponível.")

if modo in ["🔧 Apenas Licenças", "📊 Todos os Custos"] and not df_lic.empty:
    total_lic = df_lic["Custo Mensal"].sum()
    valor_formatado_lic = f"{total_lic:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.subheader(f"🔧 Custo mensal com licenças: R$ {valor_formatado_lic}")
    fig2 = px.bar(df_lic, x="Nome", y="Custo Mensal", color="Categoria", title="Custo por ferramenta")
    st.plotly_chart(fig2)

if modo == "📊 Todos os Custos" and not df_colab.empty and not df_lic.empty:
    total_geral = df_colab["Total Cost (month)"].sum() + df_lic["Custo Mensal"].sum()
    valor_formatado_total = f"{total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.success(f"💵 **Custo Total Mensal: R$ {valor_formatado_total}**")
