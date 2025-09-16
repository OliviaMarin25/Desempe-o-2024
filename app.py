import streamlit as st
import pandas as pd
import plotly.express as px

# ============================
# Configuración de la página
# ============================
st.set_page_config(page_title="Dashboard Desempeño", page_icon="📊", layout="wide")
st.title("📊 Reporte de Desempeño - Piton e Histórico")

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

    # ============================
    # Normalización
    # ============================
    for df in [df_piton, df_hist]:
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
    # Análisis de desempeño actual
    # ============================
    st.header("📊 Análisis Actual - Desempeño Piton")

    df = df_piton.copy()

    st.write(f"**Registros en Piton:** {df.shape[0]}")

    if "Categoría" in df.columns:
        st.subheader("Distribución de Categorías (Actual)")
        cat_counts = df["Categoría"].value_counts().reindex(categoria_orden, fill_value=0).reset_index()
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
    # Histórico - patrones
    # ============================
    st.header("📜 Histórico - Patrones de Evaluación")

    if not df_hist.empty and "Evaluado" in df_hist.columns:
        resumen = (
            df_hist.groupby("Evaluado")
            .agg(
                n_eval=("Nota", "count"),
                nota_prom=("Nota", "mean"),
                categoria_mas_frec=("Categoría", lambda x: x.mode().iloc[0] if not x.mode().empty else None),
                categorias=("Categoría", lambda x: ", ".join(sorted(x.unique())))
            )
            .reset_index()
        )

        # Filtrar a los que tienen +1 año (ejemplo: más de 1 evaluación)
        resumen = resumen[resumen["n_eval"] > 1]

        # Muy buenos: siempre Excepcional/Destacado
        buenos = resumen[resumen["categoria_mas_frec"].isin(["Excepcional", "Destacado"])]

        # Muy malos: siempre No cumple / Cumple Parcialmente
        malos = resumen[resumen["categoria_mas_frec"].isin(["No cumple", "Cumple Parcialmente"])]

        st.subheader("🌟 Evaluados consistentemente muy buenos")
        st.dataframe(buenos, use_container_width=True)

        st.subheader("⚠️ Evaluados consistentemente muy malos")
        st.dataframe(malos, use_container_width=True)

    else:
        st.info("No hay datos históricos cargados o faltan columnas requeridas.")

except Exception as e:
    st.error(f"❌ Error al cargar el archivo: {e}")
