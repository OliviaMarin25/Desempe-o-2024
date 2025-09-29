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
            subareas = ["Todas"] + sorted(
                df[(df["Dirección"] == direccion_sel) & (df["Área"] == area_sel)]["Sub-área"].dropna().unique()
            )
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
    # Distribución de Categorías (con orden fijo)
    # ============================
    st.subheader("📊 Distribución de Categorías")

    modo = st.radio("Ver gráfico por:", ["Porcentaje (%)", "Cantidad (N personas)"], horizontal=True)

    categoria_orden = [
        "Excepcional",
        "Destacado",
        "Cumple",
        "Cumple Parcialmente",
        "No cumple",
        "Pendiente"
    ]

    colores = {
        "Excepcional": "violet",
        "Destacado": "skyblue",
        "Cumple": "green",
        "Cumple Parcialmente": "yellow",
        "No cumple": "red",
        "Pendiente": "lightgray"
    }

    dist = df_filtered["Categoría"].value_counts().reindex(categoria_orden, fill_value=0).reset_index()
    dist.columns = ["Categoría", "Cantidad"]
    dist["Porcentaje"] = (dist["Cantidad"] / dist["Cantidad"].sum()) * 100

    if modo == "Porcentaje (%)":
        fig = px.bar(
            dist, x="Categoría", y="Porcentaje",
            text=dist["Porcentaje"].round(1).astype(str) + "%",
            color="Categoría", color_discrete_map=colores,
            category_orders={"Categoría": categoria_orden}
        )
        fig.update_yaxes(title="Porcentaje (%)")
    else:
        fig = px.bar(
            dist, x="Categoría", y="Cantidad",
            text=dist["Cantidad"],
            color="Categoría", color_discrete_map=colores,
            category_orders={"Categoría": categoria_orden}
        )
        fig.update_yaxes(title="Cantidad de personas")

    st.plotly_chart(fig, use_container_width=True)

    # ============================
    # Mejores y peores evaluados
    # ============================
    st.subheader("🏆 Mejores y Peores Evaluados")

    # Convertir Nota a numérico
    df_filtered["Nota_num"] = pd.to_numeric(df_filtered["Nota"], errors="coerce")
    df_valid = df_filtered.dropna(subset=["Nota_num"])

    mejores = df_valid.sort_values("Nota_num", ascending=False).head(20)
    peores = df_valid.sort_values("Nota_num", ascending=True).head(20)

    st.markdown("### 🔝 Top 20 Mejores Evaluados")
    st.dataframe(mejores[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]], use_container_width=True)

    st.markdown("### 🔻 Top 20 Peores Evaluados")
    st.dataframe(peores[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]], use_container_width=True)

    # ============================
    # Trabajadores con cargos de Liderazgo
    # ============================
    st.subheader("👩‍💼👨‍💼 Trabajadores con cargos de Liderazgo")

    competencias = [
        "Humildad",
        "Resolutividad",
        "Formador de Personas",
        "Liderazgo Magnético",
        "Visión Estratégica",
        "Generación de Redes y Relaciones Efectivas"
    ]

    cargos_liderazgo = ["JEFE", "COORDINADOR", "SUPERVISOR", "SUBGERENTE", "GERENTE", "DIRECTOR"]
    mask_lideres = df["Cargo"].str.upper().str.contains("|".join(cargos_liderazgo), na=False)
    df_lideres = df[mask_lideres].copy()

    if not df_lideres.empty:
        columnas_lideres = ["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"] + [c for c in competencias if c in df.columns]
        st.dataframe(df_lideres[columnas_lideres], use_container_width=True)

    # ============================
    # Radar de competencias de liderazgo
    # ============================
    st.subheader("🌟 Evaluación de Competencias de Liderazgo (Radar)")

    if all(col in df.columns for col in competencias):
        df_comp = df_lideres.copy()
        df_comp = df_comp[df_comp["Categoría"] != "Pendiente"]

        mapping = {"No cumple": 1, "Cumple Parcialmente": 2, "Cumple": 3, "Destacado": 4, "Excepcional": 5}
        for col in competencias:
            df_comp[col] = pd.to_numeric(df_comp[col], errors="coerce").fillna(df_comp[col].map(mapping))

        promedio_clinica = df_comp[competencias].mean().round(2)

        col1, col2 = st.columns(2)
        with col1:
            dir_sel_radar = st.selectbox("Selecciona dirección", ["Ninguna"] + list(df["Dirección"].dropna().unique()))
        with col2:
            if dir_sel_radar != "Ninguna":
                lideres_disponibles = df_comp[df_comp["Dirección"] == dir_sel_radar]["Evaluado"].dropna().unique()
            else:
                lideres_disponibles = df_comp["Evaluado"].dropna().unique()
            lider_sel = st.selectbox("Selecciona un líder", ["Ninguno"] + list(lideres_disponibles))

        if dir_sel_radar != "Ninguna":
            promedio_dir = df_comp[df_comp["Dirección"] == dir_sel_radar][competencias].mean().round(2)
        else:
            promedio_dir = None

        if lider_sel != "Ninguno":
            datos_lider = df_comp[df_comp["Evaluado"] == lider_sel][competencias].mean().round(2)
        else:
            datos_lider = None

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=promedio_clinica.values, theta=competencias, fill='toself',
                                      name='Promedio clínica', line=dict(color="blue"), fillcolor="rgba(0,0,255,0.3)"))

        if promedio_dir is not None and not promedio_dir.isnull().all():
            fig.add_trace(go.Scatterpolar(r=promedio_dir.values, theta=competencias, fill='toself',
                                          name=f'Dirección: {dir_sel_radar}', line=dict(color="yellow"), fillcolor="rgba(255,255,0,0.3)"))

        if datos_lider is not None and not datos_lider.isnull().all():
            fig.add_trace(go.Scatterpolar(r=datos_lider.values, theta=competencias, fill='toself',
                                          name=f'Líder: {lider_sel}', line=dict(color="skyblue"), fillcolor="rgba(135,206,250,0.3)"))

        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    # ============================
    # Ranking de Líderes por Tendencia de Evaluación
    # ============================
    st.subheader("📈 Ranking de Líderes por Tendencia de Evaluación")

    df["Nota_num"] = pd.to_numeric(df["Nota"], errors="coerce")
    ranking_lideres = (
        df.groupby("Evaluador")["Nota_num"]
        .mean()
        .reset_index()
        .sort_values("Nota_num", ascending=False)
    )
    ranking_lideres.columns = ["Líder (Evaluador)", "Promedio de Evaluación"]

    st.dataframe(ranking_lideres, use_container_width=True)

    fig_rank = px.bar(
        ranking_lideres,
        x="Promedio de Evaluación",
        y="Líder (Evaluador)",
        orientation="h",
        text=ranking_lideres["Promedio de Evaluación"].round(2),
        title="Comparación de líderes según promedio de evaluación",
        color="Promedio de Evaluación",
        color_continuous_scale="Blues"
    )
    fig_rank.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_rank, use_container_width=True)

else:
    st.info("📂 Sube un archivo CSV para comenzar.")
