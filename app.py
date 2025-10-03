import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =========================
# Configuración inicial
# =========================
st.set_page_config(page_title="Reporte de Desempeño 2024", layout="wide")

st.title("📊 Reporte de Desempeño - 2024")
st.sidebar.header("Carga de datos")

# Cargar archivo
uploaded_file = st.sidebar.file_uploader("Sube el archivo CSV con los datos", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Normalizar nombres de columnas
    df.columns = df.columns.str.strip()

    # =========================
    # Dropdowns de filtros
    # =========================
    st.sidebar.header("Filtros")
    direcciones = ["Todas"] + sorted(df["Dirección"].dropna().unique().tolist())
    areas = ["Todas"] + sorted(df["Área"].dropna().unique().tolist())
    subareas = ["Todas"] + sorted(df["Sub-área"].dropna().unique().tolist())

    filtro_dir = st.sidebar.selectbox("Dirección", direcciones)
    filtro_area = st.sidebar.selectbox("Área", areas)
    filtro_subarea = st.sidebar.selectbox("Sub-área", subareas)

    df_filtrado = df.copy()
    if filtro_dir != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Dirección"] == filtro_dir]
    if filtro_area != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Área"] == filtro_area]
    if filtro_subarea != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Sub-área"] == filtro_subarea]

    # =========================
    # Sección 1: Resultados 2024
    # =========================
    st.header("📌 Resultados 2024")

    if "Nota 2024" in df_filtrado.columns:
        df_filtrado["Nota_num"] = pd.to_numeric(df_filtrado["Nota 2024"], errors="coerce")

        # Distribución
        tipo_vista = st.radio("Visualizar resultados por:", ["Cantidad", "Porcentaje"], horizontal=True)
        dist = df_filtrado["Categoría 2024"].value_counts().reset_index()
        dist.columns = ["Categoría", "Cantidad"]

        colores = {
            "Excepcional": "darkgreen",
            "Destacado": "limegreen",
            "Cumple": "royalblue",
            "Cumple Parcial": "orange",
            "No Cumple": "red"
        }

        if tipo_vista == "Porcentaje":
            dist["Porcentaje"] = (dist["Cantidad"] / dist["Cantidad"].sum()) * 100
            fig = px.bar(dist, x="Categoría", y="Porcentaje", color="Categoría",
                         color_discrete_map=colores, text=dist["Porcentaje"].round(1).astype(str) + "%")
        else:
            fig = px.bar(dist, x="Categoría", y="Cantidad", color="Categoría",
                         color_discrete_map=colores, text=dist["Cantidad"])

        st.plotly_chart(fig, use_container_width=True)

        # Top / Bottom 20 con filtros adicionales
        st.subheader("🏆 Evaluaciones Destacadas")
        filtro_dir_tb = st.selectbox("Filtrar Dirección (Top/Bottom 20)", ["Todas"] + sorted(df["Dirección"].dropna().unique().tolist()))
        df_tb = df_filtrado.copy()
        if filtro_dir_tb != "Todas":
            df_tb = df_tb[df_tb["Dirección"] == filtro_dir_tb]

        top20 = df_tb.nlargest(20, "Nota_num")
        low20 = df_tb.nsmallest(20, "Nota_num")

        st.markdown("⬆️ **20 evaluaciones más altas**")
        st.dataframe(top20[["Evaluado", "Cargo", "Dirección", "Área", "Sub-área", "Nota 2024", "Categoría 2024"]])

        st.markdown("⬇️ **20 evaluaciones más bajas**")
        st.dataframe(low20[["Evaluado", "Cargo", "Dirección", "Área", "Sub-área", "Nota 2024", "Categoría 2024"]])

        # Buscar persona
        st.subheader("🔍 Buscar persona")
        persona = st.text_input("Escribe el nombre del trabajador").strip().lower()
        if persona:
            resultado = df_filtrado[df_filtrado["Evaluado"].str.lower().str.contains(persona)]
            st.dataframe(resultado)

    # =========================
    # Sección 2: Liderazgo
    # =========================
    st.header("📌 Sección 2: Liderazgo")

    competencias = ["Humildad", "Resolutividad", "Formador de Personas",
                    "Liderazgo Magnético", "Visión Estratégica", "Generación de Redes y Relaciones Efectivas"]

    if all(c in df.columns for c in competencias):
        lideres = df.copy()
        lideres["Nota2024"] = pd.to_numeric(lideres["Nota 2024"], errors="coerce")
        for c in competencias:
            lideres[c] = pd.to_numeric(lideres[c], errors="coerce")

        # Calcular promedio de competencias
        lideres["Promedio Competencias"] = lideres[competencias].mean(axis=1).round(2)

        # Ranking por Nota 2024 recibida
        ranking = lideres.sort_values("Nota2024", ascending=False).reset_index(drop=True)
        ranking["Ranking"] = ranking.index + 1
        st.dataframe(ranking[["Ranking", "Evaluado", "Nota2024"] + competencias + ["Promedio Competencias"]])

        # Top 20 gráfico
        top20_lideres = ranking.head(20)
        promedio_clinica = lideres["Nota2024"].mean()
        fig_bar = px.bar(top20_lideres, x="Evaluado", y="Nota2024", color="Nota2024",
                         color_continuous_scale="Blues", text="Nota2024")
        fig_bar.add_hline(y=promedio_clinica, line_dash="dash", line_color="red",
                          annotation_text=f"Promedio clínica: {promedio_clinica:.2f}")
        st.plotly_chart(fig_bar, use_container_width=True)

        # Radar comparativo
        st.subheader("🌟 Radar de Competencias (Comparación)")
        dir_sel = st.selectbox("Selecciona dirección", ["Todas"] + sorted(df["Dirección"].dropna().unique().tolist()))
        lider_sel = st.selectbox("Selecciona líder", sorted(df["Evaluado"].dropna().unique().tolist()))

        df_radar = df.copy()
        if dir_sel != "Todas":
            dir_avg = df_radar[df_radar["Dirección"] == dir_sel][competencias].mean()
        else:
            dir_avg = df_radar[competencias].mean()

        clinica_avg = df_radar[competencias].mean()
        lider_val = df_radar[df_radar["Evaluado"] == lider_sel][competencias].mean()

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=clinica_avg.values, theta=competencias, fill="toself", name="Clínica", line_color="darkblue"))
        fig_radar.add_trace(go.Scatterpolar(r=dir_avg.values, theta=competencias, fill="toself", name="Dirección", line_color="orange"))
        fig_radar.add_trace(go.Scatterpolar(r=lider_val.values, theta=competencias, fill="toself", name="Líder", line_color="yellow"))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])))
        st.plotly_chart(fig_radar, use_container_width=True)

    # =========================
    # Sección 3: Histórico
    # =========================
    st.header("📌 Sección 3: Desempeño histórico")

    cols_hist = ["Nota 2022", "Categoría 2022", "Nota 2023", "Categoría 2023", "Nota 2024", "Categoría 2024"]
    hist = df[["Evaluado", "Cargo", "Dirección", "Área", "Sub-área"] + cols_hist]
    st.dataframe(hist)

    # Trayectorias ascendentes
    st.subheader("📈 Mejores trayectorias")
    mejores = df[
        (df["Categoría 2024"].isin(["Excepcional", "Destacado"])) &
        (df["Categoría 2023"].isin(["Excepcional", "Destacado"])) |
        (df["Categoría 2022"].isin(["Excepcional", "Destacado"]))
    ]
    st.dataframe(mejores[["Evaluado"] + cols_hist])

    # Trayectorias descendentes
    st.subheader("📉 Trayectorias descendentes")
    peores = df[
        (df["Categoría 2024"].isin(["No Cumple", "Cumple Parcial"])) &
        (df["Categoría 2023"].isin(["No Cumple", "Cumple Parcial"])) |
        (df["Categoría 2022"].isin(["No Cumple", "Cumple Parcial"]))
    ]
    st.dataframe(peores[["Evaluado"] + cols_hist])

    # Evolución individual
    st.subheader("🌟 Evolución individual")
    trabajador_sel = st.selectbox("Selecciona trabajador", sorted(df["Evaluado"].dropna().unique().tolist()))

    if trabajador_sel:
        persona = df[df["Evaluado"] == trabajador_sel]
        if not persona.empty:
            notas = {
                "2022": persona["Nota 2022"].values[0],
                "2023": persona["Nota 2023"].values[0],
                "2024": persona["Nota 2024"].values[0]
            }
            fig_linea = px.line(x=list(notas.keys()), y=list(notas.values()), markers=True, title=f"Evolución global de {trabajador_sel}")
            st.plotly_chart(fig_linea, use_container_width=True)

            fig_comp = go.Figure()
            for c in competencias:
                vals = [
                    persona[c].values[0] if c in persona.columns else None
                ]
            st.write("Competencias individuales aún en desarrollo")
