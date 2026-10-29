import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Dashboard Demográfico - Censo IBGE",
    page_icon="🏙️",
    layout="wide"
)

caminho_ou_arquivo = Path(__file__).with_name(
    "CD2022_Populacao_2010_Compatibilizada_20231222.xlsx"
)


@st.cache_data
def carregar_e_limpar_dados(arquivo):
    bruto = pd.read_excel(arquivo, sheet_name="Municípios", header=2)
    df = bruto.dropna(subset=["NOME DO MUNICÍPIO"]).copy()
    df = df.rename(columns={
        "UF": "uf",
        "NOME DO MUNICÍPIO": "municipio",
        "População 2010 (Alterações de Limites até 2022)1": "pop_2010",
        "População Censo 2022": "pop_2022"
    })
    df["pop_2010"] = pd.to_numeric(df["pop_2010"], errors="coerce")
    df["pop_2022"] = pd.to_numeric(df["pop_2022"], errors="coerce")
    df["crescimento_pct"] = (
        (df["pop_2022"] / df["pop_2010"].where(df["pop_2010"] > 0) - 1) * 100
    ).round(2)
    return df


st.sidebar.title("Menu e Filtros")
file_upload = st.sidebar.file_uploader(
    "Carregar planilha do IBGE (Excel):", type=["xlsx"]
)

df = carregar_e_limpar_dados(
    file_upload if file_upload is not None else caminho_ou_arquivo
)

cid = ["Curitiba", "Porto Alegre", "Salvador", "Florianópolis", "Belo Horizonte"]
df_filtrado = df[df["municipio"].isin(cid)].copy()

st.title("Crescimento populacional das cidades")
st.caption("Comparação entre os Censos de 2010 e 2022 — IBGE")
st.dataframe(
    df_filtrado[["municipio", "uf", "pop_2010", "pop_2022", "crescimento_pct"]],
    hide_index=True
)

fig = px.bar(
    df_filtrado,
    x="municipio",
    y="crescimento_pct",
    color="municipio",
    text="crescimento_pct",
    labels={"municipio": "Cidade", "crescimento_pct": "Crescimento (%)"},
    title="Crescimento populacional acumulado de 2010 a 2022",
    hover_data=["pop_2010", "pop_2022"],
    category_orders={"municipio": cid}
)
fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)
