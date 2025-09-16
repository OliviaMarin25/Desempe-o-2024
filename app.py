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
    if "Nota" in df.columns:
        c4.metric("Promedio Nota", round(df["Nota"].mean(), 2))

    # ============================
    # Dropdown con opción "Todos"
    # ============================
    st.subheader("🔎 Filtros")

    filtros = {}
    for col in ["Dirección", "Área", "Sub-área", "Evaluador"]:
        if col in df.columns:
            opciones = ["Todos"] + sorted(df[col].dropna().unique())
            seleccion = st.selectbox(f"Filtrar por {col}", opciones, key=col)
            if seleccion != "Todos":
                filtros[col] = seleccion

    # Aplicar filtros
    df_filtrado = df.copy()
    for col, valor in filtros.items():
        df_filtrado = df_filtrado[df_filtrado[col] == valor]

    st.write(f"**Registros filtrados:** {df_filtrado.shape[0]}")

    # ============================
    # Gráficos comparativos
    # ============================
    if "Dirección" in df_filtrado.columns and "Nota" in df_filtrado.columns:
        st.subheader("📊 Promedio de Nota por Dirección")
        fig_dir = px.bar(
            df_filtrado.groupby("Dirección")["Nota"].mean().reset_index(),
            x="Dirección", y="Nota", text_auto=".2f", color="Nota"
        )
        st.plotly_chart(fig_dir, use_container_width=True)

    if "Área" in df_filtrado.columns and "Nota" in df_filtrado.columns:
        st.subheader("📊 Promedio de Nota por Área")
        fig_area = px.bar(
            df_filtrado.groupby("Área")["Nota"].mean().reset_index(),
            x="Área", y="Nota", text_auto=".2f", color="Nota"
        )
        st.plotly_chart(fig_area, use_container_width=True)

    if "Sub-área" in df_filtrado.columns and "Nota" in df_filtrado.columns:
        st.subheader("📊 Promedio de Nota por Sub-área")
        fig_sub = px.bar(
            df_filtrado.groupby("Sub-área")["Nota"].mean().reset_index(),
            x="Sub-área", y="Nota", text_auto=".2f", color="Nota"
        )
        st.plotly_chart(fig_sub, use_container_width=True)

    if "Evaluador" in df_filtrado.columns and "Nota" in df_filtrado.columns:
        st.subheader("📊 Promedio de Nota por Evaluador")
        fig_eval = px.bar(
            df_filtrado.groupby("Evaluador")["Nota"].mean().reset_index(),
            x="Evaluador", y="Nota", text_auto=".2f", color="Nota"
        )
        st.plotly_chart(fig_eval, use_container_width=True)

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
