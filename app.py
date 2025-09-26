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
# Carga de datos (desde uploader)
# ============================
st.sidebar.header("⚙️ Configuración de datos")
archivo_subido = st.sidebar.file_uploader("Sube tu archivo CSV (separador ;)", type=["csv"])

if archivo_subido is None:
    st.warning("📂 Por favor, sube un archivo CSV para comenzar.")
    st.stop()

try:
    df = pd.read_csv(archivo_subido, sep=";", encoding="utf-8", engine="python")

    # Normalización de columnas
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

    st.success(f"✅ Datos cargados: {df.shape[0]} filas × {df.shape[1]} columnas")

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

    col1, col2, col3, col4 = st.columns(4)

    direcciones = ["Todos"] + sorted(df["Dirección"].dropna().unique())
    with col1:
        dir_sel = st.selectbox("Filtrar por Dirección", direcciones)

    df_filtrado = df.copy()
    if dir_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Dirección"] == dir_sel]

    if "Área" in df_filtrado.columns:
        areas = ["Todos"] + sorted(df_filtrado["Área"].dropna().unique())
        with col2:
            area_sel = st.selectbox("Filtrar por Área", areas)
        if area_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Área"] == area_sel]
    else:
        area_sel = "Todos"

    if "Sub-área" in df_filtrado.columns:
        subareas = ["Todos"] + sorted(df_filtrado["Sub-área"].dropna().unique())
        with col3:
            sub_sel = st.selectbox("Filtrar por Sub-área", subareas)
        if sub_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Sub-área"] == sub_sel]
    else:
        sub_sel = "Todos"

    if "Evaluador" in df_filtrado.columns:
        evaluadores = ["Todos"] + sorted(df_filtrado["Evaluador"].dropna().unique())
        with col4:
            eval_sel = st.selectbox("Filtrar por Evaluador", evaluadores)
        if eval_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Evaluador"] == eval_sel]

    st.write(f"**Registros filtrados:** {df_filtrado.shape[0]}")

    # ============================
    # Distribución por Categoría
    # ============================
    if "Categoría" in df_filtrado.columns:
        st.subheader("📊 Distribución de Categorías")

        modo_grafico = st.radio("Ver gráfico por:", ["Porcentaje (%)", "Cantidad (N personas)"], horizontal=True)

        if modo_grafico == "Porcentaje (%)":
            cat_counts = df_filtrado["Categoría"].value_counts(normalize=True).reindex(categoria_orden, fill_value=0) * 100
            y_title = "Porcentaje (%)"
        else:
            cat_counts = df_filtrado["Categoría"].value_counts().reindex(categoria_orden, fill_value=0)
            y_title = "Cantidad (N personas)"

        cat_counts = cat_counts.reset_index()
        cat_counts.columns = ["Categoría", "Valor"]

        fig_cat = px.bar(
            cat_counts,
            x="Categoría", y="Valor",
            color="Categoría",
            category_orders={"Categoría": categoria_orden},
            color_discrete_map=categoria_colores,
            text="Valor"
        )
        fig_cat.update_traces(texttemplate="%{y}")
        fig_cat.update_yaxes(title=y_title)
        st.plotly_chart(fig_cat, use_container_width=True)

    # ============================
    # Mejores y peores evaluados (editable)
    # ============================
    if "Nota" in df_filtrado.columns:
        st.subheader("🏆 Mejores y Peores Evaluados")

        mejores = df_filtrado.sort_values("Nota", ascending=False).head(20).copy()
        peores = df_filtrado.sort_values("Nota", ascending=True).head(20).copy()

        if "Acciones" not in mejores.columns:
            mejores["Acciones"] = ""
        if "Acciones" not in peores.columns:
            peores["Acciones"] = ""

        st.markdown("### 🔝 Top 20 Mejores Evaluados")
        mejores_edit = st.data_editor(mejores[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota", "Acciones"]],
                                      use_container_width=True, num_rows="dynamic")
        st.download_button("⬇️ Descargar mejores (CSV)", mejores_edit.to_csv(index=False).encode("utf-8"),
                           "top_mejores.csv", "text/csv")

        st.markdown("### 🔻 Top 20 Peores Evaluados")
        peores_edit = st.data_editor(peores[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota", "Acciones"]],
                                     use_container_width=True, num_rows="dynamic")
        st.download_button("⬇️ Descargar peores (CSV)", peores_edit.to_csv(index=False).encode("utf-8"),
                           "top_peores.csv", "text/csv")

    # ============================
    # Trabajadores con cargos de liderazgo
    # ============================
    st.subheader("👩‍💼👨‍💼 Trabajadores con cargos de Liderazgo")

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

    # ============================
    # Radar de competencias
    # ============================
    st.subheader("🕸️ Evaluación de Competencias de Liderazgo (Radar)")

    if all(col in df.columns for col in competencias):
        df_comp = df_lideres.copy()
        df_comp = df_comp[df_comp["Categoría"] != "Pendiente"]

        mapping = {"No cumple": 1, "Cumple Parcialmente": 2, "Cumple": 3, "Destacado": 4, "Excepcional": 5}
        for col in competencias:
            df_comp[col] = pd.to_numeric(df_comp[col], errors="coerce").fillna(df_comp[col].map(mapping))

        promedio_clinica = df_comp[competencias].mean().round(2)

        modo_radar = st.radio("Ver radar con:", ["Solo clínica", "Clínica + Dirección", "Clínica + Dirección + Líder"], horizontal=True)

        promedio_dir = None
        datos_lider = None

        if modo_radar in ["Clínica + Dirección", "Clínica + Dirección + Líder"]:
            dir_sel_radar = st.selectbox("Selecciona dirección", list(df["Dirección"].dropna().unique()))
            promedio_dir = df_comp[df_comp["Dirección"] == dir_sel_radar][competencias].mean().round(2)

        if modo_radar == "Clínica + Dirección + Líder":
            lideres_disponibles = df_comp[df_comp["Dirección"] == dir_sel_radar]["Evaluado"].dropna().unique()
            lider_sel = st.selectbox("Selecciona un líder", lideres_disponibles)
            datos_lider = df_comp[df_comp["Evaluado"] == lider_sel][competencias].mean().round(2)

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=promedio_clinica.values,
            theta=competencias,
            fill='toself',
            name='Promedio clínica',
            line=dict(color="blue"),
            fillcolor="rgba(0,0,255,0.3)"
        ))

        if promedio_dir is not None:
            fig.add_trace(go.Scatterpolar(
                r=promedio_dir.values,
                theta=competencias,
                fill='toself',
                name=f'Dirección: {dir_sel_radar}',
                line=dict(color="darkred"),
                fillcolor="rgba(178,34,34,0.3)"
            ))

        if datos_lider is not None:
            fig.add_trace(go.Scatterpolar(
                r=datos_lider.values,
                theta=competencias,
                fill='toself',
                name=f'Líder: {lider_sel}',
                line=dict(color="darkorange"),
                fillcolor="rgba(255,140,0,0.3)"
            ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error al cargar el archivo: {e}")
