    # ============================
    # Radar de competencias
    # ============================
    st.subheader("🕸️ Evaluación de Competencias de Liderazgo (Radar)")

    if all(col in df.columns for col in competencias):
        df_comp = df_lideres.copy()
        df_comp = df_comp[df_comp["Categoría"] != "Pendiente"]

        mapping = {"No cumple": 1, "Cumple Parcialmente": 2, "Cumple": 3, "Destacado": 4, "Excepcional": 5}
        for col in competencias:
            df_comp[col] = pd.to_numeric(df_comp[col], errors="coerce").fillna(df_comp[col].map(mapping))

        promedio_clinica = df_comp[competencias].mean().round(2)

        # Siempre mostrar los controles
        modo_radar = st.radio("Ver radar con:", 
                              ["Solo clínica", "Clínica + Dirección", "Clínica + Dirección + Líder"], 
                              horizontal=True)
        direcciones_disp = list(df["Dirección"].dropna().unique())
        dir_sel_radar = st.selectbox("Selecciona dirección", direcciones_disp)
        lideres_disponibles = df_comp[df_comp["Dirección"] == dir_sel_radar]["Evaluado"].dropna().unique()
        lider_sel = st.selectbox("Selecciona un líder", lideres_disponibles)

        promedio_dir = df_comp[df_comp["Dirección"] == dir_sel_radar][competencias].mean().round(2)
        datos_lider = df_comp[df_comp["Evaluado"] == lider_sel][competencias].mean().round(2)

        # ============================
        # Radar Plot con colores nuevos
        # ============================
        fig = go.Figure()

        # Promedio clínica (azul oscuro)
        fig.add_trace(go.Scatterpolar(
            r=promedio_clinica.values,
            theta=competencias,
            fill='toself',
            name='Promedio clínica',
            line=dict(color="darkblue"),
            fillcolor="rgba(0,0,139,0.3)"
        ))

        # Dirección (amarillo)
        if modo_radar in ["Clínica + Dirección", "Clínica + Dirección + Líder"]:
            fig.add_trace(go.Scatterpolar(
                r=promedio_dir.values,
                theta=competencias,
                fill='toself',
                name=f'Dirección: {dir_sel_radar}',
                line=dict(color="gold"),
                fillcolor="rgba(255,215,0,0.3)"
            ))

        # Líder (celeste)
        if modo_radar == "Clínica + Dirección + Líder":
            fig.add_trace(go.Scatterpolar(
                r=datos_lider.values,
                theta=competencias,
                fill='toself',
                name=f'Líder: {lider_sel}',
                line=dict(color="deepskyblue"),
                fillcolor="rgba(0,191,255,0.3)"
            ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)
