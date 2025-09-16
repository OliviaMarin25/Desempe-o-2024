# ============================
# Análisis por Dirección
# ============================
if "Dirección" in df.columns and "Desempeño" in df.columns:
    st.subheader("🏢 Análisis por Dirección")

    # Tabla resumen por Dirección
    resumen_dir = df.groupby("Dirección").agg(
        Registros=("Desempeño", "count"),
        Promedio=("Desempeño", "mean"),
        Mínimo=("Desempeño", "min"),
        Máximo=("Desempeño", "max")
    ).reset_index()
    resumen_dir["Promedio"] = resumen_dir["Promedio"].round(2)

    st.markdown("**📋 Tabla Resumen por Dirección**")
    st.dataframe(resumen_dir, use_container_width=True)

    # Gráfico comparativo de promedio
    st.markdown("**📊 Promedio de Desempeño por Dirección**")
    fig_avg = px.bar(
        resumen_dir,
        x="Dirección", y="Promedio",
        text_auto=".2f", color="Promedio",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig_avg, use_container_width=True)

    # Distribución de resultados en cada Dirección
    st.markdown("**📈 Distribución de Desempeño por Dirección**")
    fig_dist = px.box(
        df, x="Dirección", y="Desempeño", color="Dirección",
        points="all", title="Distribución de Desempeño"
    )
    st.plotly_chart(fig_dist, use_container_width=True)

    # Opción de seleccionar una Dirección y ver detalle
    seleccion = st.selectbox("🔎 Ver detalle de una Dirección específica", resumen_dir["Dirección"].unique())
    detalle = df[df["Dirección"] == seleccion][["Nombre", "Cargo", "Evaluador", "Área", "Sub-área", "Desempeño"]]
    st.markdown(f"**Detalle de colaboradores en {seleccion}**")
    st.dataframe(detalle, use_container_width=True)
