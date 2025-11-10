
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Painel de Consultas Médicas — Styled", layout="wide", page_icon="🩺")

st.markdown(
    """
    <style>
      .stApp { background: #0b1220; color: #e5e7eb; }
      h1, h2, h3 { color: #e5e7eb !important; }
      .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
      .kpi {
        border-radius: 16px;
        padding: 18px 20px;
        background: radial-gradient(1000px 400px at top left, rgba(56,189,248,0.08), rgba(0,0,0,0)) , #0f172a;
        border: 1px solid rgba(148,163,184,0.25);
        box-shadow: 0 0 0 1px rgba(2,6,23,0.4) inset, 0 10px 30px rgba(0,0,0,0.35);
      }
      .kpi .label { font-size: 0.95rem; color: #cbd5e1; }
      .kpi .value { font-size: 2.0rem; font-weight: 800; letter-spacing: 0.5px; color: #22d3ee; }
      .section-title {
        display:flex; align-items:center; gap:10px; margin: 0.25rem 0 0.75rem;
        color: #86efac; font-weight: 700; font-size: 1.05rem;
      }
      .divider { height: 1px; width: 100%; background: linear-gradient(90deg, rgba(148,163,184,0.15), rgba(148,163,184,0.05)); margin: 0.75rem 0 1rem; }
      section[data-testid="stSidebar"] { background: #0f172a; border-right: 1px solid rgba(148,163,184,0.15); }
      label, .stSelectbox label { color: #e5e7eb !important; }
    </style>
    """,
    unsafe_allow_html=True
)

CSV_PATH = "consultas.csv"
df = pd.read_csv(CSV_PATH)

DATE_COL = "dataconsulta"
UNIT_COL = "unidade"
SPEC_COL = "tipoconsulta"
VALUE_COL = "valor"

df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")

st.sidebar.header("Filtros")
datas_unicas = sorted(df[DATE_COL].dropna().dt.strftime("%d-%m-%Y").unique().tolist())
opcao_data = st.sidebar.selectbox("Selecione a data:", ["Todas"] + datas_unicas, index=0)
unidades = sorted(df[UNIT_COL].dropna().unique().tolist())
opcao_unidade = st.sidebar.selectbox("Selecione uma unidade :", ["Todas"] + unidades, index=0)

df_filtrado = df.copy()
if opcao_data != "Todas":
    df_filtrado = df_filtrado.loc[df_filtrado[DATE_COL].dt.strftime("%d-%m-%Y") == opcao_data]
if opcao_unidade != "Todas":
    df_filtrado = df_filtrado.loc[df_filtrado[UNIT_COL] == opcao_unidade]

st.markdown("<h1>🩺 Painel de Consultas Médicas</h1>", unsafe_allow_html=True)

total_consultas = int(len(df_filtrado))
unidades_ativas = int(df_filtrado[UNIT_COL].nunique())
faturamento_total = float(df_filtrado[VALUE_COL].sum())

k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(f"<div class='kpi'><div class='label'>Total de Consultas</div><div class='value'>{total_consultas}</div></div>", unsafe_allow_html=True)
with k2:
    st.markdown(f"<div class='kpi'><div class='label'>Unidades Ativas</div><div class='value'>{unidades_ativas}</div></div>", unsafe_allow_html=True)
with k3:
    st.markdown(f"<div class='kpi'><div class='label'>Faturamento Total</div><div class='value'>R$ {faturamento_total:,.2f}</div></div>", unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

g1 = (
    df_filtrado
    .groupby(UNIT_COL, dropna=False)
    .size()
    .reset_index(name="Total")
    .sort_values("Total", ascending=False)
)
fig1 = px.bar(g1, x=UNIT_COL, y="Total", text="Total", color=UNIT_COL, title="Consultas por Unidade")
fig1.update_traces(textposition="outside")
fig1.update_layout(template="plotly_dark", height=420, margin=dict(l=10, r=10, t=60, b=10), xaxis_title="Unidade", yaxis_title="Total de Consultas", showlegend=False)
with c1:
    st.markdown("<div class='section-title'>✅ Consultas por Unidade</div>", unsafe_allow_html=True)
    st.plotly_chart(fig1, use_container_width=True)

g2 = (
    df_filtrado
    .groupby(SPEC_COL, dropna=False)
    .size()
    .reset_index(name="Total")
    .sort_values("Total", ascending=False)
)
fig2 = px.pie(g2, values="Total", names=SPEC_COL, hole=0.55, title="Consultas por Especialidade")
fig2.update_traces(textposition="inside", textinfo="percent", hovertemplate="%{label}<br>Total=%{value}")
fig2.update_layout(template="plotly_dark", height=420, margin=dict(l=10, r=10, t=60, b=10))
with c2:
    st.markdown("<div class='section-title'>🩺 Consultas por Especialidade</div>", unsafe_allow_html=True)
    st.plotly_chart(fig2, use_container_width=True)

g3 = (
    df_filtrado
    .groupby(UNIT_COL, dropna=False)[VALUE_COL]
    .sum()
    .reset_index(name="Faturamento")
    .sort_values("Faturamento", ascending=False)
)
fig3 = px.bar(g3, x=UNIT_COL, y="Faturamento", text="Faturamento", color=UNIT_COL, title="Faturamento Total por Unidade")
fig3.update_traces(texttemplate="%{text:.0f}", textposition="outside")
fig3.update_layout(template="plotly_dark", height=420, margin=dict(l=10, r=10, t=60, b=10), xaxis_title="Unidade", yaxis_title="Faturamento (R$)", showlegend=False)
with c3:
    st.markdown("<div class='section-title'>💰 Faturamento Total por Unidade</div>", unsafe_allow_html=True)
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.subheader(f"📋 Registros — {'todas as unidades' if opcao_unidade=='Todas' else opcao_unidade}")
st.dataframe(df_filtrado, use_container_width=True)
