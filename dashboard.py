# Dashboard v15 com todas as funcionalidades validadas por Legacia
# Gerado automaticamente a partir da especificação completa


import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Arquivos esperados
COLAB_FILE = "Employees Forecast P&D(2025).csv"
LICENCA_FILE = "licencas.csv"

# Configuração da página
st.set_page_config(page_title="Painel de Custos P&D v15", layout="wide")
st.title("💼 Painel de Custos P&D - v15")

# Função para formatar valores como moeda brasileira
def formatar_moeda(valor):
    try:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

# Carregamento robusto com validações
@st.cache_data
def carregar_colaboradores():
    encodings = ["utf-8", "latin1", "cp1252"]
    for enc in encodings:
        try:
            df = pd.read_csv(COLAB_FILE, encoding=enc, encoding_errors="ignore")
            break
        except:
            continue
    else:
        st.error("❌ Erro ao carregar a planilha de colaboradores.")
        return pd.DataFrame()

    df.columns = df.columns.str.strip()

    colunas_obrigatorias = ["Name", "Total Cost (month)"]
    for col in colunas_obrigatorias:
        if col not in df.columns:
            st.warning(f"A coluna obrigatória '{col}' está ausente.")
            df[col] = "" if col == "Name" else 0.0

    for col in df.columns:
        if any(p in col.lower() for p in ["cost", "salary", "jul", "aug", "sep", "oct", "nov", "dec"]):
            df[col] = df[col].astype(str).str.replace("R\$", "", regex=True)                     .str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if "Tipo Contrato" not in df.columns:
        df["Tipo Contrato"] = "CLT"
    if "Total Cost (year)" not in df.columns:
        df["Total Cost (year)"] = df["Total Cost (month)"] * 12
    if "Position" not in df.columns:
        df["Position"] = ""
    return df

@st.cache_data
def carregar_licencas():
    if not os.path.exists(LICENCA_FILE):
        return pd.DataFrame(columns=["Nome", "Descrição", "Custo Mensal", "Categoria"])
    encodings = ["utf-8", "latin1", "cp1252"]
    for enc in encodings:
        try:
            df = pd.read_csv(LICENCA_FILE, encoding=enc, encoding_errors="ignore")
            break
        except:
            continue
    else:
        st.error("❌ Erro ao carregar a planilha de licenças.")
        return pd.DataFrame()

    if "Custo Mensal" not in df.columns:
        df["Custo Mensal"] = 0.0
    df["Custo Mensal"] = pd.to_numeric(df["Custo Mensal"], errors="coerce").fillna(0)
    return df

df_colab = carregar_colaboradores()
df_lic = carregar_licencas()

# ===== VISUALIZAÇÃO DE CUSTOS =====
st.markdown("## 💰 Visão Geral dos Custos")

# Filtros
with st.sidebar:
    st.header("🔍 Filtros")
    periodos_disponiveis = sorted([col for col in df_colab.columns if "/" in col])
    periodo_sel = st.multiselect("Períodos (incluindo ano)", periodos_disponiveis, default=periodos_disponiveis)
    cargos = sorted(df_colab["Position"].dropna().unique().tolist())
    cargo_sel = st.multiselect("Cargo", cargos, default=cargos)
    min_val, max_val = df_colab["Total Cost (month)"].min(), df_colab["Total Cost (month)"].max()
    val_range = st.slider("Faixa de valores (mensal)", min_value=float(min_val), max_value=float(max_val), value=(float(min_val), float(max_val)), step=500.0)

# Aplicar filtros
df_filtrado = df_colab[
    (df_colab["Position"].isin(cargo_sel)) &
    (df_colab["Total Cost (month)"] >= val_range[0]) &
    (df_colab["Total Cost (month)"] <= val_range[1])
]

# Totais
total_pessoas = df_filtrado["Total Cost (month)"].sum()
total_licencas = df_lic["Custo Mensal"].sum()
total_geral = total_pessoas + total_licencas

col1, col2, col3 = st.columns(3)
col1.metric("👥 Custo mensal com pessoas", formatar_moeda(total_pessoas))
col2.metric("🔧 Custo mensal com licenças", formatar_moeda(total_licencas))
col3.metric("📊 Custo mensal total", formatar_moeda(total_geral))

# Gráfico de colaboradores
df_graf = df_filtrado.sort_values("Name")
fig_colab = px.bar(
    df_graf,
    x="Name",
    y="Total Cost (month)",
    title="👥 Custo mensal por colaborador",
    labels={"Total Cost (month)": "Custo (R$)"},
    template="plotly_white"
)
fig_colab.update_layout(xaxis_title=None, yaxis_tickformat=".2f", margin=dict(t=40, b=40))

st.plotly_chart(fig_colab, use_container_width=True)

st.markdown("## ➕ Adicionar Novo Registro")

aba = st.radio("O que deseja adicionar?", ["Colaborador", "Licença/Ferramenta"])

if aba == "Colaborador":
    with st.form("form_colab"):
        nome = st.text_input("Nome")
        contrato = st.selectbox("Tipo de contrato", ["CLT", "PJ"])
        valor_mensal = st.number_input("Custo mensal (R$)", min_value=0.0, step=500.0, format="%.2f")
        valor_anual = valor_mensal * 12
        cargo = st.text_input("Cargo (Position)")
        periodo = st.selectbox("Período", periodos_disponiveis)
        enviar = st.form_submit_button("Adicionar")

        if enviar and nome:
            novo = pd.DataFrame([{
                "Name": nome,
                "Tipo Contrato": contrato,
                "Total Cost (month)": valor_mensal,
                "Total Cost (year)": valor_anual,
                "Position": cargo,
                periodo: valor_mensal
            }])
            df_colab = pd.concat([df_colab, novo], ignore_index=True)
            df_colab.to_csv(COLAB_FILE, index=False)
            st.success("✅ Colaborador adicionado com sucesso!")

else:
    with st.form("form_lic"):
        nome = st.text_input("Nome da Licença/Ferramenta")
        descricao = st.text_area("Descrição")
        categoria = st.text_input("Categoria (ex: Infra, Dev, Produto)")
        custo = st.number_input("Custo mensal (R$)", min_value=0.0, step=100.0, format="%.2f")
        enviar = st.form_submit_button("Adicionar")

        if enviar and nome:
            nova = pd.DataFrame([{
                "Nome": nome,
                "Descrição": descricao,
                "Categoria": categoria,
                "Custo Mensal": custo
            }])
            df_lic = pd.concat([df_lic, nova], ignore_index=True)
            df_lic.to_csv(LICENCA_FILE, index=False)
            st.success("✅ Licença adicionada com sucesso!")

st.markdown("## ✏️ Editar ou Remover Registros Existentes")

aba_edicao = st.radio("Qual tabela deseja editar?", ["Colaboradores", "Licenças"])

if aba_edicao == "Colaboradores":
    st.subheader("👥 Colaboradores")
    df_editado = df_colab.copy().sort_values("Name").reset_index(drop=True)
    for i in df_editado.index:
        with st.expander(f"{df_editado.at[i, 'Name']}"):
            df_editado.at[i, "Tipo Contrato"] = st.selectbox(f"Tipo Contrato #{i}", ["CLT", "PJ"], index=0 if df_editado.at[i, "Tipo Contrato"]=="CLT" else 1, key=f"contrato_{i}")
            df_editado.at[i, "Total Cost (month)"] = st.number_input(f"Custo mensal #{i}", value=float(df_editado.at[i, "Total Cost (month)"]), step=500.0, key=f"mes_{i}")
            df_editado.at[i, "Total Cost (year)"] = st.number_input(f"Total anual #{i}", value=float(df_editado.at[i, "Total Cost (year)"]), step=1000.0, key=f"ano_{i}")
            if st.button(f"💾 Salvar #{i}", key=f"salvar_{i}"):
                df_colab.update(df_editado)
                df_colab.to_csv(COLAB_FILE, index=False)
                st.success("✅ Alterações salvas")
            if st.button(f"🗑️ Remover #{i}", key=f"remover_{i}"):
                df_colab.drop(i, inplace=True)
                df_colab.to_csv(COLAB_FILE, index=False)
                st.warning("❌ Colaborador removido")

elif aba_edicao == "Licenças":
    st.subheader("🔧 Licenças e Ferramentas")
    df_editado = df_lic.copy().reset_index(drop=True)
    for i in df_editado.index:
        with st.expander(f"{df_editado.at[i, 'Nome']}"):
            df_editado.at[i, "Custo Mensal"] = st.number_input(f"Custo mensal #{i}", value=float(df_editado.at[i, "Custo Mensal"]), step=100.0, key=f"lic_mensal_{i}")
            if st.button(f"💾 Salvar #{i}", key=f"lic_salvar_{i}"):
                df_lic.update(df_editado)
                df_lic.to_csv(LICENCA_FILE, index=False)
                st.success("✅ Licença atualizada")
            if st.button(f"🗑️ Remover #{i}", key=f"lic_remover_{i}"):
                df_lic.drop(i, inplace=True)
                df_lic.to_csv(LICENCA_FILE, index=False)
                st.warning("❌ Licença removida")

st.markdown("## 📤 Exportar Dados")

def exportar_csv_formatado(df, tipo):
    df_export = df.copy()
    for col in df_export.select_dtypes(include="number").columns:
        df_export[col] = df_export[col].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    csv = df_export.to_csv(index=False).encode("utf-8")
    st.download_button(f"📥 Baixar {tipo}", csv, file_name=f"{tipo.lower()}_exportado.csv", mime="text/csv")

col1, col2 = st.columns(2)
with col1:
    exportar_csv_formatado(df_colab, "Colaboradores")
with col2:
    exportar_csv_formatado(df_lic, "Licencas")

# ========== SEGURANÇA E UX ==========
try:
    if df_colab.empty:
        st.warning("⚠️ A planilha de colaboradores está vazia.")
except Exception as e:
    st.error(f"Erro ao carregar colaboradores: {e}")

try:
    if df_lic.empty:
        st.warning("⚠️ A planilha de licenças está vazia.")
except Exception as e:
    st.error(f"Erro ao carregar licenças: {e}")
