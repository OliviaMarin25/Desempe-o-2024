import streamlit as st
import pandas as pd
import plotly.express as px

# ============================
# Configuración de la página
# ============================
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
        st.sidebar.success("✅ Usando archivo cargado por el usuario")
    else:
        df = pd.read_csv(ARCHIVO_REPO, sep=";", encoding="utf-8", engine="python")
        st.sidebar.info("ℹ️ Usando archivo por defecto del repo")

    st.success(f"Datos cargados: {df.shape[0]} filas × {df.shape[1]} columnas")

    # ============================
    # Normalización de columnas
    # ============================
    if "Nota" in df.columns:
        # Reemplazar coma decimal por punto y convertir a número
        df["Nota"] = df["Nota"].astype(str).str.replace(",", ".")
        df["Nota"] = pd.to_numeric(df["Nota"], errors="coerce")

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
    if "Categoría" in df.columns:
        c4.metric("Categorías distintas", df["Categoría"].nunique())

    # ============================
    # Función de análisis por grupo
    # ============================
    def analisis_por_grupo(columna, nombre):
        if columna in df.columns and "Categoría" in df.columns:
            st.subheader(f"📊 Análisis por {nombre}")

            resumen = (
                df.groupby(columna)["Categoría"]
                .value_counts(normalize=True)
                .mul(100)
                .rename("Porcentaje")
                .reset_index()
            )

            st.markdown("**📋 Distribución (%) de Categorías**")
            st.dataframe(resumen, use_container_width=True)

            fig = px.bar(
                resumen,
                x=columna,
                y="Porcentaje",
                color="Categoría",
                text_auto=".1f",
                barmode="stack",
                title=f"Distribución de Categorías por {nombre}"
            )
            st.plotly_chart(fig, use_container_width=True)

            seleccion = st.selectbox(
                f"🔎 Ver detalle de un {nombre}",
                resumen[columna].unique(),
                key=columna
            )
            detalle_cols = ["Evaluado", "Cargo", "Evaluador", "Categoría"]
            if "Nota" in df.columns:
                detalle_cols.append("Nota")
            detalle = df[df[columna] == seleccion][detalle_cols]
            st.markdown(f"**Detalle de colaboradores en {seleccion}**")
            st.dataframe(detalle, use_container_width=True)

    # ============================
    # Análisis por Dirección / Área / Sub-área
    # ============================
    analisis_por_grupo("Dirección", "Dirección")
    analisis_por_grupo("Área", "Área")
    analisis_por_grupo("Sub-área", "Sub-área")

    # ============================
    # Mejores y peores evaluados (ranking por Nota)
    # ============================
    st.subheader("🏆 Mejores y Peores Evaluados")

    if "Nota" in df.columns:
        mejores = df.sort_values("Nota", ascending=False).head(10)
        peores = df.sort_values("Nota", ascending=True).head(10)

        st.markdown("**🔝 Top 10 Mejores Evaluados (por Nota)**")
        st.dataframe(mejores[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]], use_container_width=True)

        st.markdown("**🔻 Top 10 Peores Evaluados (por Nota)**")
        st.dataframe(peores[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]], use_container_width=True)
    else:
        st.warning("⚠️ La columna 'Nota' no está disponible en el archivo.")

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
            criticos = df[df[comp].isin(["Cumple Parcialmente", "No Cumple"])]
            if not criticos.empty:
                st.markdown(f"### 📌 {comp}")
                cols = ["Evaluado", "Cargo", "Evaluador", comp]
                if "Nota" in df.columns:
                    cols.append("Nota")
                st.dataframe(
                    criticos[cols],
                    use_container_width=True
                )

except Exception as e:
    st.error(f"❌ Error al cargar el archivo: {e}")
