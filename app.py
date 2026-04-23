import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

# 🎨 ESTILO LIMPIO OCEAN PRO
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #020617, #0c4a6e);
    color: #e2e8f0;
}

/* Quitar fondo gris feo */
iframe {
    background-color: transparent !important;
}
.element-container:has(iframe) {
    background: transparent !important;
}

/* HEADER */
h1 {
    text-align: center;
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
    max-width: 500px;
    margin: auto;
}

/* BOTONES */
button {
    border-radius: 14px !important;
    font-size: 18px !important;
}

/* TEXTO */
.label {
    margin-top: 15px;
    margin-bottom: 15px;
    color: #cbd5f5;
}
</style>
""", unsafe_allow_html=True)

# 🐋 HEADER
st.markdown("<h1>🐋 Control por Voz</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Sistema IoT con estilo océano 💙</p>", unsafe_allow_html=True)

# MQTT
def on_publish(client,userdata,result):
    print("dato publicado")

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
st.image(image, width=150)

st.markdown("<p class='label'>🎤 Presiona y habla (ON / OFF)</p>", unsafe_allow_html=True)

# 🎙️ BOTÓN VOZ PRO
stt_button = Button(label="🎙️ Hablar ahora", width=250)

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

# RESULTADO
if result:
    if "GET_TEXT" in result:
        texto = result.get("GET_TEXT").strip().upper()

        st.success(f"🧠 {texto}")

        client1.on_publish = on_publish
        client1.connect(broker,port)

        message = json.dumps({"Act1": texto})
        client1.publish("cmqtt_amotorcito", message)

st.markdown('</div>', unsafe_allow_html=True)

# Carpeta temp
try:
    os.mkdir("temp")
except:
    pass
