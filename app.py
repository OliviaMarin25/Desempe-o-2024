import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np 

st.set_page_config(page_title="Reporte de Desempeño - 2024", layout="wide")

# --- Constantes y Configuración ---

# Definición de constantes
COMPETENCIAS = [
    "Humildad", "Resolutividad", "Formador de Personas",
    "Liderazgo Magnético", "Visión Estratégica",
    "Generación de Redes y Relaciones Efectivas"
]
CATEGORIAS_ORDEN = [
    "Excepcional", "Destacado", "Cumple", "Cumple Parcialmente", "No Cumple", "Pendiente"
]
COLORES_CATEGORIAS = {
    "Excepcional": "#8A2BE2", # Violet
    "Destacado": "#1E90FF",   # DodgerBlue
    "Cumple": "#3CB371",      # MediumSeaGreen
    "Cumple Parcialmente": "#FFD700", # Gold
    "No Cumple": "#DC143C",   # Crimson
    "Pendiente": "#D3D3D3"    # LightGray
}
COLORES_FEEDBACK = {"Completado": "#3CB371", "En Proceso": "#FFD700", "Pendiente": "#DC143C"}


st.title("📊 Reporte de Desempeño - 2024")

# ============================
# FUNCIONES DE PROCESAMIENTO
# ============================

@st.cache_data
def load_and_process_data(uploaded_file):
    """Carga y procesa el archivo CSV con manejo de múltiples separadores/encodings."""
    try:
        # Intento 1: Separador ; UTF-8
        df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8", engine="python")
    except Exception:
        try:
            # Intento 2: Separador , Latin-1
            uploaded_file.seek(0) # Resetear puntero
            df = pd.read_csv(uploaded_file, sep=",", encoding="latin-1", engine="python")
        except Exception:
            try:
                # Intento 3: Separador tab UTF-8
                uploaded_file.seek(0) # Resetear puntero
                df = pd.read_csv(uploaded_file, sep="\t", encoding="utf-8", engine="python")
            except Exception as e:
                st.error(f"Error al leer el archivo. Intenta con un formato diferente. Detalle: {e}")
                return None
    
    # Normalización y Limpieza
    df.columns = df.columns.str.strip()
    df_proc = df.copy()
    
    # Conversión de notas a numérico
    df_proc["Nota_num_2024"] = pd.to_numeric(df_proc.get("Nota 2024", pd.Series(dtype='float64')), errors="coerce")
    df_proc["Nota_num_2023"] = pd.to_numeric(df_proc.get("Nota 2023", pd.Series(dtype='float64')), errors="coerce")
    df_proc["Nota_num_2022"] = pd.to_numeric(df_proc.get("Nota 2022", pd.Series(dtype='float64')), errors="coerce")

    # Conversión de competencias a numérico
    for comp in COMPETENCIAS:
        if comp in df_proc.columns:
             df_proc[comp] = pd.to_numeric(df_proc[comp], errors="coerce")
             
    # Rellenar valores nulos
    for col in ["Dirección", "Área", "Sub-área", "Evaluado", "Cargo", "Categoría 2024"]:
        if col in df_proc.columns:
            df_proc[col] = df_proc[col].fillna("Sin Asignar")
    
    # Columna de Feedback de ejemplo (si no existe)
    if "Avances Feedback" not in df_proc.columns:
        np.random.seed(42)
        df_proc["Avances Feedback"] = np.random.choice(["Completado", "En Proceso", "Pendiente"], size=len(df_proc))

    return df_proc

# ============================
# Subir archivo CSV
# ============================
uploaded_file = st.file_uploader("📂 Sube el archivo CSV con los datos", type=["csv"])

if uploaded_file is not None:
    df = load_and_process_data(uploaded_file)

    if df is None:
        st.stop()

    # ============================
    # Filtros dinámicos (Sidebar)
    # ============================
    st.sidebar.header("Filtros")
    
    direcciones = ["Todas"] + sorted(df["Dirección"].dropna().unique().tolist())
    seleccion_direccion = st.sidebar.selectbox("Dirección", direcciones, index=0)
    
    df_filtrado = df.copy()
    if seleccion_direccion != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Dirección"] == seleccion_direccion]

    areas_disponibles = ["Todas"] + sorted(df_filtrado["Área"].dropna().unique().tolist())
    seleccion_area = st.sidebar.selectbox("Área", areas_disponibles, index=0)
    
    if seleccion_area != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Área"] == seleccion_area]

    subareas_disponibles = ["Todas"] + sorted(df_filtrado["Sub-área"].dropna().unique().tolist())
    seleccion_subarea = st.sidebar.selectbox("Sub-área", subareas_disponibles, index=0)
    
    if seleccion_subarea != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Sub-área"] == seleccion_subarea]

    df_2024 = df_filtrado.copy()

    # --- Métricas Clave (KPI's) ---
    
    st.markdown("---")
    st.header("🔑 Métricas Clave (KPIs)")
    
    total_evaluados = df_2024["Evaluado"].nunique()
    promedio_nota = df_2024["Nota_num_2024"].mean() if "Nota_num_2024" in df_2024.columns else np.nan
    porc_destacado_o_mas = (
        df_2024["Categoría 2024"].isin(["Excepcional", "Destacado"]).sum() / total_evaluados
    ) * 100 if total_evaluados > 0 else 0

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Evaluados", f"{total_evaluados:,}")
    with col2:
        st.metric("Nota Promedio (2024)", f"{promedio_nota:.2f}" if not np.isnan(promedio_nota) else "N/A")
    with col3:
        st.metric("% Destacado o Superior", f"{porc_destacado_o_mas:.1f}%")

    st.markdown("---")
    
    # ============================
    # Sección 1: Resultados 2024
    # ============================
    st.header("📌 Resultados 2024")

    col_distribucion, col_feedback = st.columns([2, 1])

    with col_distribucion:
        st.subheader("Distribución de Categorías de Desempeño")
        conteo_categorias = df_2024["Categoría 2024"].value_counts().reindex(
            CATEGORIAS_ORDEN, fill_value=0
        ).reset_index()
        conteo_categorias.columns = ["Categoría", "Cantidad"]
        total_cat = conteo_categorias["Cantidad"].sum()
        conteo_categorias["Porcentaje"] = (conteo_categorias["Cantidad"] / total_cat * 100).round(1)

        opcion_grafico = st.radio("Ver distribución por:", ["Porcentaje (%)", "Cantidad (N personas)"], horizontal=True, key='distrib_radio')

        if opcion_grafico == "Porcentaje (%)":
            fig_cat = px.bar(
                conteo_categorias, x="Categoría", y="Porcentaje", color="Categoría",
                text=conteo_categorias["Porcentaje"].astype(str) + "%",
                color_discrete_map=COLORES_CATEGORIAS
            )
            fig_cat.update_layout(yaxis_title="Porcentaje (%)")
        else:
            fig_cat = px.bar(
                conteo_categorias, x="Categoría", y="Cantidad", color="Categoría",
                text=conteo_categorias["Cantidad"].astype(str),
                color_discrete_map=COLORES_CATEGORIAS
            )
            fig_cat.update_layout(yaxis_title="Cantidad de personas")
        fig_cat.update_traces(textposition='outside')
        st.plotly_chart(fig_cat, use_container_width=True)

    # Avances en Feedback
    with col_feedback:
        st.subheader("Avance en Plan de Feedback")
        
        # Conteo de la columna "Avances Feedback"
        conteo_feedback = df_2024["Avances Feedback"].value_counts().reset_index()
        conteo_feedback.columns = ["Estado", "Cantidad"]
        
        fig_feedback = px.pie(
            conteo_feedback, 
            names='Estado', 
            values='Cantidad', 
            title='Estado de Cumplimiento de Feedback',
            color='Estado',
            color_discrete_map=COLORES_FEEDBACK
        )
        fig_feedback.update_traces(textposition='inside', textinfo='percent+label')
        fig_feedback.update_layout(showlegend=False)
        
        st.plotly_chart(fig_feedback, use_container_width=True)


    # Top 20 y Bottom 20
    st.subheader("🏆 Evaluaciones Destacadas")
    df_tb = df_2024.copy().dropna(subset=["Nota_num_2024"]) 

    top_20 = df_tb.nlargest(20, "Nota_num_2024")[["Evaluado", "Cargo", "Evaluador", "Categoría 2024", "Nota 2024"]]
    bottom_20 = df_tb.nsmallest(20, "Nota_num_2024")[["Evaluado", "Cargo", "Evaluador", "Categoría 2024", "Nota 2024"]]

    col_top, col_bottom = st.columns(2)
    with col_top:
        st.markdown("### ⬆️ Top 20: Evaluaciones más altas")
        st.dataframe(top_20, use_container_width=True)

    with col_bottom:
        st.markdown("### ⬇️ Bottom 20: Evaluaciones más bajas")
        st.dataframe(bottom_20, use_container_width=True)
        
    st.markdown("---")

    # ============================
    # Sección 2: Liderazgo
    # ============================
    st.header("📌 Sección 2: Liderazgo")

    df_lideres = df_2024[df_2024["Cargo"].str.contains("Jefe|Subgerente|Coordinador|Director|Supervisor", case=False, na=False)].copy()

    # Ranking por nota 2024 recibida
    ranking_lideres = (
        df_lideres.groupby("Evaluado")
        .agg(Nota2024=("Nota_num_2024", "mean"),
             **{comp: (comp, "mean") for comp in COMPETENCIAS})
        .reset_index()
    )
    ranking_lideres["Promedio Competencias"] = ranking_lideres[COMPETENCIAS].mean(axis=1).round(2)
    ranking_lideres["Nota2024"] = ranking_lideres["Nota2024"].round(2)
    ranking_lideres = ranking_lideres.sort_values("Nota2024", ascending=False).reset_index(drop=True)
    ranking_lideres.index += 1
    ranking_lideres.insert(0, "Ranking", ranking_lideres.index)

    st.subheader("📈 Ranking de Líderes (Nota 2024 recibida)")
    st.dataframe(ranking_lideres, use_container_width=True)

    # Radar comparativo
    st.subheader("🕸️ Radar de Competencias (Comparación)")

    col_dir_radar, col_lider_radar = st.columns(2)
    with col_dir_radar:
        seleccion_direccion_radar = st.selectbox("Selecciona Dirección para Comparar", 
                                                 ["Ninguno"] + sorted(df["Dirección"].dropna().unique()),
                                                 key='dir_radar')
    with col_lider_radar:
        filtro_lideres_radar = df[df["Cargo"].str.contains("Jefe|Subgerente|Coordinador|Director|Supervisor", case=False, na=False)]
        
        if seleccion_direccion_radar != "Ninguno":
            lideres_disponibles = sorted(
                filtro_lideres_radar[filtro_lideres_radar["Dirección"] == seleccion_direccion_radar]["Evaluado"].dropna().unique().tolist()
            )
        else:
            lideres_disponibles = sorted(filtro_lideres_radar["Evaluado"].dropna().unique().tolist())
            
        seleccion_lider = st.selectbox("Selecciona un Líder Específico", ["Ninguno"] + lideres_disponibles, key='lider_radar')
    
    # Cálculos para el radar
    promedio_clinica = df[COMPETENCIAS].mean()
    promedio_direccion = None
    promedio_lider = None

    if seleccion_direccion_radar != "Ninguno":
        promedio_direccion = df[df["Dirección"] == seleccion_direccion_radar][COMPETENCIAS].mean()
    
    if seleccion_lider != "Ninguno":
        promedio_lider = df[df["Evaluado"] == seleccion_lider][COMPETENCIAS].mean()
        
    fig_radar = go.Figure()

    fig_radar.add_trace(go.Scatterpolar(r=promedio_clinica.values, 
                                        theta=COMPETENCIAS, 
                                        fill="toself", 
                                        name="Promedio Clínica", 
                                        line=dict(color=COLORES_CATEGORIAS["Destacado"])))

    if promedio_direccion is not None and not promedio_direccion.empty:
        fig_radar.add_trace(go.Scatterpolar(r=promedio_direccion.values, 
                                            theta=COMPETENCIAS, 
                                            fill="toself", 
                                            name=f"Promedio Dirección: {seleccion_direccion_radar}", 
                                            line=dict(color=COLORES_CATEGORIAS["Cumple"])))
                                            
    if promedio_lider is not None and not promedio_lider.empty:
        fig_radar.add_trace(go.Scatterpolar(r=promedio_lider.values, 
                                            theta=COMPETENCIAS, 
                                            fill="toself", 
                                            name=f"Líder: {seleccion_lider}", 
                                            line=dict(color=COLORES_CATEGORIAS["Excepcional"])))
        
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), 
                            showlegend=True,
                            title="Nivelación de Competencias de Liderazgo (Escala 1 a 5)")
    st.plotly_chart(fig_radar, use_container_width=True)
    
    st.markdown("---")

    # ============================
    # Sección 3: Desempeño Histórico
    # ============================
    st.header("📌 Sección 3: Desempeño Histórico")

    columnas_hist = ["Nota 2022", "Categoría 2022", "Nota 2023", "Categoría 2023", "Nota 2024", "Categoría 2024"]
    st.subheader("📋 Tabla histórica")
    
    def es_top(categoria):
        return categoria in ["Excepcional", "Destacado"]
    def es_bajo(categoria):
        return categoria in ["No Cumple", "Cumple Parcialmente"]

    # Corrección del KeyError: Ordenar antes de seleccionar columnas
    cols_base = ["Evaluado", "Cargo", "Dirección", "Área", "Sub-área"]
    cols_a_mostrar = [col for col in cols_base + columnas_hist if col in df_filtrado.columns]

    df_ordenado = df_filtrado.copy()
    if "Nota_num_2024" in df_ordenado.columns:
        df_ordenado = df_ordenado.sort_values("Nota_num_2024", ascending=False)

    st.dataframe(df_ordenado[cols_a_mostrar], use_container_width=True) # Mostrar solo las columnas visibles

    st.subheader("🌟 Mejores trayectorias (Consistentemente 'Destacado' o 'Excepcional')")
    
    mejores_tray = df_filtrado[
        df_filtrado.apply(lambda row: es_top(row.get("Categoría 2024")) and 
                                      (es_top(row.get("Categoría 2023")) or es_top(row.get("Categoría 2022"))), axis=1)
    ]
    st.dataframe(mejores_tray[["Evaluado"] + columnas_hist], use_container_width=True)

    st.subheader("⚠️ Trayectorias descendentes (Consistentemente 'No Cumple' o 'Cumple Parcialmente')")
    
    malas_tray = df_filtrado[
        df_filtrado.apply(lambda row: es_bajo(row.get("Categoría 2024")) and 
                                      (es_bajo(row.get("Categoría 2023")) or es_bajo(row.get("Categoría 2022"))), axis=1)
    ]
    st.dataframe(malas_tray[["Evaluado"] + columnas_hist], use_container_width=True)

    # Evolución Individual Mejorada
    st.subheader("📈 Evolución y Trayectoria Individual")
    
    col_sel_trabajador, _ = st.columns([1, 2])
    with col_sel_trabajador:
        trabajador = st.selectbox("Selecciona trabajador", ["Ninguno"] + sorted(df_filtrado["Evaluado"].dropna().unique().tolist()), key='sel_trab_hist')
    
    if trabajador != "Ninguno":
        
        # 1. Evolución de Nota Global (Línea)
        st.markdown("#### Evolución Histórica de la Nota Global")
        notas_data = {
            "Año": [2022, 2023, 2024],
            "Nota": [
                df_filtrado[df_filtrado["Evaluado"] == trabajador].get("Nota_num_2022", pd.Series(dtype='float64')).iloc[0] if not df_filtrado[df_filtrado["Evaluado"] == trabajador].empty else np.nan,
                df_filtrado[df_filtrado["Evaluado"] == trabajador].get("Nota_num_2023", pd.Series(dtype='float64')).iloc[0] if not df_filtrado[df_filtrado["Evaluado"] == trabajador].empty else np.nan,
                df_filtrado[df_filtrado["Evaluado"] == trabajador].get("Nota_num_2024", pd.Series(dtype='float64')).iloc[0] if not df_filtrado[df_filtrado["Evaluado"] == trabajador].empty else np.nan
            ]
        }
        notas_hist = pd.DataFrame(notas_data).dropna(subset=["Nota"])

        if not notas_hist.empty:
            fig_ind = px.line(notas_hist, x="Año", y="Nota", markers=True, 
                              title=f"Nota Global por Año de {trabajador}",
                              line_shape='spline')
            fig_ind.update_yaxes(range=[0, 5], dtick=0.5) 
            fig_ind.update_layout(xaxis=dict(tickmode='array', tickvals=[2022, 2023, 2024], tickformat='d'))
            st.plotly_chart(fig_ind, use_container_width=True)
        else:
            st.info(f"Datos de nota global insuficientes para {trabajador}.")
            
        # 2. Resumen Anual de Categoría y Feedback
        st.markdown("#### Categoría y Estado de Feedback (2024)")
        info_2024 = df_filtrado[df_filtrado["Evaluado"] == trabajador].iloc[0]
        
        col_cat, col_feed = st.columns(2)
        with col_cat:
            st.metric("Categoría 2024", info_2024.get("Categoría 2024", "N/A"))
        with col_feed:
            st.metric("Avances Feedback", info_2024.get("Avances Feedback", "N/A"))

        # 3. Evolución de Competencias (Radar)
        st.markdown("#### Desempeño en Competencias vs. Promedio del Grupo")
        
        datos_trabajador = df_filtrado[df_filtrado["Evaluado"] == trabajador][COMPETENCIAS].iloc[0]
        promedio_filtrado = df_filtrado[COMPETENCIAS].mean()
        
        fig_comp_radar = go.Figure()
        
        fig_comp_radar.add_trace(go.Scatterpolar(r=promedio_filtrado.values, 
                                            theta=COMPETENCIAS, 
                                            fill="toself", 
                                            name="Promedio Grupo Filtrado", 
                                            line=dict(color=COLORES_CATEGORIAS["Cumple"])))
        
        fig_comp_radar.add_trace(go.Scatterpolar(r=datos_trabajador.values, 
                                            theta=COMPETENCIAS, 
                                            fill="toself", 
                                            name=f"{trabajador}", 
                                            line=dict(color=COLORES_CATEGORIAS["Destacado"])))
        
        fig_comp_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), 
                                     showlegend=True,
                                     title=f"Competencias Clave (Escala 1 a 5)")
        st.plotly_chart(fig_comp_radar, use_container_width=True)


else:
    st.info("📂 Sube un archivo CSV para comenzar. El sistema intentará detecta distintos separadores y codificaciones.")
