import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Reporte de Desempeño 2024", layout="wide")

# ============================
# Subir archivo CSV
# ============================
st.title("📊 Reporte de Desempeño - 2024")

uploaded_file = st.file_uploader("📂 Sube el archivo CSV con los datos", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, delimiter=";", encoding="utf-8")
    except Exception:
        df = pd.read_csv(uploaded_file, delimiter=";", encoding="latin-1")

    # ============================
    # Preprocesamiento
    # ============================
    competencias = [
        "Humildad", "Resolutividad", "Liderazgo Magnético",
        "Visión Estratégica", "Generación de Redes y Relaciones Efectivas",
        "Formador de Personas"
    ]

    columnas_base = ["Evaluado", "Cargo", "Dirección", "Área", "Sub-área", "Evaluador"]

    # Confirmar columnas de notas y categorías históricas
    nota_cols = [c for c in df.columns if "Nota" in c]
    cat_cols = [c for c in df.columns if "Categoría" in c]

    # Alias para 2024
    df["Nota"] = df["Nota 2024"]
    df["Categoría"] = df["Categoría 2024"]
    df["Nota_num"] = pd.to_numeric(df["Nota"], errors="coerce")

    # Colores de categorías
    colores = {
        "Excepcional": "violet",
        "Destacado": "skyblue",
        "Cumple": "green",
        "Cumple Parcialmente": "yellow",
        "No cumple": "red",
        "Pendiente": "lightgrey"
    }

    # ============================
    # Sección 1: Resultados 2024
    # ============================
    st.header("📌 Sección 1: Resultados 2024")

    # Filtros jerárquicos
    direcciones = ["Todas"] + sorted(df["Dirección"].dropna().unique().tolist())
    seleccion_dir = st.selectbox("Selecciona Dirección (Resultados)", direcciones, index=0)

    df_filtrado = df.copy()
    if seleccion_dir != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Dirección"] == seleccion_dir]

    areas = ["Todas"] + sorted(df_filtrado["Área"].dropna().unique().tolist())
    seleccion_area = st.selectbox("Selecciona Área (Resultados)", areas, index=0)

    if seleccion_area != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Área"] == seleccion_area]

    subareas = ["Todas"] + sorted(df_filtrado["Sub-área"].dropna().unique().tolist())
    seleccion_subarea = st.selectbox("Selecciona Sub-área (Resultados)", subareas, index=0)

    if seleccion_subarea != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Sub-área"] == seleccion_subarea]

    # Distribución de categorías
    st.subheader("📊 Distribución de Categorías 2024")
    conteo_categorias = df_filtrado["Categoría 2024"].value_counts().reindex(
        ["Excepcional", "Destacado", "Cumple", "Cumple Parcialmente", "No cumple", "Pendiente"],
        fill_value=0
    ).reset_index()
    conteo_categorias.columns = ["Categoría", "Cantidad"]
    total = conteo_categorias["Cantidad"].sum()
    conteo_categorias["Porcentaje"] = (conteo_categorias["Cantidad"] / total * 100).round(1)

    opcion_grafico = st.radio("Ver gráfico por:", ["Porcentaje (%)", "Cantidad (N personas)"], horizontal=True)
    if opcion_grafico == "Porcentaje (%)":
        fig_cat = px.bar(conteo_categorias, x="Categoría", y="Porcentaje", color="Categoría",
                         text=conteo_categorias["Porcentaje"].astype(str) + "%",
                         color_discrete_map=colores)
    else:
        fig_cat = px.bar(conteo_categorias, x="Categoría", y="Cantidad", color="Categoría",
                         text=conteo_categorias["Cantidad"].astype(str),
                         color_discrete_map=colores)
    st.plotly_chart(fig_cat, use_container_width=True)

    # Top 20 ± con filtros independientes
    st.subheader("🏆 Mejores y Peores Evaluados 2024")
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_dir = st.selectbox("Filtrar Dirección (Top 20)", direcciones, index=0, key="dir_top")
    df_top = df.copy()
    if filtro_dir != "Todas":
        df_top = df_top[df_top["Dirección"] == filtro_dir]

    with col2:
        filtro_area = st.selectbox("Filtrar Área (Top 20)", ["Todas"] + sorted(df_top["Área"].dropna().unique().tolist()), index=0, key="area_top")
    if filtro_area != "Todas":
        df_top = df_top[df_top["Área"] == filtro_area]

    with col3:
        filtro_sub = st.selectbox("Filtrar Sub-área (Top 20)", ["Todas"] + sorted(df_top["Sub-área"].dropna().unique().tolist()), index=0, key="sub_top")
    if filtro_sub != "Todas":
        df_top = df_top[df_top["Sub-área"] == filtro_sub]

    top_altas = df_top.nlargest(20, "Nota_num")[["Evaluado", "Cargo", "Evaluador", "Categoría 2024", "Nota 2024"]]
    top_bajas = df_top.nsmallest(20, "Nota_num")[["Evaluado", "Cargo", "Evaluador", "Categoría 2024", "Nota 2024"]]
    st.markdown("### ⬆️ 20 evaluaciones más altas")
    st.data_editor(top_altas, use_container_width=True)
    st.markdown("### ⬇️ 20 evaluaciones más bajas")
    st.data_editor(top_bajas, use_container_width=True)

    # Buscador
    st.subheader("🔍 Buscar persona")
    buscador = st.text_input("Escribe el nombre del trabajador")
    if buscador:
        resultado = df[df["Evaluado"].str.contains(buscador, case=False, na=False)]
        st.dataframe(resultado[["Evaluado", "Cargo", "Dirección", "Área", "Sub-área", "Evaluador",
                                "Nota 2024", "Categoría 2024"]], use_container_width=True)

    # ============================
    # Sección 2: Liderazgo
    # ============================
    st.header("📌 Sección 2: Liderazgo")

    # Ranking líderes por Nota 2024 recibida
    st.subheader("📈 Ranking de Líderes (Nota 2024 recibida)")
    ranking = (df.groupby("Evaluador")
                 .agg(Nota2024=("Nota_num", "mean"))
                 .reset_index()
                 .sort_values("Nota2024", ascending=False))
    ranking["Ranking"] = range(1, len(ranking) + 1)

    # Agregar competencias
    comp_cols = [c for c in df.columns if c in competencias]
    lideres_comp = df.groupby("Evaluador")[comp_cols].mean().reset_index().round(2)
    ranking = ranking.merge(lideres_comp, on="Evaluador", how="left")
    ranking["Promedio Competencias"] = ranking[competencias].mean(axis=1).round(2)

    st.dataframe(ranking[["Ranking", "Evaluador", "Nota2024"] + competencias + ["Promedio Competencias"]],
                 use_container_width=True)

    # Radar comparativo
    st.subheader("🕸️ Radar de Competencias (Comparación)")
    direcciones = ["Ninguna"] + sorted(df["Dirección"].dropna().unique().tolist())
    lideres = ["Ninguno"] + sorted(df["Evaluador"].dropna().unique().tolist())
    col1, col2 = st.columns(2)
    with col1:
        seleccion_direccion = st.selectbox("Selecciona dirección", direcciones, index=0)
    with col2:
        if seleccion_direccion != "Ninguna":
            lideres_filtrados = ["Ninguno"] + sorted(df[df["Dirección"] == seleccion_direccion]["Evaluador"].dropna().unique().tolist())
        else:
            lideres_filtrados = lideres
        seleccion_lider = st.selectbox("Selecciona líder", lideres_filtrados, index=0)

    promedio_clinica = df[competencias].apply(pd.to_numeric, errors="coerce").mean().round(2)
    promedio_direccion = df[df["Dirección"] == seleccion_direccion][competencias].apply(pd.to_numeric, errors="coerce").mean().round(2) if seleccion_direccion != "Ninguna" else None
    promedio_lider = df[df["Evaluador"] == seleccion_lider][competencias].apply(pd.to_numeric, errors="coerce").mean().round(2) if seleccion_lider != "Ninguno" else None

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=promedio_clinica, theta=competencias, fill="toself", name="Clínica", line=dict(color="darkblue")))
    if promedio_direccion is not None:
        fig_radar.add_trace(go.Scatterpolar(r=promedio_direccion, theta=competencias, fill="toself", name=f"Dirección: {seleccion_direccion}", line=dict(color="orange")))
    if promedio_lider is not None:
        fig_radar.add_trace(go.Scatterpolar(r=promedio_lider, theta=competencias, fill="toself", name=f"Líder: {seleccion_lider}", line=dict(color="yellow")))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=True)
    st.plotly_chart(fig_radar, use_container_width=True)

    # Tendencia de evaluación (evaluador a su equipo)
    st.subheader("📊 Tendencia de Evaluación (líder → equipo)")
    tendencia = (df.groupby("Evaluador")
                   .agg(Promedio_Entregado=("Nota_num", "mean"),
                        Cantidad_Evaluados=("Nota_num", "count"))
                   .reset_index())
    tendencia["Promedio_Entregado"] = tendencia["Promedio_Entregado"].round(2)
    st.dataframe(tendencia, use_container_width=True)

    fig_tend = px.scatter(tendencia, x="Promedio_Entregado", y="Cantidad_Evaluados", size="Cantidad_Evaluados",
                          color="Promedio_Entregado", hover_name="Evaluador")
    st.plotly_chart(fig_tend, use_container_width=True)

    # ============================
    # Sección 3: Desempeño Histórico
    # ============================
    st.header("📌 Sección 3: Desempeño Histórico")

    # Tabla notas + categorías históricas
    st.subheader("📋 Notas y Categorías Históricas")
    historico_cols = []
    for year in ["2022", "2023", "2024"]:
        if f"Nota {year}" in df.columns and f"Categoría {year}" in df.columns:
            historico_cols += [f"Nota {year}", f"Categoría {year}"]
    st.dataframe(df[["Evaluado"] + historico_cols], use_container_width=True)

    # Mejores trayectorias
    st.subheader("🌟 Mejores trayectorias (≥2 años alto, 2024 alto)")
    mejores = df[df["Categoría 2024"].isin(["Excepcional", "Destacado"])].copy()
    mejores["Alta_count"] = (df[[c for c in cat_cols if "Categoría" in c]].isin(["Excepcional", "Destacado"]).sum(axis=1))
    mejores = mejores[mejores["Alta_count"] >= 2]
    st.dataframe(mejores[["Evaluado"] + historico_cols], use_container_width=True)

    # Trayectorias descendentes
    st.subheader("⚠️ Trayectorias descendentes (≥2 años bajos, 2024 bajo)")
    peores = df[df["Categoría 2024"].isin(["No cumple", "Cumple Parcialmente"])].copy()
    peores["Bajo_count"] = (df[[c for c in cat_cols if "Categoría" in c]].isin(["No cumple", "Cumple Parcialmente"]).sum(axis=1))
    peores = peores[peores["Bajo_count"] >= 2]
    st.dataframe(peores[["Evaluado"] + historico_cols], use_container_width=True)

    # Evolución individual
    st.subheader("📈 Evolución individual")
    trabajador = st.selectbox("Selecciona trabajador", sorted(df["Evaluado"].dropna().unique().tolist()))
    if trabajador:
        columnas_hist = [c for c in nota_cols if "Nota" in c]
        df[columnas_hist] = df[columnas_hist].apply(pd.to_numeric, errors="coerce")
        notas_hist = df[df["Evaluado"] == trabajador][columnas_hist].iloc[0]
        df_hist = pd.DataFrame({"Año": [c.replace("Nota ", "") for c in columnas_hist],
                                "Nota": notas_hist.values.round(2)})
        fig_hist = px.line(df_hist, x="Año", y="Nota", markers=True,
                           title=f"Evolución global de {trabajador}", range_y=[0, 5])
        st.plotly_chart(fig_hist, use_container_width=True)

        # Competencias históricas
        comp_hist = [c for c in df.columns if any(comp in c for comp in competencias)]
        if comp_hist:
            st.subheader("🕸️ Evolución de Competencias por Año")
            df_comp = df[df["Evaluado"] == trabajador][comp_hist]
            df_comp = df_comp.apply(pd.to_numeric, errors="coerce")
            df_comp = df_comp.melt(var_name="Competencia", value_name="Nota")
            fig_comp = px.line(df_comp, x="Competencia", y="Nota", color="Competencia", markers=True)
            st.plotly_chart(fig_comp, use_container_width=True)

else:
    st.error("⚠️ Sube un archivo CSV para comenzar.")
