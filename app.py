import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

# 🎨 ESTILOS BONITOS
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #020617, #0c4a6e);
    color: #e2e8f0;
}

/* Quitar fondo feo */
iframe { background-color: transparent !important; }
.element-container:has(iframe) { background: transparent !important; }

/* HEADER */
.title {
    text-align: center;
    font-size: 40px;
    color: #e0f2fe;
    margin-bottom: 5px;
}
.subtitle {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 30px;
}

/* CARD */
.card {
    background: rgba(15, 23, 42, 0.75);
    padding: 40px;
    border-radius: 22px;
    text-align: center;
    backdrop-filter: blur(12px);
    box-shadow: 0 10px 40px rgba(0,0,0,0.6);
    max-width: 520px;
    margin: auto;
}

/* BOTÓN */
button {
    border-radius: 16px !important;
    font-size: 18px !important;
    background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
    color: white !important;
    padding: 10px;
    transition: 0.3s;
}

button:hover {
    transform: scale(1.07);
    background: linear-gradient(135deg, #2563eb, #1e40af) !important;
}

/* chips de acciones */
.chip {
    display: inline-block;
    padding: 8px 14px;
    margin: 5px;
    border-radius: 20px;
    background: rgba(59,130,246,0.2);
    color: #93c5fd;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# 🐋 HEADER
st.markdown("<div class='title'>🐋 Control por Voz</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Interfaz multimodal IoT 💙</div>", unsafe_allow_html=True)

# MQTT
def on_publish(client,userdata,result):
    print("el dato ha sido publicado")

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received=str(message.payload.decode("utf-8"))
    st.write("📩", message_received)

broker="broker.mqttdashboard.com"
port=1883
client1= paho.Client("RAYIT4")
client1.on_message = on_message

# 🧊 CARD
st.markdown('<div class="card">', unsafe_allow_html=True)

image = Image.open('voice_ctrl.jpg')
st.image(image, width=160)

st.write("🎤 Presiona el botón y habla")

# 💙 OPCIONES VISUALES (solo UI, no lógica)
st.markdown("""
<div>
<span class="chip">🚪 abrir puerta</span>
<span class="chip">🚪 cerrar puerta</span>
<span class="chip">💡 prender luz</span>
<span class="chip">💡 apagar luz</span>
</div>
""", unsafe_allow_html=True)

# BOTÓN VOZ
stt_button = Button(label="🎙️ Hablar", width=240)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# RESULTADO (MISMA LÓGICA)
if result:
    if "GET_TEXT" in result:
        texto = result.get("GET_TEXT")

        st.success(f"🧠 {texto}")

        client1.on_publish = on_publish
        client1.connect(broker,port)

        message = json.dumps({"Act1": texto.strip()})
        client1.publish("voice_Rayita", message)

st.markdown('</div>', unsafe_allow_html=True)

# carpeta temp
try:
    os.mkdir("temp")
except:
    pass
