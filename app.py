import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================
# CARGA DE DATOS
# ==========================
@st.cache_data
def load_data():
    df = pd.read_csv("Desempeño 2024.csv", sep=";")
    return df

df = load_data()
df.columns = df.columns.str.strip()

# ==========================
# FILTROS GENERALES
# ==========================
st.sidebar.header("Filtros")

direcciones = ["Todas"] + sorted(df["Dirección"].dropna().unique().tolist())
direccion = st.sidebar.selectbox("Dirección", direcciones)

areas = ["Todas"] + sorted(df["Área"].dropna().unique().tolist())
area = st.sidebar.selectbox("Área", areas)

subareas = ["Todas"] + sorted(df["Sub-área"].dropna().unique().tolist())
subarea = st.sidebar.selectbox("Sub-área", subareas)

df_filtrado = df.copy()

if direccion != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Dirección"] == direccion]
if area != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Área"] == area]
if subarea != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Sub-área"] == subarea]

# ==========================
# SECCIÓN 1: RESULTADOS 2024
# ==========================
st.header("📌 Resultados 2024")

df_2024 = df_filtrado[df_filtrado["Año"] == 2024]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Evaluaciones totales", len(df_2024))
with col2:
    st.metric("Feedback recibido", len(df_2024[df_2024["Estado feedback"] == "Recibido"]))
with col3:
    st.metric("Feedback no recibido", len(df_2024[df_2024["Estado feedback"] == "No Recibido"]))

# Distribución de notas
st.subheader("Distribución de notas 2024")
fig_notas = px.histogram(df_2024, x="Nota", nbins=5, title="Distribución de desempeño 2024")
st.plotly_chart(fig_notas, use_container_width=True)

# ==========================
# SECCIÓN 2: LIDERAZGO
# ==========================
st.header("📌 Liderazgo")

# Ranking de líderes por promedio
if "Líder" in df_2024.columns:
    ranking_lideres = (
        df_2024.groupby("Líder")
        .agg(Promedio=("Nota","mean"), Evaluados=("Colaborador","count"))
        .reset_index()
        .sort_values(by="Promedio", ascending=False)
    )

    st.subheader("Ranking de líderes por promedio")
    st.dataframe(ranking_lideres)

    fig_lideres = px.bar(ranking_lideres, x="Líder", y="Promedio", color="Promedio",
                        title="Promedio de desempeño por líder", text_auto=".2f")
    st.plotly_chart(fig_lideres, use_container_width=True)
else:
    st.warning("⚠️ No se encontró la columna 'Líder' en el dataset.")

# ==========================
# SECCIÓN 3: HISTORIA DE LA EVALUACIÓN
# ==========================
st.header("📌 Historia de la Evaluación de Desempeño (2022-2024)")

historico = (
    df_filtrado.groupby("Año")
    .agg(Promedio=("Nota","mean"), Evaluaciones=("Colaborador","count"))
    .reset_index()
    .sort_values(by="Año")
)

col1, col2 = st.columns(2)
with col1:
    for year in [2022, 2023, 2024]:
        if year in historico["Año"].values:
            promedio = round(historico.loc[historico["Año"]==year,"Promedio"].values[0],2)
            st.metric(f"Promedio {year}", promedio)
        else:
            st.metric(f"Promedio {year}", "N/D")

with col2:
    fig_hist = px.line(historico, x="Año", y="Promedio", markers=True,
                       title="Tendencia histórica del desempeño")
    st.plotly_chart(fig_hist, use_container_width=True)

# Mostrar detalle tabla histórica
st.subheader("Detalle histórico")
st.dataframe(historico)
