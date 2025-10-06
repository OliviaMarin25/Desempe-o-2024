# Evolución Individual Mejorada
    st.subheader("📈 Evolución y Trayectoria Individual")
    
    col_sel_trabajador, _ = st.columns([1, 2])
    with col_sel_trabajador:
        trabajador = st.selectbox("Selecciona trabajador", ["Ninguno"] + sorted(df_filtrado["Evaluado"].dropna().unique().tolist()), key='sel_trab_hist')
    
    if trabajador != "Ninguno":
        
        trabajador_info = df_filtrado.loc[df_filtrado['Evaluado'] == trabajador].iloc[0]

        # 1. Evolución de Nota Global (Línea)
        st.markdown("#### Evolución Histórica de la Nota Global")
        notas_data = {
            "Año": [2022, 2023, 2024],
            "Nota": [
                trabajador_info.get("Nota_num_2022", np.nan),
                trabajador_info.get("Nota_num_2023", np.nan),
                trabajador_info.get("Nota_num_2024", np.nan)
            ]
        }
        notas_hist = pd.DataFrame(notas_data).dropna(subset=["Nota"])

        # Mantenemos la lógica anterior para el gráfico de línea. El st.info es claro.
        if not notas_hist.empty:
            fig_ind = go.Figure()
            fig_ind.add_trace(go.Scatter(
                x=notas_hist["Año"],
                y=notas_hist["Nota"],
                mode='lines+markers',
                line_shape='spline',
                marker=dict(size=10)
            ))
            fig_ind.update_layout(
                title_text=f"Nota Global por Año de {trabajador}",
                xaxis=dict(tickmode='array', tickvals=[2022, 2023, 2024], tickformat='d'),
                yaxis=dict(range=[0, 5], dtick=0.5)
            )
            st.plotly_chart(fig_ind, use_container_width=True)
        else:
            st.info(f"No se encontraron datos de notas históricas para {trabajador}.")
            
        # 2. Resumen Anual de Categoría y Feedback
        st.markdown("#### Categoría y Estado de Feedback (2024)")
        
        col_cat, col_feed = st.columns(2)
        with col_cat:
            st.metric("Categoría 2024", trabajador_info.get("Categoría 2024", "N/A"))
        with col_feed:
            st.metric("Avances Feedback", trabajador_info.get("Avances Feedback", "N/A"))

        # MODIFICACIÓN CLAVE: Lógica para elegir el gráfico de competencias adecuado.
        # 3. Evolución de Competencias (Gráfico dinámico)
        st.markdown("#### Desempeño en Competencias vs. Promedio del Grupo")
        
        competencias_existentes = [c for c in COMPETENCIAS_TRANSVERSALES if c in df_filtrado.columns and pd.notna(trabajador_info.get(c))]
        num_competencias = len(competencias_existentes)
        
        # --- Lógica condicional: Radar si >= 3, Barras si > 0, Mensaje si = 0 ---

        if num_competencias >= 3:
            # CASO 1: Hay 3 o más competencias -> Usamos el Gráfico de Radar
            st.markdown("<h5 style='text-align: center; color: grey;'>Gráfico de Radar</h5>", unsafe_allow_html=True)
            datos_trabajador = trabajador_info[competencias_existentes]
            promedio_filtrado = df_filtrado[competencias_existentes].mean()
            
            fig_comp_radar = go.Figure()
            fig_comp_radar.add_trace(go.Scatterpolar(r=promedio_filtrado.values, theta=competencias_existentes, fill="toself", name="Promedio Grupo Filtrado", line=dict(color=COLORES_CATEGORIAS["Cumple"])))
            fig_comp_radar.add_trace(go.Scatterpolar(r=datos_trabajador.values, theta=competencias_existentes, fill="toself", name=f"{trabajador}", line=dict(color=COLORES_CATEGORIAS["Destacado"])))
            fig_comp_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=True, title="Competencias Transversales (Escala 1 a 5)")
            st.plotly_chart(fig_comp_radar, use_container_width=True)

        elif num_competencias > 0:
            # CASO 2: Hay 1 o 2 competencias -> Usamos un Gráfico de Barras Horizontales
            st.markdown("<h5 style='text-align: center; color: grey;'>Gráfico de Barras</h5>", unsafe_allow_html=True)
            datos_trabajador_bar = trabajador_info[competencias_existentes]
            promedio_filtrado_bar = df_filtrado[competencias_existentes].mean()
            
            # Creamos un DataFrame para facilitar el gráfico de barras agrupado
            df_bar = pd.DataFrame({
                'Competencia': competencias_existentes,
                f'{trabajador}': datos_trabajador_bar.values,
                'Promedio Grupo Filtrado': promedio_filtrado_bar.values
            }).melt(id_vars='Competencia', var_name='Métrica', value_name='Valor')

            fig_comp_bar = px.bar(
                df_bar,
                x='Valor',
                y='Competencia',
                color='Métrica',
                barmode='group',
                orientation='h',
                text_auto='.2f', # Muestra el valor en la barra
                color_discrete_map={
                    f'{trabajador}': COLORES_CATEGORIAS["Destacado"],
                    'Promedio Grupo Filtrado': COLORES_CATEGORIAS["Cumple"]
                }
            )
            fig_comp_bar.update_layout(
                title_text="Comparación de Competencias (Escala 1 a 5)",
                xaxis_title="Nota",
                yaxis_title="",
                legend_title="Referencia",
                uniformtext_minsize=8, 
                uniformtext_mode='hide'
            )
            fig_comp_bar.update_xaxes(range=[0, 5.5]) # Damos espacio para el texto
            st.plotly_chart(fig_comp_bar, use_container_width=True)

        else:
            # CASO 3: No hay datos de competencias
            st.warning("No se encontraron datos de competencias transversales para este trabajador.")
