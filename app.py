import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================
# Configuración de la página
# ============================
st.set_page_config(page_title="Dashboard Desempeño 2024", page_icon="📊", layout="wide")
st.title("📊 Reporte de Desempeño - 2024")

# ============================
# Carga de datos
# ============================
st.sidebar.header("⚙️ Configuración de datos")

archivo_subido = st.sidebar.file_uploader("Sube tu archivo CSV (separador ;)", type=["csv"])
ARCHIVO_REPO = "Desempeño 2024.csv"

try:
    if archivo_subido is not None:
        df = pd.read_csv(archivo_subido, sep=";", encoding="utf-8", engine="python")
        st.sidebar.success("✅ Usando archivo cargado por el usuario")
    else:
        df = pd.read_csv(ARCHIVO_REPO, sep=";", encoding="utf-8", engine="python")
        st.sidebar.info("ℹ️ Usando archivo por defecto del repo")

    # ============================
    # Normalización de columnas
    # ============================
    if "Nota" in df.columns:
        df["Nota"] = df["Nota"].astype(str).str.replace(",", ".")
        df["Nota"] = pd.to_numeric(df["Nota"], errors="coerce")

    if "Categoría" in df.columns:
        df["Categoría"] = df["Categoría"].str.strip().str.upper()
        df["Categoría"] = df["Categoría"].replace({
            "NO CUMPLE": "No cumple",
            "CUMPLE PARCIALMENTE": "Cumple Parcialmente",
            "CUMPLE": "Cumple",
            "DESTACADO": "Destacado",
            "EXCEPCIONAL": "Excepcional",
            "PENDIENTE": "Pendiente"
        })

    st.success(f"Datos cargados: {df.shape[0]} filas × {df.shape[1]} columnas")

    # ============================
    # Competencias de Liderazgo
    # ============================
    competencias = [
        "Liderazgo Magnético",
        "Formador de Personas",
        "Visión Estratégica",
        "Generación de Redes y Relaciones Efectivas",
        "Humildad",
        "Resolutividad"
    ]

    # Mapeo de categorías a números
    mapa_valores = {
        "No cumple": 1,
        "Cumple Parcialmente": 2,
        "Cumple": 3,
        "Destacado": 4,
        "Excepcional": 5
    }

    # Filtrar líderes
    lideres = df[df["Cargo"].str.contains("COORDINADOR|JEFE|SUPERVISOR|SUBGERENTE|GERENTE|DIRECTOR",
                                         case=False, na=False)].copy()

    # ============================
    # Radar Chart comparativo
    # ============================
    st.subheader("🌐 Evaluación de Competencias de Liderazgo (Radar)")

    if all(c in lideres.columns for c in competencias):
        lideres_num = lideres.copy()
        for comp in competencias:
            lideres_num[comp] = lideres_num[comp].replace(mapa_valores)

        # Promedio clínica
        promedio_clinica = lideres_num[competencias].mean()

        # Selector de Dirección
        direcciones = ["Toda la clínica"] + sorted(lideres_num["Dirección"].dropna().unique())
        dir_sel = st.selectbox("Comparar dirección específica", direcciones)

        if dir_sel != "Toda la clínica":
            promedio_dir = lideres_num[lideres_num["Dirección"] == dir_sel][competencias].mean()
        else:
            promedio_dir = None

        categorias = competencias
        fig_radar = go.Figure()

        fig_radar.add_trace(go.Scatterpolar(
            r=promedio_clinica.values,
            theta=categorias,
            fill='toself',
            name="Promedio clínica"
        ))

        if promedio_dir is not None:
            fig_radar.add_trace(go.Scatterpolar(
                r=promedio_dir.values,
                theta=categorias,
                fill='toself',
                name=dir_sel
            ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[1, 5],
                                tickvals=[1, 2, 3, 4, 5],
                                ticktext=["No cumple", "Cumple Parcialmente", "Cumple", "Destacado", "Excepcional"])
            ),
            showlegend=True
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.info("No se encontraron las competencias de liderazgo en el archivo cargado.")

    # ============================
    # Heatmap por líder (Plotly)
    # ============================
    st.subheader("🔥 Evaluación de Competencias de Liderazgo - Heatmap")

    if not lideres.empty:
        comp_cols = [c for c in competencias if c in lideres.columns]
        lideres_num = lideres[["Evaluado"] + comp_cols].copy()
        for comp in comp_cols:
            lideres_num[comp] = lideres_num[comp].replace(mapa_valores)

        heatmap_data = lideres_num.set_index("Evaluado")

        fig_heat = px.imshow(
            heatmap_data,
            labels=dict(x="Competencias", y="Evaluado", color="Nivel"),
            x=heatmap_data.columns,
            y=heatmap_data.index,
            color_continuous_scale="RdYlGn",
            aspect="auto"
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # ============================
    # Barplot comparativo
    # ============================
    st.subheader("📊 Promedio de Competencias de Liderazgo")

    if not lideres.empty:
        promedios_comp = heatmap_data.mean().reset_index()
        promedios_comp.columns = ["Competencia", "Promedio"]

        fig_bar = px.bar(
            promedios_comp,
            x="Competencia", y="Promedio",
            color="Competencia",
            text_auto=".2f",
            range_y=[1, 5]
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ============================
    # Boxplot distribución
    # ============================
    st.subheader("📦 Distribución de evaluaciones en competencias de liderazgo")

    if not lideres.empty:
        df_melt = lideres.melt(id_vars=["Evaluado"], value_vars=comp_cols,
                               var_name="Competencia", value_name="Evaluación")
        df_melt["Evaluación"] = df_melt["Evaluación"].replace(mapa_valores)

        fig_box = px.box(df_melt, x="Competencia", y="Evaluación", points="all", range_y=[1, 5])
        st.plotly_chart(fig_box, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error al cargar el archivo: {e}")
