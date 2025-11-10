
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Painel de Consultas Médicas", layout="wide")

st.markdown("<h1 style='margin-bottom:0.25rem'>Painel de Consultas Medicas</h1>", unsafe_allow_html=True)

CSV_PATH = "consultas.csv"
df = pd.read_csv(CSV_PATH)

# --- Ajuste de nomes conforme o CSV enviado ---
DATE_COL = "dataconsulta"
UNIT_COL = "unidade"
SPEC_COL = "tipoconsulta"
VALUE_COL = "valor"   # habilita faturamento

# Tipagens
df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")

# Sidebar
st.sidebar.header("Filtros")
datas_unicas = sorted(df[DATE_COL].dropna().dt.strftime("%d-%m-%Y").unique().tolist())
opcao_data = st.sidebar.selectbox("Selecione a data:", ["Todas"] + datas_unicas, index=0)

unidades = sorted(df[UNIT_COL].dropna().unique().tolist())
opcao_unidade = st.sidebar.selectbox("Selecione uma unidade :", ["Todas"] + unidades, index=0)

# Filtros
df_filtrado = df.copy()
if opcao_data != "Todas":
    df_filtrado = df_filtrado.loc[df_filtrado[DATE_COL].dt.strftime("%d-%m-%Y") == opcao_data]
if opcao_unidade != "Todas":
    df_filtrado = df_filtrado.loc[df_filtrado[UNIT_COL] == opcao_unidade]

# --- Três colunas para os três gráficos ---
c1, c2, c3 = st.columns(3)

# Gráfico 1: Número de Consultas por Unidades
g1 = (
    df_filtrado
    .groupby(UNIT_COL, dropna=False)
    .size()
    .reset_index(name="Total")
    .sort_values("Total", ascending=False)
)
fig1 = px.bar(
    g1, x=UNIT_COL, y="Total", text="Total", color=UNIT_COL,
    title=f"Numero de Consultas por Unidades ({opcao_data})"
)
fig1.update_traces(textposition="outside")
fig1.update_layout(xaxis_title="", yaxis_title="Total de Consultas", height=420, margin=dict(l=10, r=10, t=60, b=10), showlegend=False)
c1.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Donut - Consultas por Especialidade (percentual)
g2 = (
    df_filtrado
    .groupby(SPEC_COL, dropna=False)
    .size()
    .reset_index(name="Total")
    .sort_values("Total", ascending=False)
)
fig2 = px.pie(
    g2, values="Total", names=SPEC_COL,
    hole=0.55, title="Consultas por Especialidade"
)
fig2.update_traces(textposition="inside", textinfo="percent", hovertemplate="%{label}<br>Total=%{value}")
fig2.update_layout(height=420, margin=dict(l=10, r=10, t=60, b=10))
c2.plotly_chart(fig2, use_container_width=True)

# Gráfico 3: Faturamento Total por Unidade (barras)
g3 = (
    df_filtrado
    .groupby(UNIT_COL, dropna=False)[VALUE_COL]
    .sum()
    .reset_index(name="Faturamento")
    .sort_values("Faturamento", ascending=False)
)
fig3 = px.bar(
    g3, x=UNIT_COL, y="Faturamento", text="Faturamento", color=UNIT_COL,
    title="💰 Faturamento Total por Unidade"
)
fig3.update_traces(texttemplate="%{text:.0f}", textposition="outside")
fig3.update_layout(yaxis_title="Faturamento (R$)", xaxis_title="", height=420, margin=dict(l=10, r=10, t=60, b=10), showlegend=False)
c3.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.subheader(f"📋 Registros — {opcao_unidade if opcao_unidade!='Todas' else 'todas as unidades'}")
st.dataframe(df_filtrado, use_container_width=True)
