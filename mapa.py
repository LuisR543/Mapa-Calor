import streamlit as st
import pandas as pd
import pydeck as pdk
import time  # <--- Necesario para la animación

# --- 1. CONFIGURACIÓN DE NOMBRES DE COLUMNAS ---
COL_LAT = "Coordy"
COL_LON = "Coordx"
COL_TIMESTAMP = "timestamp" 
COL_INDICADOR = "predominant_color" 
COL_ID = "id"

st.title("Mapa de Calor - Simulación Automática")

# --- 2. CARGA DE DATOS ---
@st.cache_data
def cargar_datos():

    df = pd.read_csv("dataset2024.csv", encoding="ISO-8859-1")
    
   
    df[COL_LON] = pd.to_numeric(df[COL_LON], errors="coerce")
    df[COL_LAT] = pd.to_numeric(df[COL_LAT], errors="coerce")
    df = df.dropna(subset=[COL_LON, COL_LAT])
    
  
    df['fecha_hora_dt'] = pd.to_datetime(df[COL_TIMESTAMP])
    
    
    df = df.sort_values(by=['fecha_hora_dt', COL_ID])
    
    return df

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"Error cargando el archivo: {e}")
    st.stop()

# --- 3. LOGICA DE COLORES ---
MAPA_COLORES = {
    'red':      [255, 0, 0, 200],       # Rojo
    'green':    [0, 255, 0, 200],       # Verde
    'red_wine': [114, 47, 55, 200],     # Vino Tinto
    'default':  [128, 128, 128, 140]    # Gris
}

def asignar_color(val):
    val_limpio = str(val).strip() 
    return MAPA_COLORES.get(val_limpio, MAPA_COLORES['default'])

df['color_rgb'] = df[COL_INDICADOR].apply(asignar_color)

# --- 4. PREPARACIÓN DE LA VISTA ---

view_state = pdk.ViewState(
    latitude=df[COL_LAT].mean(),
    longitude=df[COL_LON].mean(),
    zoom=12,
    pitch=0,
)


tiempos_unicos = df['fecha_hora_dt'].unique()

# --- 5. VISUALIZACIÓN AUTOMÁTICA ---


if st.button("▶️ Iniciar Simulación"):
    
    
    texto_status = st.empty()
    mapa_placeholder = st.empty()
    barra_progreso = st.progress(0)
    
    total_pasos = len(tiempos_unicos)

    # BUCLE DE ANIMACIÓN
    for i, hora_actual in enumerate(tiempos_unicos):
        
        
        batch = df[df['fecha_hora_dt'] == hora_actual]
        
        fecha_str = pd.to_datetime(hora_actual).strftime('%Y-%m-%d')
        hora_str = pd.to_datetime(hora_actual).strftime('%H:%M:%S')
        
        texto_status.markdown(f"""
        ### 📅 Fecha: **{fecha_str}** ### ⏰ Hora: **{hora_str}**
        """)

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=batch,
            get_position=[COL_LON, COL_LAT],
            get_fill_color='color_rgb',
            get_radius=100, 
            pickable=True,
            opacity=0.8,
            stroked=True,
            filled=True,
            radius_min_pixels=5,
            radius_max_pixels=50,
        )

        tooltip = {
            "html": f"<b>ID:</b> {{{COL_ID}}}<br/><b>Estado:</b> {{{COL_INDICADOR}}}",
            "style": {"backgroundColor": "black", "color": "white"}
        }

        mapa_placeholder.pydeck_chart(pdk.Deck(
            api_keys={"mapbox": "pk.eyJ1IjoibHVpc3JuYXYiLCJhIjoiY21pcDlyZTgwMGI0bDNrb3ZrcnJtbmNhdSJ9.CoAnz8VfHwEaK-88Oa9MVg"},
            map_style='mapbox://styles/mapbox/dark-v10',  # Estilo oscuro
            initial_view_state=view_state,
            layers=[layer],
            tooltip=tooltip
        ))
        
        barra_progreso.progress((i + 1) / total_pasos)
        time.sleep(1) 

    st.success("Simulación finalizada.")

else:
    st.info("Presiona el botón para comenzar la animación automática.")
