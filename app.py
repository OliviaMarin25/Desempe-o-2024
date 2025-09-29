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
        "Categoría", "Nota", "Liderazgo Magnético", "Formador de Personas",
        "Visión Estratégica", "Generación de Redes y Relaciones Efectivas",
        "Humildad", "Resolutividad"
    ]
    df = df[[c for c in columnas_necesarias if c in df.columns]]

    df["Nota_num"] = pd.to_numeric(df["Nota"], errors="coerce")

    # ============================
    # Filtros
    # ============================
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

    df_filtered = df.copy()
    if seleccion_direccion != "Ninguna":
        df_filtered = df_filtered[df_filtered["Dirección"] == seleccion_direccion]
    if seleccion_lider != "Ninguno":
        df_filtered = df_filtered[df_filtered["Evaluador"] == seleccion_lider]

    # ============================
    # Distribución de Categorías
    # ============================
    st.subheader("📊 Distribución de Categorías")

    conteo_categorias = df_filtered["Categoría"].value_counts().reindex(
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
            category_orders={"Categoría": ["Excepcional", "Destacado", "Cumple", "Cumple Parcialmente", "No cumple", "Pendiente"]}
        )
        fig_cat.update_layout(yaxis_title="Porcentaje (%)")
    else:
        fig_cat = px.bar(
            conteo_categorias,
            x="Categoría", y="Cantidad", color="Categoría",
            text=conteo_categorias["Cantidad"].astype(str),
            category_orders={"Categoría": ["Excepcional", "Destacado", "Cumple", "Cumple Parcialmente", "No cumple", "Pendiente"]}
        )
        fig_cat.update_layout(yaxis_title="Cantidad de personas")

    st.plotly_chart(fig_cat, use_container_width=True)

    # ============================
    # Radar de Competencias
    # ============================
    st.subheader("🕸️ Evaluación de Competencias de Liderazgo (Radar)")

    competencias = ["Humildad", "Resolutividad", "Liderazgo Magnético",
                    "Visión Estratégica", "Generación de Redes y Relaciones Efectivas",
                    "Formador de Personas"]

    promedio_clinica = df[competencias].apply(pd.to_numeric, errors="coerce").mean()

    if seleccion_direccion != "Ninguna":
        promedio_direccion = df[df["Dirección"] == seleccion_direccion][competencias].apply(pd.to_numeric, errors="coerce").mean()
    else:
        promedio_direccion = None

    if seleccion_lider != "Ninguno":
        promedio_lider = df[df["Evaluador"] == seleccion_lider][competencias].apply(pd.to_numeric, errors="coerce").mean()
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
    # Trabajadores con cargos de Liderazgo
    # ============================
    st.subheader("🧑‍💼👩‍💼 Trabajadores con cargos de Liderazgo")

    cargos_liderazgo = df[
        df["Cargo"].str.contains("Jefe|Subgerente|Coordinador|Director|Supervisor", case=False, na=False)
    ].copy()

    st.dataframe(cargos_liderazgo[
        ["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"] + competencias
    ], use_container_width=True)

    # ============================
    # Mejores y Peores Evaluados
    # ============================
    st.subheader("🏆 Mejores y Peores Evaluados")

    top_mejores = df.nlargest(20, "Nota_num")[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]]
    top_peores = df.nsmallest(20, "Nota_num")[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]]

    st.markdown("### ⬆️ Top 20 Mejores Evaluados")
    st.dataframe(top_mejores, use_container_width=True)
    st.download_button("⬇️ Descargar mejores (CSV)", top_mejores.to_csv(index=False).encode("utf-8"), "mejores.csv", "text/csv")

    st.markdown("### ⬇️ Top 20 Peores Evaluados")
    st.dataframe(top_peores, use_container_width=True)
    st.download_button("⬇️ Descargar peores (CSV)", top_peores.to_csv(index=False).encode("utf-8"), "peores.csv", "text/csv")

    # ============================
    # Ranking de Líderes por Tendencia de Evaluación (mejorado)
    # ============================
    st.subheader("📈 Ranking de Líderes por Tendencia de Evaluación")

    ranking_lideres = (
        df.groupby("Evaluador")
        .agg(Promedio_Evaluacion=("Nota_num", "mean"),
             Cantidad_Evaluados=("Nota_num", "count"))
        .reset_index()
        .sort_values("Promedio_Evaluacion", ascending=False)
    )

    # Mostrar tabla con promedio + cantidad
    st.dataframe(ranking_lideres.rename(columns={
        "Evaluador": "Líder (Evaluador)",
        "Promedio_Evaluacion": "Promedio de Evaluación",
        "Cantidad_Evaluados": "Cantidad de Personas Evaluadas"
    }), use_container_width=True)

    # Scatter plot (comparación)
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

else:
    st.error("⚠️ Sube un archivo CSV para comenzar.")
