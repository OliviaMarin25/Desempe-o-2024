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

    # Filtrar solo filas con nota válida
    df_valid = df_filtered.dropna(subset=["Nota_num"])

    mejores = df_valid.sort_values("Nota_num", ascending=False).head(20)
    peores = df_valid.sort_values("Nota_num", ascending=True).head(20)

    st.markdown("### 🔝 Top 20 Mejores Evaluados")
    st.dataframe(mejores[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]], use_container_width=True)
    st.download_button(
        "⬇️ Descargar mejores (CSV)",
        mejores[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]].to_csv(index=False).encode("utf-8"),
        "top_mejores.csv",
        "text/csv"
    )

    st.markdown("### 🔻 Top 20 Peores Evaluados")
    st.dataframe(peores[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]], use_container_width=True)
    st.download_button(
        "⬇️ Descargar peores (CSV)",
        peores[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]].to_csv(index=False).encode("utf-8"),
        "top_peores.csv",
        "text/csv"
    )

else:
    st.info("📂 Sube un archivo CSV para comenzar.")
