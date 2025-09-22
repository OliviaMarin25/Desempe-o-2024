import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
    # Filtros jerárquicos
    # ============================
    st.subheader("🔎 Filtros")

    direcciones = ["Todos"] + sorted(df["Dirección"].dropna().unique())
    dir_sel = st.selectbox("Filtrar por Dirección", direcciones)

    df_filtrado = df.copy()
    if dir_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Dirección"] == dir_sel]

    if "Área" in df_filtrado.columns:
        areas = ["Todos"] + sorted(df_filtrado["Área"].dropna().unique())
        area_sel = st.selectbox("Filtrar por Área", areas)
        if area_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Área"] == area_sel]
    else:
        area_sel = "Todos"

    if "Sub-área" in df_filtrado.columns:
        subareas = ["Todos"] + sorted(df_filtrado["Sub-área"].dropna().unique())
        sub_sel = st.selectbox("Filtrar por Sub-área", subareas)
        if sub_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Sub-área"] == sub_sel]
    else:
        sub_sel = "Todos"

    if "Evaluador" in df.columns:
        evaluadores = ["Todos"] + sorted(df["Evaluador"].dropna().unique())
        eval_sel = st.selectbox("Filtrar por Evaluador", evaluadores)
        if eval_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Evaluador"] == eval_sel]

    st.write(f"**Registros filtrados:** {df_filtrado.shape[0]}")

    # ============================
    # Distribución por Categoría (%)
    # ============================
    if "Categoría" in df_filtrado.columns:
        st.subheader("📊 Distribución de Categorías (%)")
        cat_counts = df_filtrado["Categoría"].value_counts(normalize=True).reindex(categoria_orden, fill_value=0) * 100
        cat_counts = cat_counts.reset_index()
        cat_counts.columns = ["Categoría", "Porcentaje"]

        fig_cat = px.bar(
            cat_counts,
            x="Categoría", y="Porcentaje",
            color="Categoría",
            category_orders={"Categoría": categoria_orden},
            color_discrete_map=categoria_colores,
            text_auto=".1f"
        )
        fig_cat.update_yaxes(title="Porcentaje (%)")
        st.plotly_chart(fig_cat, use_container_width=True)

        st.download_button("⬇️ Descargar distribución (CSV)", cat_counts.to_csv(index=False).encode("utf-8"), "distribucion_categorias.csv", "text/csv")

    # ============================
    # Mejores y peores evaluados
    # ============================
    if "Nota" in df_filtrado.columns:
        st.subheader("🏆 Mejores y Peores Evaluados")

        mejores = df_filtrado.sort_values("Nota", ascending=False).head(10)
        peores = df_filtrado.sort_values("Nota", ascending=True).head(20)

        st.markdown("### 🔝 Top 10 Mejores Evaluados")
        st.dataframe(mejores[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]], use_container_width=True)
        st.download_button("⬇️ Descargar mejores (CSV)", mejores.to_csv(index=False).encode("utf-8"), "top_mejores.csv", "text/csv")

        st.markdown("### 🔻 Top 20 Peores Evaluados")
        st.dataframe(peores[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]], use_container_width=True)
        st.download_button("⬇️ Descargar peores (CSV)", peores.to_csv(index=False).encode("utf-8"), "top_peores.csv", "text/csv")

    # ============================
    # Colaboradores con cargos de liderazgo
    # ============================
    st.subheader("👩‍💼👨‍💼 Colaboradores con cargos de Liderazgo")

    competencias = [
        "Liderazgo Magnético",
        "Formador de Personas",
        "Visión Estratégica",
        "Generación de Redes y Relaciones Efectivas",
        "Humildad",
        "Resolutividad"
    ]

    cargos_liderazgo = ["JEFE", "COORDINADOR", "SUPERVISOR", "SUBGERENTE", "GERENTE", "DIRECTOR"]
    mask_lideres = df["Cargo"].str.upper().str.contains("|".join(cargos_liderazgo), na=False)
    df_lideres = df[mask_lideres].copy()

    if not df_lideres.empty:
        columnas_lideres = ["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"] + [c for c in competencias if c in df.columns]
        st.dataframe(df_lideres[columnas_lideres], use_container_width=True)
        st.download_button("⬇️ Descargar listado de líderes (CSV)", df_lideres[columnas_lideres].to_csv(index=False).encode("utf-8"), "lideres.csv", "text/csv")

    # ============================
    # Radar de competencias de liderazgo
    # ============================
    st.subheader("🕸️ Evaluación de Competencias de Liderazgo (Radar)")

    if all(col in df.columns for col in competencias):
        df_comp = df_lideres.copy()
        df_comp = df_comp[df_comp["Categoría"] != "Pendiente"]

        mapping = {"No cumple": 1, "Cumple Parcialmente": 2, "Cumple": 3, "Destacado": 4, "Excepcional": 5}
        for col in competencias:
            df_comp[col] = pd.to_numeric(df_comp[col], errors="coerce").fillna(df_comp[col].map(mapping))

        promedio_clinica = df_comp[competencias].mean().round(2)

        dir_sel_radar = st.selectbox("Comparar dirección específica", ["Ninguna"] + list(df["Dirección"].dropna().unique()))

        if dir_sel_radar != "Ninguna":
            promedio_dir = df_comp[df_comp["Dirección"] == dir_sel_radar][competencias].mean().round(2)
            lideres_disponibles = df_comp[df_comp["Dirección"] == dir_sel_radar]["Evaluado"].dropna().unique()
        else:
            promedio_dir = None
            lideres_disponibles = df_comp["Evaluado"].dropna().unique()

        lider_sel = st.selectbox("Comparar un líder específico", ["Ninguno"] + list(lideres_disponibles))
        if lider_sel != "Ninguno":
            datos_lider = df_comp[df_comp["Evaluado"] == lider_sel][competencias].mean().round(2)
        else:
            datos_lider = None

        # ============================
        # Radar Plot
        # ============================
        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=promedio_clinica.values,
            theta=competencias,
            fill='toself',
            name='Promedio clínica',
            line=dict(color="darkblue"),
            fillcolor="rgba(0,0,139,0.4)"
        ))

        if promedio_dir is not None and not promedio_dir.isnull().all():
            fig.add_trace(go.Scatterpolar(
                r=promedio_dir.values,
                theta=competencias,
                fill='toself',
                name=f'{dir_sel_radar}',
                line=dict(color="darkgreen"),
                fillcolor="rgba(0,128,0,0.4)"
            ))

        if datos_lider is not None and not datos_lider.isnull().all():
            fig.add_trace(go.Scatterpolar(
                r=datos_lider.values,
                theta=competencias,
                fill='toself',
                name=f'Líder: {lider_sel}',
                line=dict(color="darkorange"),
                fillcolor="rgba(255,140,0,0.4)"
            ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

        # ============================
        # Cuadro comparativo (con flechas y redondeo)
        # ============================
        comparacion_data = pd.DataFrame({
            "Promedio Clínica": promedio_clinica.values,
            f"{dir_sel_radar if dir_sel_radar != 'Ninguna' else 'Dirección'}": promedio_dir.values if promedio_dir is not None else [None]*len(competencias),
            f"Líder: {lider_sel}" if lider_sel != "Ninguno" else "Líder": datos_lider.values if datos_lider is not None else [None]*len(competencias)
        }, index=competencias)

        if datos_lider is not None and promedio_dir is not None:
            for comp in competencias:
                if pd.notna(datos_lider[comp]) and pd.notna(promedio_dir[comp]):
                    if datos_lider[comp] > promedio_dir[comp]:
                        comparacion_data.loc[comp, f"Líder: {lider_sel}"] = f"⬆️ {datos_lider[comp]:.2f}"
                    elif datos_lider[comp] < promedio_dir[comp]:
                        comparacion_data.loc[comp, f"Líder: {lider_sel}"] = f"⬇️ {datos_lider[comp]:.2f}"
                    else:
                        comparacion_data.loc[comp, f"Líder: {lider_sel}"] = f"- {datos_lider[comp]:.2f}"

        comparacion_data = comparacion_data.T

        st.markdown("### 📋 Comparación Numérica de Competencias")
        st.dataframe(comparacion_data, use_container_width=True)

    else:
        st.info("⚠️ No se encontraron todas las competencias de liderazgo en el archivo cargado.")

except Exception as e:
    st.error(f"❌ Error al cargar el archivo: {e}")
