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

    # ============================
    # Normalización de columnas
    # ============================
    if "Nota" in df.columns:
        df["Nota"] = df["Nota"].astype(str).str.replace(",", ".")
        df["Nota"] = pd.to_numeric(df["Nota"], errors="coerce")

    if "Categoría" in df.columns:
        df["Categoría"] = df["Categoría"].str.strip().str.upper()
        df["Categoría"] = df["Categoría"].replace({
            "NO CUMPLE": "No cumple",
            "CUMPLE PARCIALMENTE": "Cumple Parcialmente",
            "CUMPLE": "Cumple",
            "DESTACADO": "Destacado",
            "EXCEPCIONAL": "Excepcional",
            "PENDIENTE": "Pendiente"
        })

    st.success(f"Datos cargados: {df.shape[0]} filas × {df.shape[1]} columnas")

    # ============================
    # Paleta de colores personalizada
    # ============================
    categoria_colores = {
        "No cumple": "red",
        "Cumple Parcialmente": "gold",
        "Cumple": "green",
        "Destacado": "skyblue",
        "Excepcional": "violet",
        "Pendiente": "lightgrey"
    }

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
    if "Nota" in df.columns:
        c4.metric("Promedio Nota", round(df["Nota"].mean(), 2))

    # ============================
    # Filtros jerárquicos
    # ============================
    st.subheader("🔎 Filtros")

    # Dirección
    direcciones = ["Todos"] + sorted(df["Dirección"].dropna().unique())
    dir_sel = st.selectbox("Filtrar por Dirección", direcciones)

    df_filtrado = df.copy()
    if dir_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Dirección"] == dir_sel]

    # Área dependiente de Dirección
    if "Área" in df_filtrado.columns:
        areas = ["Todos"] + sorted(df_filtrado["Área"].dropna().unique())
        area_sel = st.selectbox("Filtrar por Área", areas)
        if area_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Área"] == area_sel]
    else:
        area_sel = "Todos"

    # Sub-área dependiente de Área
    if "Sub-área" in df_filtrado.columns:
        subareas = ["Todos"] + sorted(df_filtrado["Sub-área"].dropna().unique())
        sub_sel = st.selectbox("Filtrar por Sub-área", subareas)
        if sub_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Sub-área"] == sub_sel]
    else:
        sub_sel = "Todos"

    # Evaluador independiente
    if "Evaluador" in df.columns:
        evaluadores = ["Todos"] + sorted(df["Evaluador"].dropna().unique())
        eval_sel = st.selectbox("Filtrar por Evaluador", evaluadores)
        if eval_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Evaluador"] == eval_sel]

    st.write(f"**Registros filtrados:** {df_filtrado.shape[0]}")

    # ============================
    # Distribución por Categoría
    # ============================
    if "Categoría" in df_filtrado.columns:
        st.subheader("📊 Distribución de Categorías")
        cat_counts = df_filtrado["Categoría"].value_counts().reset_index()
        cat_counts.columns = ["Categoría", "Cantidad"]
        fig_cat = px.bar(
            cat_counts,
            x="Categoría", y="Cantidad",
            color="Categoría",
            color_discrete_map=categoria_colores,
            text_auto=True
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    # ============================
    # Mejores y peores evaluados
    # ============================
    if "Nota" in df_filtrado.columns:
        st.subheader("🏆 Mejores y Peores Evaluados")

        mejores = df_filtrado.sort_values("Nota", ascending=False).head(10)
        peores = df_filtrado.sort_values("Nota", ascending=True).head(10)

        st.markdown("### 🔝 Evaluados con mejores resultados")
        st.dataframe(mejores[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]], use_container_width=True)

        st.markdown("### 🔻 Evaluados con peores resultados")
        st.dataframe(peores[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]], use_container_width=True)

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
                st.dataframe(
                    criticos[["Evaluado", "Cargo", "Evaluador", comp]],
                    use_container_width=True
                )

except Exception as e:
    st.error(f"❌ Error al cargar el archivo: {e}")
