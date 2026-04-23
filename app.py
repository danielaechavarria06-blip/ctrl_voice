import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

# 🎨 ESTILO MINIMAL
st.markdown("""
<style>
.stApp {
    background-color: #0f172a;
    color: #e2e8f0;
}

/* Títulos */
h1, h2, h3 {
    color: #38bdf8;
}

/* Botón voz */
button {
    border-radius: 12px !important;
}

/* Caja estilo card */
.card {
    background-color: #111827;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# 🐋 HEADER SIMPLE
st.markdown("## 🎤 Control por Voz")
st.caption("Sistema IoT vía MQTT")

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

# 🧊 CARD CENTRAL
st.markdown('<div class="card">', unsafe_allow_html=True)

image = Image.open('voice_ctrl.jpg')
st.image(image, width=140)

st.write("Presiona y habla (ON / OFF)")

# BOTÓN VOZ
stt_button = Button(label="🎙️ Hablar", width=180)

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

        st.success(f"{texto}")

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
