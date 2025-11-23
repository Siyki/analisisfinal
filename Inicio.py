import pandas as pd
import streamlit as st
from PIL import Image
import numpy as np
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Sensor de Luz",
    page_icon="📡",
    layout="wide"
)

# --- FONDO AZUL CLARO ---
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Mulish:wght@300;700&display=swap');

/* Fondo */
html, body, .stApp {
    background: linear-gradient(135deg, #d8eefe, #b7dbff);
    color: #002147 !important; /* 🔵 Azul oscuro global */
    font-family: 'Mulish', sans-serif;
}

/* Títulos */
h1, h2, h3, h4, h5, h6 {
    color: #001a33 !important;  /* Azul oscuro más intenso */
    font-weight: 700;
}

/* Texto en markdown, widgets, labels, tabs */
p, label, span, div, .stText, .stMarkdown, .stSubheader, .stCaption, .stCheckbox, .stSelectbox label {
    color: #002147 !important;
}

/* Tab labels */
.stTabs [role="tab"] {
    color: #002147 !important;
    font-weight: bold;
}

/* Tab seleccionado */
.stTabs [aria-selected="true"] {
    color: #001a33 !important;
}

/* Botones */
.stButton>button {
    background-color: #0b5fa4;
    color: white !important;
    font-weight: bold;
    border-radius: 10px;
    padding: 0.6em 1.2em;
    border: none;
}

/* Dataframe (tablas) */
.dataframe, .stDataFrame, .stTable {
    color: #002147 !important;
}

/* Métricas */
[data-testid="stMetricDelta"] {
    color: #002147 !important;
}

</style>
""", unsafe_allow_html=True)


# --- TÍTULO PERSONALIZADO ---
st.title("💡 Sensor de Luz")

st.markdown(
    """
    ### Esta página te permite visualizar y analizar los datos capturados por un sensor de luz 📈✨
    """
)

# --- AGREGAR IMAGEN OLA ---
try:
    ola = Image.open("ola.jpg")
    st.image(ola, caption="Ola sensor-friendly 🌊", use_column_width=True)
except:
    st.info("⚠️ No se encontró la imagen 'ola.png'. Colócala en la carpeta del proyecto.")

# Crear mapa con ubicación de EAFIT
eafit_location = pd.DataFrame({
    'lat': [6.2006],
    'lon': [-75.5783],
    'location': ['Universidad EAFIT']
})

st.subheader("📍 Ubicación del Sensor - Universidad EAFIT")
st.map(eafit_location, zoom=15)

# --- SUBIR ARCHIVO ---
uploaded_file = st.file_uploader("Seleccione archivo CSV", type=["csv"])

if uploaded_file is not None:
    try:
        df1 = pd.read_csv(uploaded_file)

        # Si existe Time, renombrar
        if "Time" in df1.columns:
            other_columns = [col for col in df1.columns if col != "Time"]
            if len(other_columns) > 0:
                df1 = df1.rename(columns={other_columns[0]: "variable"})
        else:
            df1 = df1.rename(columns={df1.columns[0]: "variable"})

        # Procesar columna de tiempo
        if "Time" in df1.columns:
            df1["Time"] = pd.to_datetime(df1["Time"])
            df1 = df1.set_index("Time")

        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(
            ["📈 Visualización", "📊 Estadísticas", "🔍 Filtros", "🗺️ Info del Sitio"]
        )

        with tab1:
            st.subheader("📈 Visualización de Datos del Sensor de Luz")

            chart_type = st.selectbox(
                "Tipo de gráfico",
                ["Línea", "Área", "Barra"]
            )

            if chart_type == "Línea":
                st.line_chart(df1["variable"])
            elif chart_type == "Área":
                st.area_chart(df1["variable"])
            else:
                st.bar_chart(df1["variable"])

            if st.checkbox("Mostrar datos crudos"):
                st.write(df1)

        with tab2:
            st.subheader("📊 Estadísticas del Sensor")
            stats_df = df1["variable"].describe()

            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(stats_df)

            with col2:
                st.metric("Promedio", f"{stats_df['mean']:.2f}")
                st.metric("Máximo", f"{stats_df['max']:.2f}")
                st.metric("Mínimo", f"{stats_df['min']:.2f}")
                st.metric("Desviación Estándar", f"{stats_df['std']:.2f}")

        with tab3:
            st.subheader("🔍 Filtros de Datos")
            min_value = float(df1["variable"].min())
            max_value = float(df1["variable"].max())
            mean_value = float(df1["variable"].mean())

            if min_value == max_value:
                st.warning(f"⚠️ Todos los valores son iguales: {min_value:.2f}")
                st.dataframe(df1)
            else:
                col1, col2 = st.columns(2)

                with col1:
                    min_val = st.slider(
                        "Valor mínimo",
                        min_value,
                        max_value,
                        mean_value
                    )
                    filtrado_df_min = df1[df1["variable"] > min_val]
                    st.dataframe(filtrado_df_min)

                with col2:
                    max_val = st.slider(
                        "Valor máximo",
                        min_value,
                        max_value,
                        mean_value
                    )
                    filtrado_df_max = df1[df1["variable"] < max_val]
                    st.dataframe(filtrado_df_max)

                if st.button("Descargar filtrados"):
                    csv = filtrado_df_min.to_csv().encode("utf-8")
                    st.download_button(
                        label="Descargar CSV",
                        data=csv,
                        file_name="datos_filtrados.csv",
                        mime="text/csv"
                    )

        with tab4:
            st.subheader("🗺️ Información del Sitio")
            col1, col2 = st.columns(2)

            with col1:
                st.write("### 🌍 Ubicación")
                st.write("**Universidad EAFIT**")
                st.write("- Latitud: 6.2006")
                st.write("- Longitud: -75.5783")
                st.write("- Altitud: ~1,495 msnm")

            with col2:
                st.write("### 🔧 Datos del Sensor")
                st.write("- Tipo: ESP32")
                st.write("- Variable: Luz")
                st.write("- Frecuencia: Configurable")

    except Exception as e:
        st.error(f"Error al procesar archivo: {str(e)}")

else:
    st.warning("📁 Cargue un archivo CSV para comenzar.")

# Footer
st.markdown("---")
st.markdown("Desarrollado para análisis de sensores de luz • Universidad EAFIT ✨")
