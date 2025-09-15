import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard Desempeño Piton", page_icon="📊", layout="wide")
st.title("📊 Reporte de Desempeño - Piton")

# ============================
# Carga de datos
# ============================
st.sidebar.header("⚙️ Configuración de datos")

archivo_subido = st.sidebar.file_uploader("Sube tu archivo CSV (separador ;)", type=["csv"])

# Archivo por defecto en el repo
ARCHIVO_REPO = "Desempeño-Piton.csv"

try:
    if archivo_subido is not None:
        df = pd.read_csv(archivo_subido, sep=";", encoding="utf-8", engine="python")
        st.sidebar.success("✅ Usando archivo cargado por el usuario")
    else:
        df = pd.read_csv(ARCHIVO_REPO, sep=";", encoding="utf-8", engine="python")
        st.sidebar.info("ℹ️ Usando archivo por defecto del repo")

    st.success(f"Datos cargados: {df.shape[0]} filas × {df.shape[1]} columnas")

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
    if "Desempeño" in df.columns:
        c4.metric("Promedio Desempeño", round(df["Desempeño"].mean(), 2))

    # ============================
    # Filtros
    # ============================
    st.sidebar.subheader("🔎 Filtros")
    filtros = {}
    for col in ["Dirección", "Área", "Sub-área", "Evaluador"]:
        if col in df.columns:
            valores = sorted(df[col].dropna().unique())
            seleccionados = st.sidebar.multiselect(f"{col}", valores, default=[])
            if seleccionados:
                filtros[col] = seleccionados

    # Aplicar filtros
    df_filtrado = df.copy()
    for col, valores in filtros.items():
        df_filtrado = df_filtrado[df_filtrado[col].isin(valores)]

    st.write(f"**Registros filtrados:** {df_filtrado.shape[0]}")

    # ============================
    # Gráficos comparativos
    # ============================
    if "Dirección" in df_filtrado.columns and "Desempeño" in df_filtrado.columns:
        st.subheader("📊 Promedio de Desempeño por Dirección")
        fig_dir = px.bar(
            df_filtrado.groupby("Dirección")["Desempeño"].mean().reset_index(),
            x="Dirección", y="Desempeño", text_auto=".2f", color="Desempeño"
        )
        st.plotly_chart(fig_dir, use_container_width=True)

    if "Área" in df_filtrado.columns and "Desempeño" in df_filtrado.columns:
        st.subheader("📊 Promedio de Desempeño por Área")
        fig_area = px.bar(
            df_filtrado.groupby("Área")["Desempeño"].mean().reset_index(),
            x="Área", y="Desempeño", text_auto=".2f", color="Desempeño"
        )
        st.plotly_chart(fig_area, use_container_width=True)

    if "Sub-área" in df_filtrado.columns and "Desempeño" in df_filtrado.columns:
        st.subheader("📊 Promedio de Desempeño por Sub-área")
        fig_sub = px.bar(
            df_filtrado.groupby("Sub-área")["Desempeño"].mean().reset_index(),
            x="Sub-área", y="Desempeño", text_auto=".2f", color="Desempeño"
        )
        st.plotly_chart(fig_sub, use_container_width=True)

    if "Evaluador" in df_filtrado.columns and "Desempeño" in df_filtrado.columns:
        st.subheader("📊 Promedio de Desempeño por Evaluador")
        fig_eval = px.bar(
            df_filtrado.groupby("Evaluador")["Desempeño"].mean().reset_index(),
            x="Evaluador", y="Desempeño", text_auto=".2f", color="Desempeño"
        )
        st.plotly_chart(fig_eval, use_container_width=True)

    # ============================
    # Correlaciones
    # ============================
    num_cols = df_filtrado.select_dtypes(include=[np.number]).columns.tolist()
    if len(num_cols) >= 2:
        st.subheader("📈 Matriz de Correlación")
        corr = df_filtrado[num_cols].corr()
        fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r", title="Correlación")
        st.plotly_chart(fig_corr, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error al cargar el archivo: {e}")
