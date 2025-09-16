import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

# ============================
# Configuración de la página
# ============================
st.set_page_config(page_title="Dashboard Desempeño 2024", page_icon="📊", layout="wide")
st.title("📊 Reporte de Desempeño - 2024")

# ============================
# Función para exportar a Excel
# ============================
def descargar_excel(df, nombre_archivo, etiqueta="💾 Descargar Excel"):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Datos")
    st.download_button(
        label=etiqueta,
        data=buffer.getvalue(),
        file_name=nombre_archivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ============================
# Carga de datos
# ============================
st.sidebar.header("⚙️ Configuración de datos")

archivo_subido = st.sidebar.file_uploader("Sube tu archivo CSV (separador ;)", type=["csv"])
ARCHIVO_REPO = "Desempeño 2024.csv"   # archivo por defecto

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

    # ============================
    # Normalización de competencias
    # ============================
    mapa_competencias = {
        "HUMILDAD": "Humildad",
        "RESOLUTIVIDAD": "Resolutividad",
        "FORMADOR DE": "Formador de Personas",
        "LIDERAZGO MA": "Liderazgo Magnético",
        "VISION ESTRAT": "Visión Estratégica",
        "GENERACION D": "Generación de Redes y Relaciones Efectivas"
    }
    df.rename(columns=lambda c: mapa_competencias.get(c.strip().upper(), c), inplace=True)

    st.success(f"Datos cargados: {df.shape[0]} filas × {df.shape[1]} columnas")

    # ============================
    # Paleta de colores y orden
    # ============================
    categoria_colores = {
        "Excepcional": "violet",
        "Destacado": "skyblue",
        "Cumple": "green",
        "Cumple Parcialmente": "gold",
        "No cumple": "red",
        "Pendiente": "lightgrey"
    }
    categoria_orden = ["Excepcional","Destacado","Cumple","Cumple Parcialmente","No cumple","Pendiente"]

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
    if "Nota" in df.columns:
        c4.metric("Promedio Nota", round(df["Nota"].mean(), 2))

    # ============================
    # Filtros jerárquicos
    # ============================
    st.subheader("🔎 Filtros")

    direcciones = ["Todos"] + sorted(df["Dirección"].dropna().unique())
    dir_sel = st.selectbox("Filtrar por Dirección", direcciones)

    df_filtrado = df.copy()
    if dir_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Dirección"] == dir_sel]

    if "Área" in df_filtrado.columns:
        areas = ["Todos"] + sorted(df_filtrado["Área"].dropna().unique())
        area_sel = st.selectbox("Filtrar por Área", areas)
        if area_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Área"] == area_sel]
    else:
        area_sel = "Todos"

    if "Sub-área" in df_filtrado.columns:
        subareas = ["Todos"] + sorted(df_filtrado["Sub-área"].dropna().unique())
        sub_sel = st.selectbox("Filtrar por Sub-área", subareas)
        if sub_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Sub-área"] == sub_sel]
    else:
        sub_sel = "Todos"

    if "Evaluador" in df.columns:
        evaluadores = ["Todos"] + sorted(df["Evaluador"].dropna().unique())
        eval_sel = st.selectbox("Filtrar por Evaluador", evaluadores)
        if eval_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Evaluador"] == eval_sel]

    st.write(f"**Registros filtrados:** {df_filtrado.shape[0]}")

    # ============================
    # Distribución por Categoría (%)
    # ============================
    if "Categoría" in df_filtrado.columns:
        st.subheader("📊 Distribución de Categorías (%)")
        cat_counts = (
            df_filtrado["Categoría"].value_counts(normalize=True) * 100
        ).reindex(categoria_orden, fill_value=0).reset_index()
        cat_counts.columns = ["Categoría", "Porcentaje"]

        fig_cat = px.bar(
            cat_counts,
            x="Categoría", y="Porcentaje",
            color="Categoría",
            category_orders={"Categoría": categoria_orden},
            color_discrete_map=categoria_colores,
            text_auto=".1f"
        )
        fig_cat.update_layout(yaxis_title="Porcentaje (%)")
        st.plotly_chart(fig_cat, use_container_width=True)

        descargar_excel(cat_counts, "Distribucion_Categorias.xlsx")

    # ============================
    # Mejores y peores evaluados
    # ============================
    if "Nota" in df_filtrado.columns:
        st.subheader("🏆 Mejores y Peores Evaluados")

        mejores = df_filtrado.sort_values("Nota", ascending=False).head(10)
        peores = df_filtrado.sort_values("Nota", ascending=True).head(20)

        st.markdown("### 🔝 Top 10 mejores resultados")
        st.dataframe(mejores[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]], use_container_width=True)
        descargar_excel(mejores, "Top10_Mejores.xlsx", "💾 Descargar Excel (Mejores)")

        st.markdown("### 🔻 Top 20 peores resultados")
        st.dataframe(peores[["Evaluado", "Cargo", "Evaluador", "Categoría", "Nota"]], use_container_width=True)
        descargar_excel(peores, "Top20_Peores.xlsx", "💾 Descargar Excel (Peores)")

    # ============================
    # Tabla de líderes con competencias numéricas
    # ============================
    st.subheader("👔 Líderes y Evaluación de Competencias")
    cargos_lider = ["COORDINADOR", "JEFE", "SUPERVISOR", "SUBGERENTE", "GERENTE", "DIRECTOR"]

    mapa_valores = {
        "NO CUMPLE": 1,
        "CUMPLE PARCIALMENTE": 2,
        "CUMPLE": 3,
        "DESTACADO": 4,
        "EXCEPCIONAL": 5
    }

    if "Cargo" in df.columns:
        lideres = df[df["Cargo"].str.upper().str.contains("|".join(cargos_lider), na=False)]

        comp_cols = [
            "Liderazgo Magnético",
            "Formador de Personas",
            "Visión Estratégica",
            "Generación de Redes y Relaciones Efectivas",
            "Humildad",
            "Resolutividad"
        ]
        cols_finales = ["Evaluado","Cargo","Evaluador","Categoría","Nota"] + [c for c in comp_cols if c in df.columns]

        if not lideres.empty:
            lideres_num = lideres.copy()
            for col in comp_cols:
                if col in lideres_num.columns:
                    lideres_num[col] = lideres_num[col].replace(mapa_valores)

            st.dataframe(lideres_num[cols_finales], use_container_width=True)
            descargar_excel(lideres_num[cols_finales], "Lideres_Competencias.xlsx")

    # ============================
    # Competencias críticas
    # ============================
    competencias = [
        "Liderazgo Magnético",
        "Formador de Personas",
        "Visión Estratégica",
        "Generación de Redes y Relaciones Efectivas",
        "Humildad",
        "Resolutividad"
    ]

    st.subheader("⚠️ Personas con Competencias en 'Cumple Parcialmente' o 'No Cumple'")
    for comp in competencias:
        if comp in df.columns:
            criticos = df[df[comp].isin(["CUMPLE PARCIALMENTE", "NO CUMPLE"])]
            if not criticos.empty:
                st.markdown(f"### 📌 {comp}")
                st.dataframe(criticos[["Evaluado", "Cargo", "Evaluador", comp]], use_container_width=True)
                descargar_excel(criticos[["Evaluado", "Cargo", "Evaluador", comp]], f"Criticos_{comp}.xlsx")

    # ============================
    # Radar + Tabla + Barplot
    # ============================
    st.subheader("🌐 Competencias de Liderazgo (Radar y Comparaciones)")

    comp_cols = [c for c in competencias if c in df.columns]

    if comp_cols:
        df_comp = df_filtrado[comp_cols].replace(mapa_valores)
        promedio_clinica = df[comp_cols].replace(mapa_valores).mean()

        if dir_sel != "Todos":
            promedio_dir = df[df["Dirección"] == dir_sel][comp_cols].replace(mapa_valores).mean()
        else:
            promedio_dir = None

        categorias = comp_cols
        valores_clinica = promedio_clinica.values.tolist()
        valores_dir = promedio_dir.values.tolist() if promedio_dir is not None else None

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=valores_clinica,
            theta=categorias,
            fill='toself',
            name="Promedio Clínica",
            line=dict(color="green")
        ))
        if valores_dir:
            fig_radar.add_trace(go.Scatterpolar(
                r=valores_dir,
                theta=categorias,
                fill='toself',
                name=f"Promedio {dir_sel}",
                line=dict(color="blue")
            ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[1,5])),
            showlegend=True
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        tabla = pd.DataFrame({
            "Competencia": categorias,
            "Promedio Clínica": valores_clinica,
            f"Promedio {dir_sel}": valores_dir if valores_dir else ["-"]*len(categorias)
        })
        st.dataframe(tabla, use_container_width=True)
        descargar_excel(tabla, "Competencias_Liderazgo.xlsx")

        st.subheader("📊 Promedio de Competencias de Liderazgo")
        datos_bar = pd.DataFrame({
            "Competencia": categorias,
            "Clínica": valores_clinica,
            f"{dir_sel}": valores_dir if valores_dir else [None]*len(categorias)
        })
        datos_bar = datos_bar.melt(id_vars="Competencia", var_name="Grupo", value_name="Promedio")

        fig_bar = px.bar(
            datos_bar, x="Competencia", y="Promedio",
            color="Grupo", barmode="group",
            text_auto=".2f", range_y=[1,5]
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        descargar_excel(datos_bar, "Comparacion_Competencias.xlsx")

except Exception as e:
    st.error(f"❌ Error al cargar el archivo: {e}")
