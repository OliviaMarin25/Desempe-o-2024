import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Reporte Desempeño 2024", layout="wide")

st.title("📊 Reporte de Desempeño - 2024")

# ============================
# Subida de archivo
# ============================
uploaded_file = st.file_uploader("📂 Sube el archivo CSV de desempeño", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        st.stop()

    # ============================
    # Filtros en fila
    # ============================
    st.subheader("🔎 Filtros")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        direcciones = ["Todas"] + sorted(df["Dirección"].dropna().unique())
        direccion_sel = st.selectbox("Dirección", direcciones)

    with col2:
        if direccion_sel != "Todas":
            areas = ["Todas"] + sorted(df[df["Dirección"] == direccion_sel]["Área"].dropna().unique())
        else:
            areas = ["Todas"] + sorted(df["Área"].dropna().unique())
        area_sel = st.selectbox("Área", areas)

    with col3:
        if area_sel != "Todas" and direccion_sel != "Todas":
            subareas = ["Todas"] + sorted(df[(df["Dirección"] == direccion_sel) & (df["Área"] == area_sel)]["Sub-área"].dropna().unique())
        elif direccion_sel != "Todas":
            subareas = ["Todas"] + sorted(df[df["Dirección"] == direccion_sel]["Sub-área"].dropna().unique())
        else:
            subareas = ["Todas"] + sorted(df["Sub-área"].dropna().unique())
        subarea_sel = st.selectbox("Sub-área", subareas)

    with col4:
        if subarea_sel != "Todas":
            evaluadores = ["Todos"] + sorted(df[df["Sub-área"] == subarea_sel]["Evaluador"].dropna().unique())
        elif area_sel != "Todas":
            evaluadores = ["Todos"] + sorted(df[df["Área"] == area_sel]["Evaluador"].dropna().unique())
        elif direccion_sel != "Todas":
            evaluadores = ["Todos"] + sorted(df[df["Dirección"] == direccion_sel]["Evaluador"].dropna().unique())
        else:
            evaluadores = ["Todos"] + sorted(df["Evaluador"].dropna().unique())
        evaluador_sel = st.selectbox("Evaluador", evaluadores)

    # Aplicar filtros
    df_filtered = df.copy()
    if direccion_sel != "Todas":
        df_filtered = df_filtered[df_filtered["Dirección"] == direccion_sel]
    if area_sel != "Todas":
        df_filtered = df_filtered[df_filtered["Área"] == area_sel]
    if subarea_sel != "Todas":
        df_filtered = df_filtered[df_filtered["Sub-área"] == subarea_sel]
    if evaluador_sel != "Todos":
        df_filtered = df_filtered[df_filtered["Evaluador"] == evaluador_sel]

    # ============================
    # Distribución de Categorías
    # ============================
    st.subheader("📊 Distribución de Categorías")

    modo = st.radio("Ver gráfico por:", ["Porcentaje (%)", "Cantidad (N personas)"], horizontal=True)

    dist = df_filtered["Categoría"].value_counts().reset_index()
    dist.columns = ["Categoría", "Cantidad"]
    dist["Porcentaje"] = (dist["Cantidad"] / dist["Cantidad"].sum()) * 100

    colores = {
        "Excepcional": "violet",
        "Destacado": "skyblue",
        "Cumple": "green",
        "Cumple Parcialmente": "yellow",
        "No cumple": "red",
        "Pendiente": "lightgray"
    }

    if modo == "Porcentaje (%)":
        fig = px.bar(dist, x="Categoría", y="Porcentaje", text=dist["Porcentaje"].round(1).astype(str) + "%",
                     color="Categoría", color_discrete_map=colores)
        fig.update_yaxes(title="Porcentaje (%)")
    else:
        fig = px.bar(dist, x="Categoría", y="Cantidad", text=dist["Cantidad"],
                     color="Categoría", color_discrete_map=colores)
        fig.update_yaxes(title="Cantidad de personas")

    st.plotly_chart(fig, use_container_width=True)

    # ============================
    # Mejores y peores evaluados
    # ============================
    st.subheader("🏆 Mejores y Peores Evaluados")

    mejores = df_filtered.sort_values("Nota", ascending=False).head(20).copy()
    peores = df_filtered.sort_values("Nota", ascending=True).head(20).copy()

    # Columna editable "Acciones"
    for dataset in [mejores, peores]:
        if "Acciones" not in dataset.columns:
            dataset["Acciones"] = ""

    tab1, tab2 = st.tabs(["✨ Top 20 Mejores", "⚠️ Top 20 Peores"])

    with tab1:
        st.data_editor(mejores, num_rows="dynamic", use_container_width=True)
        st.download_button("⬇️ Descargar mejores (CSV)", data=mejores.to_csv(index=False).encode("utf-8"), file_name="mejores.csv", mime="text/csv")

    with tab2:
        st.data_editor(peores, num_rows="dynamic", use_container_width=True)
        st.download_button("⬇️ Descargar peores (CSV)", data=peores.to_csv(index=False).encode("utf-8"), file_name="peores.csv", mime="text/csv")

    # ============================
    # Trabajadores con cargos de liderazgo + Ranking
    # ============================
    st.subheader("👩‍💼👨‍💼 Trabajadores con cargos de Liderazgo")

    competencias = [
        "Humildad",
        "Resolutividad",
        "Liderazgo Magnético",
        "Visión Estratégica",
        "Generación de Redes y Relaciones Efectivas",
        "Formador de Personas"
    ]

    cargos_liderazgo = ["JEFE", "COORDINADOR", "SUPERVISOR", "SUBGERENTE", "GERENTE", "DIRECTOR"]
    mask_lideres = df["Cargo"].str.upper().str.contains("|".join(cargos_liderazgo), na=False)
    df_lideres = df[mask_lideres].copy()

    if not df_lideres.empty:
        # Crear columna con promedio de las 6 competencias
        df_lideres["Promedio Competencias Liderazgo"] = df_lideres[competencias].mean(axis=1, numeric_only=True)

        # Ordenar y asignar ranking
        df_lideres = df_lideres.sort_values("Promedio Competencias Liderazgo", ascending=False)
        df_lideres["Ranking"] = range(1, len(df_lideres) + 1)

        # Mostrar tabla igual que antes, pero con ranking y promedio
        columnas_lideres = ["Ranking", "Evaluado", "Cargo", "Evaluador", "Categoría", "Nota", "Promedio Competencias Liderazgo"]
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

        # Dropdowns con opción "Ninguna"
        direcciones_disp = ["Ninguna"] + list(df["Dirección"].dropna().unique())
        dir_sel_radar = st.selectbox("Selecciona dirección", direcciones_disp)

        if dir_sel_radar != "Ninguna":
            lideres_disponibles = ["Ninguno"] + list(df_comp[df_comp["Dirección"] == dir_sel_radar]["Evaluado"].dropna().unique())
        else:
            lideres_disponibles = ["Ninguno"]

        lider_sel = st.selectbox("Selecciona un líder", lideres_disponibles)

        promedio_dir, datos_lider = None, None
        if dir_sel_radar != "Ninguna":
            promedio_dir = df_comp[df_comp["Dirección"] == dir_sel_radar][competencias].mean().round(2)
        if lider_sel != "Ninguno":
            datos_lider = df_comp[df_comp["Evaluado"] == lider_sel][competencias].mean().round(2)

        fig = go.Figure()

        # Clínica (azul oscuro)
        fig.add_trace(go.Scatterpolar(
            r=promedio_clinica.values,
            theta=competencias,
            fill='toself',
            name='Promedio clínica',
            line=dict(color="darkblue"),
            fillcolor="rgba(0,0,139,0.3)"
        ))

        # Dirección (amarillo)
        if promedio_dir is not None and not promedio_dir.isnull().all():
            fig.add_trace(go.Scatterpolar(
                r=promedio_dir.values,
                theta=competencias,
                fill='toself',
                name=f'Dirección: {dir_sel_radar}',
                line=dict(color="gold"),
                fillcolor="rgba(255,215,0,0.3)"
            ))

        # Líder (celeste)
        if datos_lider is not None and not datos_lider.isnull().all():
            fig.add_trace(go.Scatterpolar(
                r=datos_lider.values,
                theta=competencias,
                fill='toself',
                name=f'Líder: {lider_sel}',
                line=dict(color="deepskyblue"),
                fillcolor="rgba(0,191,255,0.3)"
            ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("📂 Sube un archivo CSV para comenzar.")
