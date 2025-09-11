import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Reporte de Desempeño", layout="wide")

st.title("📊 Reporte de Desempeño - Piton")

# Nombre del archivo CSV (debe estar en el mismo repo que app.py)
archivo = "Desempeño-Piton.csv"

try:
    # Leer CSV (si ves problemas con tildes, cambia utf-8 por latin-1)
    df = pd.read_csv(archivo, encoding="utf-8")

    st.subheader("Vista general de los datos")
    st.dataframe(df)

    # KPIs básicos
    st.subheader("Indicadores")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total registros", len(df))
    if "Área" in df.columns:
        col2.metric("Áreas distintas", df["Área"].nunique())
    if "Desempeño" in df.columns:
        promedio = round(df["Desempeño"].mean(), 2)
        col3.metric("Promedio Desempeño", promedio)

    # Gráfico por Área
    if "Área" in df.columns:
        st.subheader("Distribución por Área")
        conteo = df["Área"].value_counts()
        st.bar_chart(conteo)

    # Gráfico por Evaluador
    if "Evaluador" in df.columns:
        st.subheader("Evaluaciones por Evaluador")
        evaluadores = df["Evaluador"].value_counts()
        st.bar_chart(evaluadores)

except Exception as e:
    st.error(f"❌ Error al cargar el archivo: {e}")
