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
# Función de descarga
# ============================
def download_excel(df, nombre_archivo, etiqueta):
    if df.empty:
        return
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Datos")
    st.download_button(
        label=f"💾 Descargar {etiqueta} (Excel)",
        data=buffer.getvalue(),
        file_name=nombre_archivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

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
    # Distribución de Categorías (%)
    # ============================
    if "Categoría" in df_filtrado.columns:
        st.subheader("📊 Distribución de Categorías (Total %)")
        cat_counts = (
            df_filtrado["Categoría"].value_counts(normalize=True)
            .reindex(categoria_orden, fill_value=0)
            .mul(100)
            .reset_index()
        )
        cat_counts.columns = ["Categoría", "%"]

        fig_cat = px.bar(
            cat_counts,
            x="Categoría", y="%",
            color="Categoría",
            category_orders={"Categoría": categoria_orden},
            color_discrete_map=categoria_colores,
            text_auto=".1f"
        )
        fig_cat.update_layout(yaxis_title="% de evaluados")
        st.plotly_chart(fig_cat, use_container_width=True)

        download_excel(cat_counts, "distribucion_total.xlsx", "Distribución total (%)")

    # ============================
    # Distribución por Dirección (%)
    # ============================
    if "Dirección" in df_filtrado.columns and "Categoría" in df_filtrado.columns:
        st.subheader("📊 Distribución de Categorías por Dirección (%)")
        dir_cat = (
            df_filtrado.groupby(["Dirección", "Categoría"]).size().reset_index(name="Cantidad")
        )
        total_dir = dir_cat.groupby("Dirección")["Cantidad"].transform("sum")
        dir_cat["%"] = dir_cat["Cantidad"] / total_dir * 100

        fig_dir = px.bar(
            dir_cat,
            x="Dirección",
            y="%",
            color="Categoría",
            category_orders={"Categoría": categoria_orden},
            color_discrete_map=categoria_colores,
            text_auto=".1f",
            barmode="stack"
        )
        fig_dir.update_layout(yaxis_title="% de evaluados")
        st.plotly_chart(fig_dir, use_container_width=True)

        download_excel(dir_cat, "distribucion_direccion.xlsx", "Distribución por Dirección (%)")

    # ============================
    # Distribución por Área (%)
    # ============================
    if "Área" in df_filtrado.columns and "Categoría" in df_filtrado.columns:
        st.subheader("📊 Distribución de Categorías por Área (%)")
        area_cat = (
            df_filtrado.groupby(["Área", "Categoría"]).size().reset_index(name="Cantidad")
        )
        total_area = area_cat.groupby("Área")["Cantidad"].transform("sum")
        area_cat["%"] = area_cat["Cantidad"] / total_area * 100

        fig_area = px.bar(
            area_cat,
            x="Área",
            y="%",
            color="Categoría",
            category_orders={"Categoría": categoria_orden},
            color_discrete_map=categoria_colores,
            text_auto=".1f",
            barmode="stack"
        )
        fig_area.update_layout(yaxis_title="% de evaluados")
        st.plotly_chart(fig_area, use_container_width=True)

        download_excel(area_cat, "distribucion_area.xlsx", "Distribución por Área (%)")

    # ============================
    # Distribución por Sub-área (%)
    # ============================
    if "Sub-área" in df_filtrado.columns and "Categoría" in df_filtrado.columns:
        st.subheader("📊 Distribución de Categorías por Sub-área (%)")
        sub_cat = (
            df_filtrado.groupby(["Sub-área", "Categoría"]).size().reset_index(name="Cantidad")
        )
        total_sub = sub_cat.groupby("Sub-área")["Cantidad"].transform("sum")
        sub_cat["%"] = sub_cat["Cantidad"] / total_sub * 100

        fig_sub = px.bar(
            sub_cat,
            x="Sub-área",
            y="%",
            color="Categoría",
            category_orders={"Categoría": categoria_orden},
            color_discrete_map=categoria_colores,
            text_auto=".1f",
            barmode="stack"
        )
        fig_sub.update_layout(yaxis_title="% de evaluados")
        st.plotly_chart(fig_sub, use_container_width=True)

        download_excel(sub_cat, "distribucion_subarea.xlsx", "Distribución por Sub-área (%)")

    # ============================
    # Mejores y peores evaluados
    # ============================
    if "Nota" in df_filtrado.columns:
        st.subheader("🏆 Mejores y Peores Evaluados")

        mejores = df_filtrado.sort_values("Nota", ascending=False).head(10)
        peores = df_filtrado.sort_values("Nota", ascending=True).head(10)

        st.markdown("### 🔝 Evaluados con mejores resultados")
        st.dataframe(mejores[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]], use_container_width=True)
        download_excel(mejores, "mejores_evaluados.xlsx", "Mejores evaluados")

        st.markdown("### 🔻 Evaluados con peores resultados")
        st.dataframe(peores[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]], use_container_width=True)
        download_excel(peores, "peores_evaluados.xlsx", "Peores evaluados")

    # ============================
    # Competencias críticas
    # ============================
    competencias = [
        "LIDERAZGO MAGNETICO",
        "FORMADOR DE PERSONAS",
        "VISIÓN ESTRATÉGICA",
        "GENERACIÓN DE REDES",
        "HUMILDAD",
        "RESOLUTIVIDAD"
    ]

    st.subheader("⚠️ Personas con Competencias en 'Cumple Parcialmente' o 'No Cumple'")
    for comp in competencias:
        if comp in df.columns:
            criticos = df[df[comp].isin(["CUMPLE PARCIALMENTE", "NO CUMPLE"])]
            if not criticos.empty:
                st.markdown(f"### 📌 {comp}")
                st.dataframe(criticos[["Evaluado", "Cargo", "Evaluador", comp]], use_container_width=True)
                download_excel(criticos[["Evaluado", "Cargo", "Evaluador", comp]],
                               f"criticos_{comp.lower().replace(' ', '_')}.xlsx",
                               f"Críticos en {comp}")

    # ============================
    # Líderes y sus competencias
    # ============================
    st.subheader("👔 Evaluaciones de Liderazgo (Cargos de Jefatura)")
    cargos_liderazgo = ["COORDINADOR", "JEFE", "SUPERVISOR", "SUBGERENTE", "GERENTE", "DIRECTOR"]

    if "Cargo" in df.columns:
        lideres = df[df["Cargo"].str.upper().str.contains("|".join(cargos_liderazgo), na=False)]
        if not lideres.empty:
            cols_mostrar = ["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"] + [c for c in competencias if c in df.columns]
            st.dataframe(lideres[cols_mostrar], use_container_width=True)
            download_excel(lideres[cols_mostrar], "evaluaciones_liderazgo.xlsx", "Evaluaciones de liderazgo")
        else:
            st.info("No se encontraron cargos de liderazgo en los datos cargados.")

except Exception as e:
    st.error(f"❌ Error al cargar el archivo: {e}")
