import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Reporte de Desempeño - 2024", layout="wide")

st.title("📊 Reporte de Desempeño - 2024")

# ============================
# Subir archivo CSV
# ============================
uploaded_file = st.file_uploader("📂 Sube el archivo CSV con los datos", type=["csv"])

if uploaded_file is not None:
    # Intentar distintas configuraciones de lectura
    try:
        df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8", engine="python")
    except:
        try:
            df = pd.read_csv(uploaded_file, sep=",", encoding="latin-1", engine="python")
        except:
            df = pd.read_csv(uploaded_file, sep="\t", encoding="utf-8", engine="python")

    # Normalizar columnas
    df.columns = df.columns.str.strip()

    # ============================
    # Filtros dinámicos
    # ============================
    st.sidebar.header("Filtros")
    direcciones = ["Todas"] + sorted(df["Dirección"].dropna().unique().tolist())
    areas = ["Todas"] + sorted(df["Área"].dropna().unique().tolist())
    subareas = ["Todas"] + sorted(df["Sub-área"].dropna().unique().tolist())

    seleccion_direccion = st.sidebar.selectbox("Dirección", direcciones, index=0)
    seleccion_area = st.sidebar.selectbox("Área", areas, index=0)
    seleccion_subarea = st.sidebar.selectbox("Sub-área", subareas, index=0)

    df_filtrado = df.copy()
    if seleccion_direccion != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Dirección"] == seleccion_direccion]
    if seleccion_area != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Área"] == seleccion_area]
    if seleccion_subarea != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Sub-área"] == seleccion_subarea]

    # ============================
    # Sección 1: Resultados 2024
    # ============================
    st.header("📌 Resultados 2024")

    df_2024 = df_filtrado.copy()
    df_2024["Nota_num"] = pd.to_numeric(df_2024["Nota 2024"], errors="coerce")

    conteo_categorias = df_2024["Categoría 2024"].value_counts().reindex(
        ["Excepcional", "Destacado", "Cumple", "Cumple Parcialmente", "No Cumple", "Pendiente"],
        fill_value=0
    ).reset_index()
    conteo_categorias.columns = ["Categoría", "Cantidad"]
    total = conteo_categorias["Cantidad"].sum()
    conteo_categorias["Porcentaje"] = (conteo_categorias["Cantidad"] / total * 100).round(1)

    opcion_grafico = st.radio("Ver gráfico por:", ["Porcentaje (%)", "Cantidad (N personas)"], horizontal=True)

    colores = {
        "Excepcional": "violet",
        "Destacado": "skyblue",
        "Cumple": "green",
        "Cumple Parcialmente": "yellow",
        "No Cumple": "red",
        "Pendiente": "lightgrey"
    }

    if opcion_grafico == "Porcentaje (%)":
        fig_cat = px.bar(
            conteo_categorias,
            x="Categoría", y="Porcentaje", color="Categoría",
            text=conteo_categorias["Porcentaje"].astype(str) + "%",
            color_discrete_map=colores
        )
        fig_cat.update_layout(yaxis_title="Porcentaje (%)")
    else:
        fig_cat = px.bar(
            conteo_categorias,
            x="Categoría", y="Cantidad", color="Categoría",
            text=conteo_categorias["Cantidad"].astype(str),
            color_discrete_map=colores
        )
        fig_cat.update_layout(yaxis_title="Cantidad de personas")

    st.plotly_chart(fig_cat, use_container_width=True)

    # Top 20 y Bottom 20 filtrables
    st.subheader("🏆 Evaluaciones Destacadas")
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_dir_tb = st.selectbox("Dirección (Top/Bottom)", ["Todas"] + sorted(df["Dirección"].dropna().unique()), index=0)
    with col2:
        filtro_area_tb = st.selectbox("Área (Top/Bottom)", ["Todas"] + sorted(df["Área"].dropna().unique()), index=0)
    with col3:
        filtro_sub_tb = st.selectbox("Sub-área (Top/Bottom)", ["Todas"] + sorted(df["Sub-área"].dropna().unique()), index=0)

    df_tb = df_2024.copy()
    if filtro_dir_tb != "Todas":
        df_tb = df_tb[df_tb["Dirección"] == filtro_dir_tb]
    if filtro_area_tb != "Todas":
        df_tb = df_tb[df_tb["Área"] == filtro_area_tb]
    if filtro_sub_tb != "Todas":
        df_tb = df_tb[df_tb["Sub-área"] == filtro_sub_tb]

    top_20 = df_tb.nlargest(20, "Nota_num")[["Evaluado", "Cargo", "Evaluador", "Categoría 2024", "Nota 2024"]]
    bottom_20 = df_tb.nsmallest(20, "Nota_num")[["Evaluado", "Cargo", "Evaluador", "Categoría 2024", "Nota 2024"]]

    st.markdown("### ⬆️ 20 evaluaciones más altas")
    st.dataframe(top_20, use_container_width=True)

    st.markdown("### ⬇️ 20 evaluaciones más bajas")
    st.dataframe(bottom_20, use_container_width=True)

    # ============================
    # Sección 2: Liderazgo
    # ============================
    st.header("📌 Sección 2: Liderazgo")

    competencias = ["Humildad", "Resolutividad", "Formador de Personas",
                    "Liderazgo Magnético", "Visión Estratégica",
                    "Generación de Redes y Relaciones Efectivas"]

    df_lideres = df_2024[df_2024["Cargo"].str.contains("Jefe|Subgerente|Coordinador|Director|Supervisor", case=False, na=False)].copy()

    # Ranking por nota 2024 recibida
    ranking_lideres = (
        df_lideres.groupby("Evaluado")
        .agg(Nota2024=("Nota_num", "mean"),
             **{comp: (comp, "mean") for comp in competencias})
        .reset_index()
    )
    ranking_lideres["Promedio Competencias"] = ranking_lideres[competencias].mean(axis=1)
    ranking_lideres = ranking_lideres.sort_values("Nota2024", ascending=False).reset_index(drop=True)
    ranking_lideres.index += 1
    ranking_lideres.insert(0, "Ranking", ranking_lideres.index)

    st.subheader("📈 Ranking de Líderes (Nota 2024 recibida)")
    st.dataframe(ranking_lideres, use_container_width=True)

    # Radar comparativo (SOLO líderes)
    st.subheader("🕸️ Radar de Competencias (Comparación)")

    col1, col2 = st.columns(2)
    with col1:
        seleccion_direccion = st.selectbox("Selecciona dirección", ["Todas"] + sorted(df_2024["Dirección"].dropna().unique()))
    with col2:
        filtro_lideres = df_2024[df_2024["Cargo"].str.contains("Jefe|Subgerente|Coordinador|Director|Supervisor", case=False, na=False)]
        if seleccion_direccion != "Todas":
            lideres_filtrados = ["Ninguno"] + sorted(
                filtro_lideres[filtro_lideres["Dirección"] == seleccion_direccion]["Evaluado"].dropna().unique().tolist()
            )
        else:
            lideres_filtrados = ["Ninguno"] + sorted(filtro_lideres["Evaluado"].dropna().unique().tolist())
        seleccion_lider = st.selectbox("Selecciona un líder", lideres_filtrados)

    promedio_clinica = df_2024[competencias].apply(pd.to_numeric, errors="coerce").mean()
    if seleccion_direccion != "Todas":
        promedio_direccion = df_2024[df_2024["Dirección"] == seleccion_direccion][competencias].apply(pd.to_numeric, errors="coerce").mean()
    else:
        promedio_direccion = None
    if seleccion_lider != "Ninguno":
        promedio_lider = df_2024[df_2024["Evaluado"] == seleccion_lider][competencias].apply(pd.to_numeric, errors="coerce").mean()
    else:
        promedio_lider = None

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=promedio_clinica, theta=competencias, fill="toself", name="Clínica", line=dict(color="darkblue")))
    if promedio_direccion is not None:
        fig_radar.add_trace(go.Scatterpolar(r=promedio_direccion, theta=competencias, fill="toself", name=f"Dirección: {seleccion_direccion}", line=dict(color="orange")))
    if promedio_lider is not None:
        fig_radar.add_trace(go.Scatterpolar(r=promedio_lider, theta=competencias, fill="toself", name=f"Líder: {seleccion_lider}", line=dict(color="yellow")))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=True)
    st.plotly_chart(fig_radar, use_container_width=True)

    # ============================
    # Sección 3: Desempeño Histórico
    # ============================
    st.header("📌 Sección 3: Desempeño Histórico")

    columnas_hist = ["Nota 2022", "Categoría 2022", "Nota 2023", "Categoría 2023", "Nota 2024", "Categoría 2024"]
    st.subheader("📋 Tabla histórica")
    st.dataframe(df_filtrado[["Evaluado", "Cargo", "Dirección", "Área", "Sub-área"] + columnas_hist], use_container_width=True)

    # Trayectorias destacadas
    st.subheader("🌟 Mejores trayectorias")
    mejores_tray = df_filtrado[
        (df_filtrado["Categoría 2024"].isin(["Excepcional", "Destacado"])) &
        (df_filtrado[["Categoría 2022", "Categoría 2023"]].isin(["Excepcional", "Destacado"]).sum(axis=1) >= 1)
    ]
    st.dataframe(mejores_tray[["Evaluado"] + columnas_hist], use_container_width=True)

    st.subheader("⚠️ Trayectorias descendentes")
    malas_tray = df_filtrado[
        (df_filtrado["Categoría 2024"].isin(["No Cumple", "Cumple Parcialmente"])) &
        (df_filtrado[["Categoría 2022", "Categoría 2023"]].isin(["No Cumple", "Cumple Parcialmente"]).sum(axis=1) >= 1)
    ]
    st.dataframe(malas_tray[["Evaluado"] + columnas_hist], use_container_width=True)

    # Evolución individual
    st.subheader("📈 Evolución individual")
    trabajador = st.selectbox("Selecciona trabajador", ["Ninguno"] + sorted(df_filtrado["Evaluado"].dropna().unique().tolist()))
    if trabajador != "Ninguno":
        notas_hist = df_filtrado[df_filtrado["Evaluado"] == trabajador][["Nota 2022", "Nota 2023", "Nota 2024"]].T
        notas_hist.columns = ["Nota"]
        notas_hist["Año"] = [2022, 2023, 2024]
        fig_ind = px.line(notas_hist, x="Año", y="Nota", markers=True, title=f"Evolución global de {trabajador}")
        fig_ind.update_yaxes(range=[0, 5])
        st.plotly_chart(fig_ind, use_container_width=True)

        st.subheader("🌐 Evolución de Competencias por Año")
        competencias_hist = df_filtrado[df_filtrado["Evaluado"] == trabajador][competencias].T
        competencias_hist.columns = [trabajador]
        competencias_hist["Competencia"] = competencias_hist.index
        fig_comp = px.bar(competencias_hist, x="Competencia", y=trabajador, title=f"Evolución de competencias - {trabajador}")
        fig_comp.update_yaxes(range=[0, 5])
        st.plotly_chart(fig_comp, use_container_width=True)

else:
    st.info("📂 Sube un archivo CSV para comenzar.")
