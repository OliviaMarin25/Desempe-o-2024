import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard Desempeño Piton", page_icon="📊", layout="wide")
st.title("📊 Reporte de Desempeño - Piton")

# ============================
# Carga de datos
# ============================
st.sidebar.header("⚙️ Configuración de datos")
archivo_subido = st.sidebar.file_uploader("Sube tu archivo CSV (separador ;)", type=["csv"])

# Archivo por defecto en el repo
ARCHIVO_REPO = "Desempeño-Piton.csv"

try:
    if archivo_subido is not None:
        df = pd.read_csv(archivo_subido, sep=";", encoding="utf-8", engine="python")
        st.sidebar.success("✅ Usando archivo cargado por el usuario")
    else:
        df = pd.read_csv(ARCHIVO_REPO, sep=";", encoding="utf-8", engine="python")
        st.sidebar.info("ℹ️ Usando archivo por defecto del repo")

    st.success(f"Datos cargados: {df.shape[0]} filas × {df.shape[1]} columnas")

    # ============================
    # KPIs
    # ============================
    st.subheader("📌 Indicadores Generales")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total registros", len(df))
    if "Dirección" in df.columns:
        c2.metric("Direcciones", df["Dirección"].nunique())
    if "Área" in df.columns:
        c3.metric("Áreas", df["Área"].nunique())
    if "Desempeño" in df.columns:
        c4.metric("Promedio Desempeño", round(df["Desempeño"].mean(), 2))

    # ============================
    # Función de análisis por grupo
    # ============================
    def analisis_por_grupo(columna):
        if columna in df.columns and "Desempeño" in df.columns:
            st.subheader(f"📊 Análisis por {columna}")

            resumen = df.groupby(columna).agg(
                Registros=("Desempeño", "count"),
                Promedio=("Desempeño", "mean"),
                Mínimo=("Desempeño", "min"),
                Máximo=("Desempeño", "max")
            ).reset_index()
            resumen["Promedio"] = resumen["Promedio"].round(2)

            st.markdown("**📋 Tabla Resumen**")
            st.dataframe(resumen, use_container_width=True)

            st.markdown("**📊 Promedio de Desempeño**")
            fig_avg = px.bar(
                resumen,
                x=columna, y="Promedio",
                text_auto=".2f", color="Promedio",
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig_avg, use_container_width=True)

            st.markdown("**📈 Distribución de Resultados**")
            fig_box = px.box(
                df, x=columna, y="Desempeño", color=columna,
                points="all", title=f"Distribución de Desempeño por {columna}"
            )
            st.plotly_chart(fig_box, use_container_width=True)

            seleccion = st.selectbox(f"🔎 Ver detalle de un {columna}", resumen[columna].unique(), key=columna)
            detalle = df[df[columna] == seleccion][["Nombre", "Cargo", "Evaluador", "Área", "Sub-área", "Desempeño"]]
            st.markdown(f"**Detalle de colaboradores en {seleccion}**")
            st.dataframe(detalle, use_container_width=True)

    # ============================
    # Análisis por Dirección / Área / Sub-área
    # ============================
    analisis_por_grupo("Dirección")
    analisis_por_grupo("Área")
    analisis_por_grupo("Sub-área")

    # ============================
    # Mejores y peores evaluados
    # ============================
    if "Desempeño" in df.columns and "Nombre" in df.columns:
        st.subheader("🏆 Mejores y Peores Evaluados")
        top5 = df.nlargest(5, "Desempeño")[["Nombre", "Cargo", "Evaluador", "Desempeño"]]
        low5 = df.nsmallest(5, "Desempeño")[["Nombre", "Cargo", "Evaluador", "Desempeño"]]

        st.markdown("**🔝 Top 5 Mejores Evaluados**")
        st.dataframe(top5, use_container_width=True)

        st.markdown("**🔻 Top 5 Peores Evaluados**")
        st.dataframe(low5, use_container_width=True)

    # ============================
    # Competencias críticas
    # ============================
    competencias = [
        "LIDERAZGO MAGNETICO",
        "HUMILDAD",
        "VISIÓN ESTRATÉGICA",
        "RESOLUTIVIDAD",
        "GENERACIÓN DE REDES",
        "FORMADOR DE PERSONAS"
    ]

    st.subheader("⚠️ Personas con Competencias en 'Cumple Parcialmente' o 'No Cumple'")
    for comp in competencias:
        if comp in df.columns:
            criticos = df[df[comp].isin(["CUMPLE PARCIALMENTE", "NO CUMPLE"])]
            if not criticos.empty:
                st.markdown(f"### 📌 {comp}")
                st.dataframe(criticos[["Nombre", "Cargo", "Evaluador", comp]], use_container_width=True)

except Exception as e:
    st.error(f"❌ Error al cargar el archivo: {e}")
