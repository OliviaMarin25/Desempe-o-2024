import streamlit as st
import pandas as pd
import plotly.express as px

# ============================
# Configuración de la página
# ============================
st.set_page_config(page_title="Dashboard Desempeño", page_icon="📊", layout="wide")
st.title("📊 Reporte de Desempeño - Piton vs Histórico")

# ============================
# Carga de datos
# ============================
st.sidebar.header("⚙️ Configuración de datos")

archivo_piton = st.sidebar.file_uploader("Sube archivo Desempeño-Piton (CSV ;)", type=["csv"], key="piton")
archivo_historico = st.sidebar.file_uploader("Sube archivo Histórico (CSV ;)", type=["csv"], key="historico")

# Archivos por defecto
ARCHIVO_PITON = "Desempeño-Piton.csv"
ARCHIVO_HIST = "Historico.csv"

try:
    # ---- Cargar Piton ----
    if archivo_piton is not None:
        df_piton = pd.read_csv(archivo_piton, sep=";", encoding="utf-8", engine="python")
    else:
        df_piton = pd.read_csv(ARCHIVO_PITON, sep=";", encoding="utf-8", engine="python")
    df_piton["Origen"] = "Piton"

    # ---- Cargar Histórico ----
    if archivo_historico is not None:
        df_hist = pd.read_csv(archivo_historico, sep=";", encoding="utf-8", engine="python")
    else:
        df_hist = pd.read_csv(ARCHIVO_HIST, sep=";", encoding="utf-8", engine="python")
    df_hist["Origen"] = "Histórico"

    # ---- Combinar ----
    df_total = pd.concat([df_piton, df_hist], ignore_index=True)

    # ============================
    # Normalización
    # ============================
    if "Nota" in df_total.columns:
        df_total["Nota"] = df_total["Nota"].astype(str).str.replace(",", ".")
        df_total["Nota"] = pd.to_numeric(df_total["Nota"], errors="coerce")

    if "Categoría" in df_total.columns:
        df_total["Categoría"] = df_total["Categoría"].str.strip().str.upper()
        df_total["Categoría"] = df_total["Categoría"].replace({
            "NO CUMPLE": "No cumple",
            "CUMPLE PARCIALMENTE": "Cumple Parcialmente",
            "CUMPLE": "Cumple",
            "DESTACADO": "Destacado",
            "EXCEPCIONAL": "Excepcional",
            "PENDIENTE": "Pendiente"
        })

    # ============================
    # Paleta de colores y orden
    # ============================
    categoria_colores = {
        "Excepcional": "violet",
        "Destacado": "skyblue",
        "Cumple": "green",
        "Cumple Parcialmente": "gold",
        "No cumple": "red",
        "Pendiente": "lightgrey"
    }

    categoria_orden = [
        "Excepcional",
        "Destacado",
        "Cumple",
        "Cumple Parcialmente",
        "No cumple",
        "Pendiente"
    ]

    # ============================
    # Elección de dataset
    # ============================
    opcion = st.sidebar.radio("📂 Selección de datos", ["Piton", "Histórico", "Comparar ambos"])

    if opcion == "Piton":
        df = df_piton.copy()
    elif opcion == "Histórico":
        df = df_hist.copy()
    else:
        df = df_total.copy()

    st.success(f"📊 Usando dataset: **{opcion}** → {df.shape[0]} filas × {df.shape[1]} columnas")

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

    df_filtrado = df.copy()

    # Dirección
    if "Dirección" in df.columns:
        direcciones = ["Todos"] + sorted(df["Dirección"].dropna().unique())
        dir_sel = st.selectbox("Filtrar por Dirección", direcciones)
        if dir_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Dirección"] == dir_sel]

    # Área
    if "Área" in df_filtrado.columns:
        areas = ["Todos"] + sorted(df_filtrado["Área"].dropna().unique())
        area_sel = st.selectbox("Filtrar por Área", areas)
        if area_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Área"] == area_sel]

    # Sub-área
    if "Sub-área" in df_filtrado.columns:
        subareas = ["Todos"] + sorted(df_filtrado["Sub-área"].dropna().unique())
        sub_sel = st.selectbox("Filtrar por Sub-área", subareas)
        if sub_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Sub-área"] == sub_sel]

    # Evaluador
    if "Evaluador" in df.columns:
        evaluadores = ["Todos"] + sorted(df["Evaluador"].dropna().unique())
        eval_sel = st.selectbox("Filtrar por Evaluador", evaluadores)
        if eval_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Evaluador"] == eval_sel]

    st.write(f"**Registros filtrados:** {df_filtrado.shape[0]}")

    # ============================
    # Distribución de categorías
    # ============================
    if "Categoría" in df_filtrado.columns:
        st.subheader("📊 Distribución de Categorías")
        if opcion == "Comparar ambos":
            cat_counts = df_filtrado.groupby(["Origen", "Categoría"]).size().reset_index(name="Cantidad")
            fig_cat = px.bar(
                cat_counts,
                x="Categoría", y="Cantidad", color="Origen", barmode="group",
                category_orders={"Categoría": categoria_orden},
                text_auto=True
            )
        else:
            cat_counts = df_filtrado["Categoría"].value_counts().reindex(categoria_orden, fill_value=0).reset_index()
            cat_counts.columns = ["Categoría", "Cantidad"]
            fig_cat = px.bar(
                cat_counts,
                x="Categoría", y="Cantidad",
                color="Categoría",
                category_orders={"Categoría": categoria_orden},
                color_discrete_map=categoria_colores,
                text_auto=True
            )
        st.plotly_chart(fig_cat, use_container_width=True)

    # ============================
    # Promedio por Dirección (comparación si aplica)
    # ============================
    if "Dirección" in df_filtrado.columns and "Nota" in df_filtrado.columns:
        st.subheader("📊 Promedio de Nota por Dirección")
        if opcion == "Comparar ambos":
            fig_dir = px.bar(
                df_filtrado.groupby(["Origen", "Dirección"])["Nota"].mean().reset_index(),
                x="Dirección", y="Nota", color="Origen", barmode="group", text_auto=".2f"
            )
        else:
            fig_dir = px.bar(
                df_filtrado.groupby("Dirección")["Nota"].mean().reset_index(),
                x="Dirección", y="Nota", text_auto=".2f", color="Nota"
            )
        st.plotly_chart(fig_dir, use_container_width=True)

    # ============================
    # Mejores y peores evaluados
    # ============================
    if "Nota" in df_filtrado.columns:
        st.subheader("🏆 Mejores y Peores Evaluados")

        mejores = df_filtrado.sort_values("Nota", ascending=False).head(10)
        peores = df_filtrado.sort_values("Nota", ascending=True).head(10)

        st.markdown("### 🔝 Evaluados con mejores resultados")
        st.dataframe(mejores[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota", "Origen"]], use_container_width=True)

        st.markdown("### 🔻 Evaluados con peores resultados")
        st.dataframe(peores[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota", "Origen"]], use_container_width=True)

except Exception as e:
    st.error(f"❌ Error al cargar el archivo: {e}")
