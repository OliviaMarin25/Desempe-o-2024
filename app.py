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
    # Mejores y peores evaluados
    # ============================
    if "Nota" in df.columns:
        st.subheader("🏆 Mejores y Peores Evaluados")

        mejores = df.sort_values("Nota", ascending=False).head(10)
        peores = df.sort_values("Nota", ascending=True).head(10)

        st.markdown("### 🔝 Top 10 Mejores Evaluados")
        st.dataframe(mejores[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]], use_container_width=True)

        st.markdown("### 🔻 Top 10 Peores Evaluados")
        st.dataframe(peores[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]], use_container_width=True)

        # Descargar CSV (en vez de Excel)
        ranking = pd.concat({"Mejores": mejores, "Peores": peores})
        buffer_csv = io.BytesIO()
        ranking.to_csv(buffer_csv, index=False, encoding="utf-8-sig", sep=";")
        st.download_button(
            label="📥 Descargar Ranking (CSV)",
            data=buffer_csv.getvalue(),
            file_name="Ranking_Desempeno2024.csv",
            mime="text/csv"
        )

    # ============================
    # Liderazgo - cargos clave
    # ============================
    st.subheader("👩‍💼👨‍💼 Colaboradores con cargos de Liderazgo")

    if "Cargo" in df.columns:
        df["Cargo_upper"] = df["Cargo"].str.upper()
        cargos_liderazgo = [
            "COORDINADOR", "COORDINADORA",
            "JEFE", "JEFA",
            "SUPERVISOR", "SUPERVISORA",
            "SUBGERENTE", "SUBGERENTA",
            "GERENTE", "GERENTA",
            "DIRECTOR", "DIRECTORA"
        ]
        lideres = df[df["Cargo_upper"].str.contains("|".join(cargos_liderazgo), regex=True, na=False)]

        if not lideres.empty:
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

            # Descargar CSV
            buffer_csv = io.BytesIO()
            lideres[cols_a_mostrar].to_csv(buffer_csv, index=False, encoding="utf-8-sig", sep=";")
            st.download_button(
                label="📥 Descargar listado de líderes (CSV)",
                data=buffer_csv.getvalue(),
                file_name="Lideres_Desempeno2024.csv",
                mime="text/csv"
            )

            # ============================
            # Gráfico de distribución de líderes
            # ============================
            st.subheader("📊 Distribución de Categorías en Líderes")
            lideres_counts = lideres["Categoría"].value_counts(normalize=True).reindex(categoria_orden, fill_value=0).reset_index()
            lideres_counts.columns = ["Categoría", "Porcentaje"]
            lideres_counts["Porcentaje"] *= 100

            fig_lideres = px.bar(
                lideres_counts,
                x="Categoría", y="Porcentaje",
                color="Categoría",
                category_orders={"Categoría": categoria_orden},
                color_discrete_map=categoria_colores,
                text_auto=".1f"
            )
            fig_lideres.update_yaxes(title="% sobre líderes")
            st.plotly_chart(fig_lideres, use_container_width=True)

        else:
            st.info("No se encontraron colaboradores con cargos de liderazgo en el dataset.")

except Exception as e:
    st.error(f"❌ Error al cargar el archivo: {e}")
