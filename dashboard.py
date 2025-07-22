
import streamlit as st
import pandas as pd
import plotly.express as px
import os

COLAB_FILE = "Employees Forecast P&D(2025).csv"
LICENCA_FILE = "licencas.csv"

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

@st.cache_data
def carregar_colaboradores():
    if not os.path.exists(COLAB_FILE):
        return pd.DataFrame()
    df = pd.read_csv(COLAB_FILE, encoding="utf-8", encoding_errors="ignore")
    df.columns = df.columns.str.strip()
    for col in df.columns:
        if any(p in col.lower() for p in ["cost", "salary", "jul", "aug", "sep", "oct", "nov", "dec"]):
            df[col] = df[col].astype(str).str.replace("R\$", "", regex=True).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

@st.cache_data
def carregar_licencas():
    if not os.path.exists(LICENCA_FILE):
        return pd.DataFrame(columns=["Nome", "Descrição", "Custo Mensal", "Categoria"])
    df = pd.read_csv(LICENCA_FILE, encoding="utf-8", encoding_errors="ignore")
    df["Custo Mensal"] = pd.to_numeric(df["Custo Mensal"], errors="coerce").fillna(0)
    return df

def salvar_colaboradores(df):
    df.to_csv(COLAB_FILE, index=False)

# Layout
st.set_page_config(page_title="Painel de Custos P&D v14", layout="wide")
st.title("💰 Painel de Custos P&D v14")

df_colab = carregar_colaboradores()
df_lic = carregar_licencas()

# Edição e remoção
st.subheader("✏️ Editar ou Remover Colaboradores")
if df_colab.empty:
    st.warning("Nenhum colaborador encontrado.")
else:
    df_editado = df_colab.copy()
    if "Tipo Contrato" not in df_editado.columns:
        df_editado["Tipo Contrato"] = "CLT"
    if "Total Cost (year)" not in df_editado.columns:
        df_editado["Total Cost (year)"] = 0.0
    for i in df_editado.index:
        with st.expander(f"👤 {df_editado.at[i, 'Name']}"):
            df_editado.at[i, "Name"] = st.text_input(f"Nome #{i}", df_editado.at[i, "Name"], key=f"nome_{i}")
            df_editado.at[i, "Position"] = st.text_input(f"Cargo #{i}", df_editado.at[i, "Position"], key=f"cargo_{i}")
            df_editado.at[i, "Tipo Contrato"] = st.selectbox(f"Tipo Contrato #{i}", ["CLT", "PJ"], index=0 if df_editado.at[i, "Tipo Contrato"]=="CLT" else 1, key=f"contrato_{i}")
            df_editado.at[i, "Total Cost (month)"] = st.number_input(f"Total mensal #{i}", value=float(df_editado.at[i, "Total Cost (month)"]), step=500.0, key=f"mes_{i}")
            df_editado.at[i, "Total Cost (year)"] = st.number_input(f"Total anual #{i}", value=float(df_editado.at[i, "Total Cost (year)"]), step=1000.0, key=f"ano_{i}")
            if st.button(f"🗑️ Remover {df_editado.at[i, 'Name']}", key=f"del_{i}"):
                df_editado.drop(i, inplace=True)
                st.success(f"{df_colab.at[i, 'Name']} removido. Clique em Salvar alterações.")
    if st.button("💾 Salvar alterações"):
        salvar_colaboradores(df_editado.reset_index(drop=True))
        st.success("Alterações salvas com sucesso. Recarregue a página.")
