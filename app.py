import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard Desempeño Piton", page_icon="📊", layout="wide")
st.title("📊 Reporte de Desempeño - Piton")

# ============================
# Carga de datos
# ============================
st.sidebar.header("⚙️ Configuración de datos")
archivo_subido = st.sidebar.file_uploader("Sube tu archivo CSV (separador ;)", type=["csv"])
ARCHIVO_REPO = "Desempeño-Piton.csv"

try:
    if archivo_subido is not None:
        df = pd.read_csv(archivo_subido, sep=";", encoding="utf-8", engine="python")
    else:
        df = pd.read_csv(ARCHIVO_REPO, sep=";", encoding="utf-8", engine="python")

    st.success(f"Datos cargados: {df.shape[0]} filas × {df.shape[1]} columnas")

    # ============================
    # KPIs
    # ============================
    st.subheader("📌 Indicadores Generales")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total registros", len(df))
    c2.metric("Direcciones", df["Dirección"].nunique())
    c3.metric("Áreas", df["Área"].nunique())
    c4.metric("Categorías distintas", df["Categoría"].nunique())

    # ============================
    # Función de análisis por grupo
    # ============================
    def analisis_por_grupo(columna, nombre):
        st.subheader(f"📊 Análisis por {nombre}")

        resumen = df.groupby(columna)["Categoría"].value_counts(normalize=True).mul(100).rename("Porcentaje").reset_index()
        st.markdown("**📋 Distribución (%) de Categorías**")
        st.dataframe(resumen, use_container_width=True)

        st.markdown("**📊 Gráfico de Distribución**")
        fig = px.bar(
            resumen,
            x=columna, y="Porcentaje", color="Categoría", text_auto=".1f",
            barmode="stack", title=f"Distribución de Categorías por {nombre}"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ============================
    # Análisis por Dirección / Área / Sub-área
    # ============================
    analisis_por_grupo("Dirección", "Dirección")
    analisis_por_grupo("Área", "Área")
    analisis_por_grupo("Sub-área", "Sub-área")

    # ============================
    # Mejores y peores evaluados
    # ============================
    st.subheader("🏆 Mejores y Peores Evaluados")
    # definimos "mejor" como quienes tienen más frecuencia en "CUMPLE" y "ALTO DESEMPEÑO"
    mejores = df[df["Categoría"].isin(["CUMPLE", "ALTO DESEMPEÑO"])]
    peores = df[df["Categoría"].isin(["CUMPLE PARCIALMENTE", "NO CUMPLE"])]

    st.markdown("**🔝 Evaluados con mejores resultados**")
    st.dataframe(mejores[["Evaluado", "Cargo", "Evaluador", "Categoría"]].head(10), use_container_width=True)

    st.markdown("**🔻 Evaluados con peores resultados**")
    st.dataframe(peores[["Evaluado", "Cargo", "Evaluador", "Categoría"]].head(10), use_container_width=True)

    # ============================
    # Competencias críticas
    # ============================
    competencias = [
        "LIDERAZGO MAGNETICO",
