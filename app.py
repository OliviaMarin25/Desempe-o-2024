    # ============================
    # Preprocesamiento
    # ============================
    columnas_necesarias = [
        "Evaluado", "Cargo", "Dirección", "Área", "Sub-área", "Evaluador",
        "Liderazgo Magnético", "Formador de Personas",
        "Visión Estratégica", "Generación de Redes y Relaciones Efectivas",
        "Humildad", "Resolutividad"
    ]

    # Detectar columnas de notas y categorías por año
    nota_cols = [c for c in df.columns if "Nota" in c]
    cat_cols = [c for c in df.columns if "Categoría" in c]

    if "Nota 2024" in nota_cols:
        df["Nota"] = df["Nota 2024"]   # alias estándar
    elif "Nota" in df.columns:
        df["Nota"] = df["Nota"]
    else:
        st.error("⚠️ No se encontró ninguna columna de Nota (ej: 'Nota 2024').")
        st.stop()

    if "Categoría 2024" in cat_cols:
        df["Categoría"] = df["Categoría 2024"]   # alias estándar
    elif "Categoría" in df.columns:
        df["Categoría"] = df["Categoría"]
    else:
        st.error("⚠️ No se encontró ninguna columna de Categoría (ej: 'Categoría 2024').")
        st.stop()

    # Convertir nota a número
    df["Nota_num"] = pd.to_numeric(df["Nota"], errors="coerce")

    # Seleccionar columnas finales
    df = df[[c for c in columnas_necesarias if c in df.columns] + ["Categoría", "Nota", "Nota_num"]]
