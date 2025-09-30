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
    columnas_necesarias = [
        "Evaluado", "Cargo", "Dirección", "Área", "Sub-área", "Evaluador",
        "Liderazgo Magnético", "Formador de Personas",
        "Visión Estratégica", "Generación de Redes y Relaciones Efectivas",
        "Humildad", "Resolutividad"
    ]

    # Detectar columnas de notas y categorías por año
    nota_cols = [c for c in df.columns if "Nota" in c]
    cat_cols = [c for c in df.columns if "Categoría" in c]

    # Alias para la nota principal (2024 o la más reciente que exista)
    if "Nota 2024" in df.columns:
        df["Nota"] = df["Nota 2024"]
    elif "Nota" in df.columns:
        df["Nota"] = df["Nota"]
    else:
        st.error("⚠️ No se encontró ninguna columna de Nota (ej: 'Nota 2024').")
        st.stop()

    # Alias para categoría
    if "Categoría 2024" in df.columns:
        df["Categoría"] = df["Categoría 2024"]
    elif "Categoría" in df.columns:
        df["Categoría"] = df["Categoría"]
    else:
        st.error("⚠️ No se encontró ninguna columna de Categoría (ej: 'Categoría 2024').")
        st.stop()

    # Convertir nota a número
    df["Nota_num"] = pd.to_numeric(df["Nota"], errors="coerce")

    # Seleccionar columnas finales
    df = df[[c for c in columnas_necesarias if c in df.columns] + ["Categoría", "Nota", "Nota_num"] + nota_cols]

    # ============================
    # 1. Distribución de Categorías
    # ============================
    st.subheader("📊 Distribución de Categorías")

    conteo_categorias = df["Categoría"].value_counts().reindex(
        ["Excepcional", "Destacado", "Cumple", "Cumple Parcialmente", "No cumple", "Pendiente"],
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
        "No cumple": "red",
        "Pendiente": "lightgrey"
    }

    if opcion_grafico == "Porcentaje (%)":
        fig_cat = px.bar(
            conteo_categorias,
            x="Categoría", y="Porcentaje", color="Categoría",
            text=conteo_categorias["Porcentaje"].astype(str) + "%",
            color_discrete_map=colores,
            category_orders={"Categoría": ["Excepcional", "Destacado", "Cumple", "Cumple Parcialmente", "No cumple", "Pendiente"]}
        )
        fig_cat.update_layout(yaxis_title="Porcentaje (%)")
    else:
        fig_cat = px.bar(
            conteo_categorias,
            x="Categoría", y="Cantidad", color="Categoría",
            text=conteo_categorias["Cantidad"].astype(str),
            color_discrete_map=colores,
            category_orders={"Categoría": ["Excepcional", "Destacado", "Cumple", "Cumple Parcialmente", "No cumple", "Pendiente"]}
        )
        fig_cat.update_layout(yaxis_title="Cantidad de personas")

    st.plotly_chart(fig_cat, use_container_width=True)

    # ============================
    # 2. Evaluaciones más altas y más bajas
    # ============================
    st.subheader("🏆 Evaluaciones Destacadas")

    # 20 más altas
    top_altas = df.nlargest(20, "Nota_num")[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]].copy()
    top_altas["Acciones"] = ""  # columna editable

    st.markdown("### ⬆️ 20 evaluaciones más altas")
    edited_top_altas = st.data_editor(
        top_altas,
        use_container_width=True,
        num_rows="dynamic"
    )
    st.download_button(
        "⬇️ Descargar evaluaciones más altas (CSV)",
        edited_top_altas.to_csv(index=False).encode("utf-8"),
        "evaluaciones_mas_altas.csv",
        "text/csv"
    )

    # 20 más bajas
    top_bajas = df.nsmallest(20, "Nota_num")[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]].copy()
    top_bajas["Acciones"] = ""  # columna editable

    st.markdown("### ⬇️ 20 evaluaciones más bajas")
    edited_top_bajas = st.data_editor(
        top_bajas,
        use_container_width=True,
        num_rows="dynamic"
    )
    st.download_button(
        "⬇️ Descargar evaluaciones más bajas (CSV)",
        edited_top_bajas.to_csv(index=False).encode("utf-8"),
        "evaluaciones_mas_bajas.csv",
        "text/csv"
    )

    # ============================
    # 3. Trabajadores con cargos de Liderazgo
    # ============================
    st.subheader("🧑‍💼👩‍💼 Trabajadores con cargos de Liderazgo")

    cargos_liderazgo = df[
        df["Cargo"].str.contains("Jefe|Subgerente|Coordinador|Director|Supervisor", case=False, na=False)
    ].copy()

    st.dataframe(cargos_liderazgo[
        ["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]
    ], use_container_width=True)

    # ============================
    # 4. Radar de Competencias
    # ============================
    st.subheader("🕸️ Evaluación de Competencias de Liderazgo (Radar)")

    competencias = ["Humildad", "Resolutividad", "Liderazgo Magnético",
                    "Visión Estratégica", "Generación de Redes y Relaciones Efectivas",
                    "Formador de Personas"]

    direcciones = ["Ninguna"] + sorted(df["Dirección"].dropna().unique().tolist())
    lideres = ["Ninguno"] + sorted(df["Evaluador"].dropna().unique().tolist())

    col1, col2 = st.columns(2)
    with col1:
        seleccion_direccion = st.selectbox("Selecciona dirección", direcciones, index=0)
    with col2:
        if seleccion_direccion != "Ninguna":
            lideres_filtrados = ["Ninguno"] + sorted(
                df[df["Dirección"] == seleccion_direccion]["Evaluador"].dropna().unique().tolist()
            )
        else:
            lideres_filtrados = lideres
        seleccion_lider = st.selectbox("Selecciona un líder", lideres_filtrados, index=0)

    promedio_clinica = df[competencias].apply(pd.to_numeric, errors="coerce").mean().round(2)

    if seleccion_direccion != "Ninguna":
        promedio_direccion = df[df["Dirección"] == seleccion_direccion][competencias].apply(pd.to_numeric, errors="coerce").mean().round(2)
    else:
        promedio_direccion = None

    if seleccion_lider != "Ninguno":
        promedio_lider = df[df["Evaluador"] == seleccion_lider][competencias].apply(pd.to_numeric, errors="coerce").mean().round(2)
    else:
        promedio_lider = None

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=promedio_clinica, theta=competencias, fill="toself", name="Promedio clínica", line=dict(color="blue")
    ))
    if promedio_direccion is not None:
        fig_radar.add_trace(go.Scatterpolar(
            r=promedio_direccion, theta=competencias, fill="toself", name=f"Dirección: {seleccion_direccion}", line=dict(color="yellow")
        ))
    if promedio_lider is not None:
        fig_radar.add_trace(go.Scatterpolar(
            r=promedio_lider, theta=competencias, fill="toself", name=f"Líder: {seleccion_lider}", line=dict(color="cyan")
        ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=True)
    st.plotly_chart(fig_radar, use_container_width=True)

    # ============================
    # 5. Ranking de Líderes
    # ============================
    st.subheader("📈 Ranking de Líderes por Tendencia de Evaluación")

    ranking_lideres = (
        df.groupby("Evaluador")
        .agg(Promedio_Evaluacion=("Nota_num", "mean"),
             Cantidad_Evaluados=("Nota_num", "count"))
        .reset_index()
        .sort_values("Promedio_Evaluacion", ascending=False)
    )
    ranking_lideres["Promedio_Evaluacion"] = ranking_lideres["Promedio_Evaluacion"].round(2)

    st.dataframe(ranking_lideres.rename(columns={
        "Evaluador": "Líder (Evaluador)",
        "Promedio_Evaluacion": "Promedio de Evaluación",
        "Cantidad_Evaluados": "Cantidad de Personas Evaluadas"
    }), use_container_width=True)

    fig_rank = px.scatter(
        ranking_lideres,
        x="Promedio_Evaluacion",
        y="Cantidad_Evaluados",
        size="Cantidad_Evaluados",
        color="Promedio_Evaluacion",
        hover_name="Evaluador",
        title="Comparación de líderes: Promedio vs Cantidad de Personas Evaluadas",
        color_continuous_scale="Blues"
    )
    fig_rank.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color='DarkSlateGrey')))
    fig_rank.update_layout(
        xaxis_title="Promedio de Evaluación",
        yaxis_title="Cantidad de Personas Evaluadas"
    )
    st.plotly_chart(fig_rank, use_container_width=True)

    # ============================
    # 6. Evolución Histórica por Trabajador
    # ============================
    st.subheader("📉 Evolución histórica de desempeño (2022-2024)")

    # --- Filtros jerárquicos ---
    direcciones_hist = ["Todas"] + sorted(df["Dirección"].dropna().unique().tolist())
    seleccion_dir = st.selectbox("Selecciona Dirección", direcciones_hist, index=0)

    if seleccion_dir != "Todas":
        df_filtrado = df[df["Dirección"] == seleccion_dir]
    else:
        df_filtrado = df.copy()

    areas_hist = ["Todas"] + sorted(df_filtrado["Área"].dropna().unique().tolist())
    seleccion_area = st.selectbox("Selecciona Área", areas_hist, index=0)

    if seleccion_area != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Área"] == seleccion_area]

    subareas_hist = ["Todas"] + sorted(df_filtrado["Sub-área"].dropna().unique().tolist())
    seleccion_subarea = st.selectbox("Selecciona Sub-área", subareas_hist, index=0)

    if seleccion_subarea != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Sub-área"] == seleccion_subarea]

    trabajadores = sorted(df_filtrado["Evaluado"].dropna().unique().tolist())
    seleccion_trabajador = st.selectbox("Selecciona un trabajador", trabajadores)

    # --- Preparar datos históricos ---
    columnas_hist = [c for c in df.columns if "Nota" in c and c != "Nota_num"]

    if seleccion_trabajador and columnas_hist:
        notas_hist = df[df["Evaluado"] == seleccion_trabajador][columnas_hist].mean().round(2)

        df_hist = pd.DataFrame({
            "Año": [col.replace("Nota ", "") for col in columnas_hist],
            "Nota": notas_hist.values
        })

        fig_hist = px.line(
            df_hist,
            x="Año",
            y="Nota",
            markers=True,
            title=f"Evolución de {seleccion_trabajador}",
            range_y=[0, 5]
        )
        fig_hist.update_traces(line=dict(color="blue", width=3), marker=dict(size=10))
        fig_hist.update_layout(yaxis_title="Nota promedio")

        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("⚠️ No se encontraron columnas de notas históricas (ej: 'Nota 2022', 'Nota 2023', 'Nota 2024').")

else:
    st.error("⚠️ Sube un archivo CSV para comenzar.")
