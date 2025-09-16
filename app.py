import streamlit as st
import pandas as pd
import plotly.express as px
import io

# ============================
# Configuración de la página
# ============================
st.set_page_config(page_title="Dashboard Desempeño 2024", page_icon="📊", layout="wide")
st.title("📊 Reporte de Desempeño - 2024")

# ============================
# Carga de datos
# ============================
st.sidebar.header("⚙️ Configuración de datos")

archivo_subido = st.sidebar.file_uploader("Sube tu archivo CSV (separador ;)", type=["csv"])
ARCHIVO_REPO = "Desempeño 2024.csv"

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
    # Distribución por Categoría (%)
    # ============================
    if "Categoría" in df.columns:
        st.subheader("📊 Distribución de Categorías")
        cat_counts = df["Categoría"].value_counts(normalize=True).reindex(categoria_orden, fill_value=0).reset_index()
        cat_counts.columns = ["Categoría", "Porcentaje"]
        cat_counts["Porcentaje"] *= 100

        fig_cat = px.bar(
            cat_counts,
            x="Categoría", y="Porcentaje",
            color="Categoría",
            category_orders={"Categoría": categoria_orden},
            color_discrete_map=categoria_colores,
            text_auto=".1f"
        )
        fig_cat.update_yaxes(title="% sobre total")
        st.plotly_chart(fig_cat, use_container_width=True)

    # ============================
    # Liderazgo - cargos clave
    # ============================
    st.subheader("👩‍💼👨‍💼 Colaboradores con cargos de Liderazgo")

    # Normalizar columna Cargo
    if "Cargo" in df.columns:
        df["Cargo_upper"] = df["Cargo"].str.upper()

        # Palabras clave (masculino y femenino)
        cargos_liderazgo = [
            "COORDINADOR", "COORDINADORA",
            "JEFE", "JEFA",
            "SUPERVISOR", "SUPERVISORA",
            "SUBGERENTE", "SUBGERENTA",
            "GERENTE", "GERENTA",
            "DIRECTOR", "DIRECTORA"
        ]

        # Filtrar líderes
        lideres = df[df["Cargo_upper"].str.contains("|".join(cargos_liderazgo), regex=True, na=False)]

        if not lideres.empty:
            # Selección de columnas a mostrar
            competencias = [
                "LIDERAZGO MAGNETICO",
                "FORMADOR DE PERSONAS",
                "VISIÓN ESTRATÉGICA",
                "GENERACIÓN DE REDES",
                "HUMILDAD",
                "RESOLUTIVIDAD"
            ]
            cols_a_mostrar = ["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"] + [c for c in competencias if c in lideres.columns]

            st.dataframe(lideres[cols_a_mostrar], use_container_width=True)

            # Botón para descargar Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                lideres[cols_a_mostrar].to_excel(writer, index=False, sheet_name="Liderazgo")
            st.download_button(
                label="📥 Descargar listado de líderes",
                data=buffer.getvalue(),
                file_name="Lideres_Desempeno2024.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No se encontraron colaboradores con cargos de liderazgo en el dataset.")

except Exception as e:
    st.error(f"❌ Error al cargar el archivo: {e}")
