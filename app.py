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

    # Detectar columnas de notas y categorías
    nota_cols = [c for c in df.columns if "Nota" in c]
    cat_cols = [c for c in df.columns if "Categoría" in c]

    # Alias para 2024
    if "Nota 2024" in df.columns:
        df["Nota"] = df["Nota 2024"]
    elif "Nota" in df.columns:
        df["Nota"] = df["Nota"]
    else:
        st.error("⚠️ No se encontró ninguna columna de Nota (ej: 'Nota 2024').")
        st.stop()

    if "Categoría 2024" in df.columns:
        df["Categoría"] = df["Categoría 2024"]
    elif "Categoría" in df.columns:
        df["Categoría"] = df["Categoría"]
    else:
        st.error("⚠️ No se encontró ninguna columna de Categoría (ej: 'Categoría 2024').")
        st.stop()

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
    seleccion_dir = st.selectbox("Selecciona Dirección", direcciones, index=0)

    df_filtrado = df.copy()
    if seleccion_dir != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Dirección"] == seleccion_dir]

    areas = ["Todas"] + sorted(df_filtrado["Área"].dropna().unique().tolist())
    seleccion_area = st.selectbox("Selecciona Área", areas, index=0)

    if seleccion_area != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Área"] == seleccion_area]

    subareas = ["Todas"] + sorted(df_filtrado["Sub-área"].dropna().unique().tolist())
    seleccion_subarea = st.selectbox("Selecciona Sub-área", subareas, index=0)

    if seleccion_subarea != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Sub-área"] == seleccion_subarea]

    # Distribución de categorías
    st.subheader("📊 Distribución de Categorías")
    conteo_categorias = df_filtrado["Categoría"].value_counts().reindex(
        ["Excepcional", "Destacado", "Cumple", "Cumple Parcialmente", "No cumple", "Pendiente"],
        fill_value=0
    ).reset_index()
    conteo_categorias.columns = ["Categoría", "Cantidad"]
    total = conteo_categorias["Cantidad"].sum()
    conteo_categorias["Porcentaje"] = (conteo_categorias["Cantidad"] / total * 100).round(1)

    opcion_grafico = st.radio("Ver gráfico por:", ["Porcentaje (%)", "Cantidad (N personas)"], horizontal=True)
    if opcion_grafico == "Porcentaje (%)":
        fig_cat = px.bar(
            conteo_categorias,
            x="Categoría", y="Porcentaje", color="Categoría",
            text=conteo_categorias["Porcentaje"].astype(str) + "%",
            color_discrete_map=colores
        )
    else:
        fig_cat = px.bar(
            conteo_categorias,
            x="Categoría", y="Cantidad", color="Categoría",
            text=conteo_categorias["Cantidad"].astype(str),
            color_discrete_map=colores
        )
    st.plotly_chart(fig_cat, use_container_width=True)

    # Top 20 más altas y bajas
    st.subheader("🏆 Mejores y Peores Evaluados")
    top_altas = df_filtrado.nlargest(20, "Nota_num")[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]].copy()
    top_bajas = df_filtrado.nsmallest(20, "Nota_num")[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]].copy()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ⬆️ 20 evaluaciones más altas")
        st.data_editor(top_altas, use_container_width=True)
    with col2:
        st.markdown("### ⬇️ 20 evaluaciones más bajas")
        st.data_editor(top_bajas, use_container_width=True)

    # Buscador de persona
    st.subheader("🔍 Buscar persona")
    buscador = st.text_input("Escribe el nombre del trabajador")
    if buscador:
        resultado = df[df["Evaluado"].str.contains(buscador, case=False, na=False)]
        st.dataframe(resultado[["Evaluado", "Cargo", "Dirección", "Área", "Sub-área", "Evaluador", "Nota", "Categoría"]],
                     use_container_width=True)

    # ============================
    # Sección 2: Liderazgo
    # ============================
    st.header("📌 Sección 2: Liderazgo")

    # Tabla de cargos de liderazgo
    st.subheader("👔 Personas con cargos de Liderazgo")
    cargos_liderazgo = df[df["Cargo"].str.contains("Jefe|Subgerente|Coordinador|Director|Supervisor", case=False, na=False)].copy()
    st.dataframe(cargos_liderazgo[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]], use_container_width=True)

    # Radar comparativo
    st.subheader("🕸️ Radar de Competencias de Liderazgo")
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
        seleccion_lider = st.selectbox("Selecciona un líder", lideres_filtrados, index=0)

    promedio_clinica = df[competencias].apply(pd.to_numeric, errors="coerce").mean().round(2)
    promedio_direccion = df[df["Dirección"] == seleccion_direccion][competencias].apply(pd.to_numeric, errors="coerce").mean().round(2) if seleccion_direccion != "Ninguna" else None
    promedio_lider = df[df["Evaluador"] == seleccion_lider][competencias].apply(pd.to_numeric, errors="coerce").mean().round(2) if seleccion_lider != "Ninguno" else None

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=promedio_clinica, theta=competencias, fill="toself", name="Promedio clínica"))
    if promedio_direccion is not None:
        fig_radar.add_trace(go.Scatterpolar(r=promedio_direccion, theta=competencias, fill="toself", name=f"Dirección: {seleccion_direccion}"))
    if promedio_lider is not None:
        fig_radar.add_trace(go.Scatterpolar(r=promedio_lider, theta=competencias, fill="toself", name=f"Líder: {seleccion_lider}"))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=True)
    st.plotly_chart(fig_radar, use_container_width=True)

    # Ranking líderes
    st.subheader("📈 Ranking de Líderes por Tendencia de Evaluación")
    ranking_lideres = df.groupby("Evaluador").agg(Promedio_Evaluacion=("Nota_num", "mean"),
                                                 Cantidad_Evaluados=("Nota_num", "count")).reset_index()
    ranking_lideres["Promedio_Evaluacion"] = ranking_lideres["Promedio_Evaluacion"].round(2)
    st.dataframe(ranking_lideres, use_container_width=True)

    fig_rank = px.scatter(ranking_lideres, x="Promedio_Evaluacion", y="Cantidad_Evaluados",
                          size="Cantidad_Evaluados", color="Promedio_Evaluacion", hover_name="Evaluador")
    st.plotly_chart(fig_rank, use_container_width=True)

    # ============================
    # Sección 3: Desempeño Histórico
    # ============================
    st.header("📌 Sección 3: Desempeño Histórico")

    # Tabla general
    st.subheader("📋 Notas históricas")
    st.dataframe(df[["Evaluado"] + nota_cols], use_container_width=True)

    # Mejores trayectorias
    st.subheader("🌟 Mejores trayectorias (2022-2024)")
    mejores = df[df["Categoría"].isin(["Excepcional", "Destacado"])]
    st.dataframe(mejores[["Evaluado", "Nota", "Categoría"]], use_container_width=True)

    # Peores trayectorias
    st.subheader("⚠️ Peores trayectorias (2022-2024)")
    peores = df[df["Categoría"].isin(["Cumple Parcialmente", "No cumple"])]
    st.dataframe(peores[["Evaluado", "Nota", "Categoría"]], use_container_width=True)

    # Evolución individual
    st.subheader("📈 Evolución individual por trabajador (nota global y competencias)")
    trabajadores = sorted(df["Evaluado"].dropna().unique().tolist())
    seleccion_trabajador = st.selectbox("Selecciona trabajador", trabajadores)
    if seleccion_trabajador:
        columnas_hist = [c for c in df.columns if "Nota" in c and c != "Nota_num"]
        df[columnas_hist] = df[columnas_hist].apply(lambda col: pd.to_numeric(col, errors="coerce"))
        notas_hist = df[df["Evaluado"] == seleccion_trabajador][columnas_hist].iloc[0]
        df_hist = pd.DataFrame({"Año": [col.replace("Nota ", "") for col in columnas_hist],
                                "Nota": notas_hist.values.round(2)})
        fig_hist = px.line(df_hist, x="Año", y="Nota", markers=True, title=f"Evolución global de {seleccion_trabajador}", range_y=[0, 5])
        st.plotly_chart(fig_hist, use_container_width=True)

        # Competencias por año
        competencias_hist = [c for c in df.columns if any(comp in c for comp in competencias)]
        if competencias_hist:
            st.subheader("🕸️ Evolución de competencias")
            df_comp = df[df["Evaluado"] == seleccion_trabajador][competencias_hist]
            df_comp = df_comp.apply(pd.to_numeric, errors="coerce")
            df_comp = df_comp.melt(var_name="Competencia", value_name="Nota")
            fig_comp = px.line(df_comp, x="Competencia", y="Nota", color="Competencia", markers=True)
            st.plotly_chart(fig_comp, use_container_width=True)

else:
    st.error("⚠️ Sube un archivo CSV para comenzar.")
