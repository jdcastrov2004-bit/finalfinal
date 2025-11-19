import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

# =========================
# Configuración de la página
# =========================
st.set_page_config(
    page_title="Lector de Sensor MQTT",
    page_icon="📡",
    layout="wide"
)

# ====== Estilos globales (solo estética) ======
st.markdown(
    """
    <style>
    /* Fondo general */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at top left, #1f2933 0, #020617 45%, #020617 100%);
        color: #e5e7eb;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #020617 !important;
        border-right: 1px solid rgba(148,163,184,0.3);
    }

    [data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }

    /* Títulos principales */
    h1, h2, h3 {
        color: #f9fafb !important;
    }

    /* Tarjetas "glassmorphism" */
    .glass-card {
        background: rgba(15, 23, 42, 0.75);
        border-radius: 18px;
        padding: 1.5rem 1.8rem;
        border: 1px solid rgba(148, 163, 184, 0.3);
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.8);
    }

    .glass-card-soft {
        background: rgba(15, 23, 42, 0.75);
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
        border: 1px solid rgba(148, 163, 184, 0.25);
    }

    /* Botón principal */
    .stButton>button {
        width: 100%;
        border-radius: 999px;
        padding: 0.7rem 1.2rem;
        font-weight: 600;
        border: 1px solid rgba(96,165,250,0.7);
        background: linear-gradient(90deg, #2563eb, #7c3aed);
        color: #f9fafb;
        box-shadow: 0 12px 28px rgba(37, 99, 235, 0.35);
        transition: all 0.15s ease-in-out;
    }

    .stButton>button:hover {
        filter: brightness(1.07);
        transform: translateY(-1px);
        box-shadow: 0 18px 36px rgba(37, 99, 235, 0.45);
    }

    /* Métricas */
    [data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.9);
        border-radius: 16px;
        padding: 0.9rem 0.9rem;
        border: 1px solid rgba(148, 163, 184, 0.35);
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.65);
    }

    [data-testid="stMetric"] label {
        font-size: 0.85rem;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    [data-testid="stMetric"] div:nth-of-type(2) {
        font-size: 1.4rem;
        font-weight: 700;
        color: #e5e7eb;
    }

    /* Divider */
    hr {
        border: none;
        border-top: 1px solid rgba(148, 163, 184, 0.3);
    }

    /* Expander */
    [data-testid="stExpander"] {
        background: rgba(15, 23, 42, 0.85);
        border-radius: 14px;
        border: 1px solid rgba(148, 163, 184, 0.35);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ======================
# Variables de estado
# ======================
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = None

if 'last_update' not in st.session_state:
    st.session_state.last_update = None


def get_mqtt_message(broker, port, topic, client_id):
    """Función para obtener un mensaje MQTT"""
    message_received = {"received": False, "payload": None}
    
    def on_message(client, userdata, message):
        try:
            payload = json.loads(message.payload.decode())
            message_received["payload"] = payload
            message_received["received"] = True
        except:
            # Si no es JSON, guardar como texto
            message_received["payload"] = message.payload.decode()
            message_received["received"] = True
    
    try:
        client = mqtt.Client(client_id=client_id)
        client.on_message = on_message
        client.connect(broker, port, 60)
        client.subscribe(topic)
        client.loop_start()
        
        # Esperar máximo 5 segundos
        timeout = time.time() + 5
        while not message_received["received"] and time.time() < timeout:
            time.sleep(0.1)
        
        client.loop_stop()
        client.disconnect()
        
        return message_received["payload"]
    
    except Exception as e:
        return {"error": str(e)}

# ======================
# Sidebar - Configuración
# ======================
with st.sidebar:
    st.markdown("### ⚙️ Configuración de Conexión")
    st.caption("Ajusta los parámetros de tu broker MQTT para comenzar a escuchar el sensor.")

    broker = st.text_input(
        'Broker MQTT',
        value='broker.mqttdashboard.com',
        help='Dirección del broker MQTT'
    )
    
    port = st.number_input(
        'Puerto',
        value=1883,
        min_value=1,
        max_value=65535,
        help='Puerto del broker (generalmente 1883)'
    )
    
    topic = st.text_input(
        'Tópico',
        value='Sensor/THP2',
        help='Tópico MQTT al que deseas suscribirte'
    )
    
    client_id = st.text_input(
        'ID del Cliente',
        value='streamlit_client',
        help='Identificador único para este cliente'
    )

    st.markdown("---")
    st.caption("💡 Consejo: Usa brokers públicos para pruebas rápidas o tu propio broker en producción.")

# ======================
# Layout principal
# ======================

# Encabezado
col_title, col_status = st.columns([0.7, 0.3])

with col_title:
    st.markdown(
        """
        <div class="glass-card">
            <h1>📡 Lector de Sensor MQTT</h1>
            <p style="color:#9ca3af; margin-top:0.4rem;">
                Monitorea en tiempo real los datos que llegan desde tu sensor MQTT, 
                visualízalos como métricas y explora el JSON recibido.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_status:
    with st.container():
        st.markdown('<div class="glass-card-soft">', unsafe_allow_html=True)
        st.markdown("#### Estado de sesión")
        if st.session_state.last_update:
            st.success(f"Última actualización: {st.session_state.last_update}")
        else:
            st.info("Aún no se han recibido datos 📭")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("")

# Bloque de información
with st.expander('ℹ️ Cómo usar esta aplicación', expanded=False):
    st.markdown("""
    1. **Broker MQTT**: Ingresa la dirección del servidor MQTT en el sidebar.  
    2. **Puerto**: Generalmente es `1883` para conexiones no seguras.  
    3. **Tópico**: El canal al que deseas suscribirte (ej. `Sensor/THP2`).  
    4. **ID del Cliente**: Un identificador único para esta conexión.  
    5. Haz clic en **Obtener Datos del Sensor** para leer el mensaje más reciente.  
    
    **Brokers públicos para pruebas rápidas**:
    - `broker.mqttdashboard.com`
    - `test.mosquitto.org`
    - `broker.hivemq.com`
    """)

st.markdown("---")

# ======================
# Botón para obtener datos
# ======================
col_btn, col_hint = st.columns([0.4, 0.6])

with col_btn:
    if st.button('🔄 Obtener Datos del Sensor'):
        with st.spinner('Conectando al broker y esperando datos...'):
            sensor_data = get_mqtt_message(broker, int(port), topic, client_id)
            st.session_state.sensor_data = sensor_data
            st.session_state.last_update = time.strftime("%Y-%m-%d %H:%M:%S")

with col_hint:
    st.caption("Cada clic realiza una nueva conexión, escucha el tópico configurado y actualiza los datos mostrados abajo.")

# ======================
# Mostrar resultados
# ======================
if st.session_state.sensor_data:
    st.markdown("---")
    st.subheader('📊 Datos Recibidos')

    data = st.session_state.sensor_data

    # Verificar si hay error
    if isinstance(data, dict) and 'error' in data:
        st.error(f"❌ Error de conexión: {data['error']}")
    else:
        st.success('✅ Datos recibidos correctamente desde el broker')

        # Si es JSON/dict, mostrar como métricas + JSON
        if isinstance(data, dict):
            st.markdown("##### Métricas del mensaje")

            # Métricas en columnas
            num_items = len(data)
            num_cols = min(num_items, 4) if num_items > 0 else 1
            rows = (num_items // num_cols) + (1 if num_items % num_cols != 0 else 0)

            # Distribuir las métricas en filas y columnas
            items = list(data.items())
            idx = 0
            for _ in range(rows):
                cols = st.columns(num_cols)
                for c in range(num_cols):
                    if idx < num_items:
                        key, value = items[idx]
                        with cols[c]:
                            st.metric(label=key, value=value)
                        idx += 1

            st.markdown("")
            with st.expander('🧾 Ver JSON completo'):
                st.json(data)
        else:
            # Si no es diccionario, mostrar como texto plano
            st.markdown("##### Mensaje recibido (texto)")
            st.code(data)

else:
    st.markdown("")
    st.info("🛰️ Aún no hay datos para mostrar. Configura tu conexión en el panel lateral y presiona **Obtener Datos del Sensor**.")

